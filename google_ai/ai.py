from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter

loader = PyPDFLoader("documentos/documento_ai.pdf")
documents = loader.load()

load_dotenv()

google_api_key = os.getenv('GOOGLE_API_KEY')

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.from_documents(texts, embedding_model)


class AIGoogle:
    def __init__(self, prompt_user, response, k=4):
        self.prompt_user = prompt_user
        self.response = response
        self.db = db
        self.k = k
        self.google_ai_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    def interaction(self):
        docs = self.db.similarity_search(self.prompt_user, k=self.k)

        context = "\n\n".join([d.page_content for d in docs])

        messages = [
            ("system", f"{self.prompt_user}\n\nContexto relevante:\n{context}"),
            ("human", self.response),
        ]

        return self.google_ai_llm.invoke(messages)
