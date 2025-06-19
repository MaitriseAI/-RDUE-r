import os
from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate

# --- CONFIGURATION ---
# On fait le travail lourd UNE SEULE FOIS, au démarrage du serveur.
print("Initialisation du serveur RAG...")

# Récupération de la clé API depuis les variables d'environnement
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("La clé API OpenAI n'est pas définie. Veuillez la définir dans docker-compose.yaml.")

# Chargement du document
document_path = "./zola-14.pdf"
if not os.path.exists(document_path):
    raise FileNotFoundError(f"Le document {document_path} est introuvable.")

loader = PyPDFLoader(document_path)
documents = loader.load()

# Découpage et création des embeddings (via API OpenAI)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
split_docs = text_splitter.split_documents(documents)
embeddings = OpenAIEmbeddings(openai_api_key=api_key, model="text-embedding-3-small")

# Création de la base de données vectorielle locale
vector_store = FAISS.from_documents(split_docs, embeddings)
retriever = vector_store.as_retriever()

# Définition du modèle et du prompt
llm = ChatOpenAI(openai_api_key=api_key, model="gpt-4o")
prompt_template = ChatPromptTemplate.from_template("""En te basant UNIQUEMENT sur le contexte suivant, réponds à la question.
Contexte:{context}
Question: {input}
""")
# Création de la chaîne RAG finale
combine_docs_chain = create_stuff_documents_chain(llm, prompt_template)
rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

print("--- Serveur RAG prêt ! ---")


# --- API FLASK ---
# On crée l'application web qui va recevoir les requêtes
app = Flask(__name__)

# On définit une route pour les questions, qui n'accepte que les requêtes POST
@app.route('/ask_rag', methods=['POST'])
def ask_rag():
    # On récupère les données JSON envoyées par le client (notre pipeline)
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "La requête doit être en JSON et contenir une 'question'."}), 400

    user_question = data['question']
    print(f"Question reçue par le serveur RAG: '{user_question}'")

    # On utilise notre chaîne RAG pré-configurée pour obtenir la réponse
    response = rag_chain.invoke({"input": user_question})
    answer = response.get("answer", "Aucune réponse générée.")

    # On renvoie la réponse au format JSON
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)