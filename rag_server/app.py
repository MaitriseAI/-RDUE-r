import os
import asyncio
from flask import Flask, request, jsonify

# Imports LangChain
import faiss
from langchain_community.docstore import InMemoryDocstore
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers import ContextualCompressionRetriever, ParentDocumentRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.storage import InMemoryStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader # <-- NOUVEL IMPORT
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain, create_history_aware_retriever # <-- NOUVEL IMPORT
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder # <-- NOUVEL IMPORT

# --- CONFIGURATION FAITE AU DÉMARRAGE DU SERVEUR ---
print("🚀 Initialisation du serveur RAG d'Entreprise...")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Clé API OpenAI non trouvée.")

# 1. Chargement de TOUS les documents d'un dossier
# Nous allons maintenant charger tous les PDF qui se trouvent dans le sous-dossier 'documents'
documents_path = "./documents/"
if not os.path.exists(documents_path):
    os.makedirs(documents_path)
    raise FileNotFoundError(f"Le dossier '{documents_path}' a été créé mais est vide. Veuillez y ajouter vos documents PDF.")

print(f"📂 Chargement des documents depuis : {documents_path}")
loader = DirectoryLoader(documents_path, glob="**/*.pdf", loader_cls=PyPDFLoader, show_progress=True)
docs = loader.load()
if not docs:
    raise ValueError(f"Aucun document PDF trouvé dans le dossier '{documents_path}'.")
print(f"✅ {len(docs)} pages de documents chargées.")


# Les étapes 2, 3 et 4 (Splitters, Stockage, Retriever avancé) restent identiques à notre RAG ultime
# ... (le code est le même que précédemment)
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)
embeddings = OpenAIEmbeddings(openai_api_key=api_key, model="text-embedding-3-small")
embedding_dimension = 1536
index = faiss.IndexFlatL2(embedding_dimension)
faiss_docstore = InMemoryDocstore({})
vectorstore = FAISS(
    embedding_function=embeddings, index=index, docstore=faiss_docstore, index_to_docstore_id={}
)
store = InMemoryStore()
parent_document_retriever = ParentDocumentRetriever(
    vectorstore=vectorstore, docstore=store, child_splitter=child_splitter, parent_splitter=parent_splitter
)
parent_document_retriever.add_documents(docs, ids=None)
print("Niveau 1 (Parent Document Retriever) configuré.")
cross_encoder_model = HuggingFaceCrossEncoder(model_name='cross-encoder/ms-marco-MiniLM-L-6-v2')
compressor = CrossEncoderReranker(model=cross_encoder_model, top_n=3)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=parent_document_retriever
)
print("Niveau 2 (Re-Ranker) configuré.")
llm = ChatOpenAI(openai_api_key=api_key, model="gpt-4o-mini", temperature=0)
multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=compression_retriever, llm=llm
)
print("Niveau 3 (Multi-Query Retriever) configuré.")


# 5. Création de la chaîne RAG finale AVEC CITATION DES SOURCES
# Nouveau prompt qui demande explicitement de citer les sources
prompt_template = ChatPromptTemplate.from_template("""Tu es un assistant expert qui répond aux questions en se basant sur un contexte fourni. Sois aussi détaillé que possible. Pour chaque information que tu utilises, tu DOIS citer tes sources.

INSTRUCTIONS DE CITATION :
- Après chaque phrase ou affirmation basée sur un document, ajoute une citation sous la forme : ``.
- Le nom du fichier et le numéro de page sont fournis dans les métadonnées de chaque document du contexte.

CONTEXTE FOURNI :
{context}

QUESTION :
{input}

RÉPONSE DÉTAILLÉE AVEC CITATIONS :""")

# La chaîne qui combine les documents et le prompt reste la même
combine_docs_chain = create_stuff_documents_chain(llm, prompt_template)

# La chaîne finale reste la même structure
rag_chain = create_retrieval_chain(multi_query_retriever, combine_docs_chain)

print("\n✅ Serveur RAG d'Entreprise prêt ! ---")

# --- API FLASK ---
app = Flask(__name__)

# Cette fonction va formater le contexte pour le rendre lisible par le LLM, avec les métadonnées
def format_docs_with_sources(docs):
    formatted_docs = []
    for i, doc in enumerate(docs):
        # On crée une chaîne de caractères qui inclut le contenu et les métadonnées
        source_info = f"Source : {os.path.basename(doc.metadata.get('source', 'N/A'))} - Page {doc.metadata.get('page', 'N/A') + 1}"
        formatted_doc = f"--- Document {i+1} ---\n{source_info}\n\n{doc.page_content}"
        formatted_docs.append(formatted_doc)
    return "\n\n".join(formatted_docs)


@app.route('/ask_rag', methods=['POST'])
def ask_rag():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "La requête doit être en JSON et contenir une 'question'."}), 400
    
    user_question = data['question']
    print(f"Question reçue : '{user_question}'")
    
    try:
        # On invoque la chaîne pour obtenir le contexte ET la réponse
        response = asyncio.run(rag_chain.ainvoke({"input": user_question}))
        
        # On formate le contexte pour l'inclure dans la réponse finale si on veut le voir
        # Mais ici, la réponse du LLM devrait déjà contenir les citations
        answer = response.get("answer", "Aucune réponse générée.")
        
        # On peut aussi renvoyer les sources brutes pour que l'UI les affiche joliment
        source_documents = []
        for doc in response.get("context", []):
            source_documents.append({
                "source": os.path.basename(doc.metadata.get("source", "N/A")),
                "page": doc.metadata.get("page", 'N/A') + 1
            })

        return jsonify({
            "answer": answer,
            "sources": source_documents
        })
        
    except Exception as e:
        print(f"❌ Erreur lors de l'invocation de la chaîne RAG : {e}")
        return jsonify({"error": f"Une erreur interne est survenue dans le serveur RAG: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
