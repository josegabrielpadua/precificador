from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

google_api_key = os.getenv('GOOGLE_API_KEY')


class AIGoogle:
    def __init__(self, prompt_user, response):
        self.prompt_user = prompt_user
        self.response = response
        self.google_ai_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")


    def interaction(self):

        messages = [
            ("system", f"{self.prompt_user}"),
            ("human", f"{self.response}"),
        ]

        return self.google_ai_llm.invoke(messages)
        
