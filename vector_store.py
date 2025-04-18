# Ajout dans un nouveau fichier: vector_store.py
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, PyPDFLoader, CSVLoader

class VectorStore:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_db = Chroma(persist_directory=persist_directory, 
                               embedding_function=self.embeddings)
        
    def add_documents(self, documents_path, doc_type="text"):
        """Ajoute des documents à la base vectorielle"""
        if doc_type == "text":
            loader = TextLoader(documents_path)
        elif doc_type == "pdf":
            loader = PyPDFLoader(documents_path)
        elif doc_type == "csv":
            loader = CSVLoader(documents_path)
        
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        
        self.vector_db.add_documents(texts)
        self.vector_db.persist()
        
    def query(self, query_text, n_results=5):
        """Recherche les documents les plus pertinents pour une requête"""
        results = self.vector_db.similarity_search(query_text, k=n_results)
        return results