from hugchat import hugchat
from hugchat.login import Login
import os
from dotenv import load_dotenv


# Reference: https://github.com/Soulter/hugging-chat-api
# Create account on https://huggingface.co/
# Login https://huggingface.co/chat/

import os
from dotenv import load_dotenv

class RAGAgent:
    def __init__(self):
        """Initialize the RAGAgent class, hugchat client, and load environment variables."""
        load_dotenv()
        email = os.getenv("EMAIL")
        password = os.getenv("PASSWD")
        cookie_path_dir = "./cookies/"
        sign = Login(email, password)
        cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
        self.chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

    def retrieve_similar_question(self, user_query):
        """Finds the most similar question from the stored Q&A pairs and returns the embedding vector value, question, and answer.
        Focus on this in Sprint 1.
        """
        ...
