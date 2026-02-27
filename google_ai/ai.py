from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
import streamlit as st

def carregar_base():
    load_dotenv()
    loader = PyPDFLoader("documentos/documento_ai.pdf")
    documents = loader.load()
    texts = CharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    ).split_documents(documents)
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return FAISS.from_documents(texts, embedding_model)

db = carregar_base()


class AIGoogle:
    def __init__(self, prompt_user, response, k=4):
        self.prompt_user = prompt_user
        self.response = response
        self.db = db
        self.k = k
        self.google_ai_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    def interaction(self):
        docs = self.db.similarity_search(self.prompt_user, k=self.k)

        context = "\n\n".join([d.page_content for d in docs])

        messages = [
            ("system", f"{self.prompt_user}\n\nContexto relevante:\n{context}"),
            ("human", self.response),
        ]

        return self.google_ai_llm.invoke(messages)
