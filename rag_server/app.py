import os
import asyncio
from flask import Flask, request, jsonify

# --- IMPORTS NÉCESSAIRES (validés dans Jupyter) ---
import faiss
from langchain_community.docstore import InMemoryDocstore
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

from langchain.retrievers import ContextualCompressionRetriever, ParentDocumentRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.storage import InMemoryStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate

# --- CONFIGURATION (Le travail lourd fait au démarrage) ---
print("🚀 Initialisation du serveur RAG Ultime...")

# Récupération de la clé API
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("La clé API OpenAI n'est pas définie. Veuillez la définir dans docker-compose.yaml.")

# 1. Chargement du document
# Assurez-vous que ce document est copié dans votre Dockerfile ou monté via un volume
document_path = "./document.pdf"
if not os.path.exists(document_path):
    raise FileNotFoundError(f"Le document {document_path} est introuvable dans le conteneur.")
loader = PyPDFLoader(document_path)
docs = loader.load()
print(f"📄 Document '{document_path}' chargé.")

# 2. Découpage Parent/Enfant
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)

# 3. Initialisation des composants de stockage (avec le correctif)
embeddings = OpenAIEmbeddings(openai_api_key=api_key, model="text-embedding-3-small")
embedding_dimension = 1536
index = faiss.IndexFlatL2(embedding_dimension)
faiss_docstore = InMemoryDocstore({})
vectorstore = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=faiss_docstore,
    index_to_docstore_id={}
)
store = InMemoryStore() # Pour les documents parents

# 4. Assemblage des 3 niveaux d'amélioration
# NIVEAU 1: Parent Document Retriever
parent_document_retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)
parent_document_retriever.add_documents(docs, ids=None)
print("Niveau 1 (Parent Document Retriever) configuré.")

# NIVEAU 2: Re-Ranking (avec le correctif)
cross_encoder_model = HuggingFaceCrossEncoder(model_name='cross-encoder/ms-marco-MiniLM-L-6-v2')
compressor = CrossEncoderReranker(model=cross_encoder_model, top_n=3)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=parent_document_retriever
)
print("Niveau 2 (Re-Ranker) configuré.")

# NIVEAU 3: Expansion de Requête
llm = ChatOpenAI(openai_api_key=api_key, model="gpt-4o-mini", temperature=0)
multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=compression_retriever,
    llm=llm
)
print("Niveau 3 (Multi-Query Retriever) configuré.")

# 5. Création de la chaîne RAG finale
prompt_template = ChatPromptTemplate.from_template("""En te basant UNIQUEMENT sur le contexte riche et élargi suivant, réponds de manière détaillée et structurée à la question. Si l'information n'est pas dans le contexte, dis clairement "L'information n'est pas disponible dans le document".

Contexte:
{context}

Question: {input}
""")
combine_docs_chain = create_stuff_documents_chain(llm, prompt_template)
rag_chain = create_retrieval_chain(multi_query_retriever, combine_docs_chain)

print("\n✅ Serveur RAG Ultime prêt ! ---")


# --- API FLASK ---
app = Flask(__name__)

@app.route('/ask_rag', methods=['POST'])
def ask_rag():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "La requête doit être en JSON et contenir une 'question'."}), 400

    user_question = data['question']
    print(f"Question reçue par le serveur RAG: '{user_question}'")

    try:
        # LangChain utilise de plus en plus l'asynchrone.
        # Pour appeler une fonction 'async' depuis une fonction 'sync' comme celle-ci,
        # nous utilisons asyncio.run()
        response = asyncio.run(rag_chain.ainvoke({"input": user_question}))
        answer = response.get("answer", "Aucune réponse générée.")
        return jsonify({"answer": answer})
    except Exception as e:
        print(f"❌ Erreur lors de l'invocation de la chaîne RAG : {e}")
        return jsonify({"error": "Une erreur interne est survenue dans le serveur RAG."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
