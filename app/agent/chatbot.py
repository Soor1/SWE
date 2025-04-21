from hugchat import hugchat
from hugchat.login import Login

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import os
from dotenv import load_dotenv

from data_pipeline.embedding.pinecone_interface import PineconeInterface


# Reference: https://github.com/Soulter/hugging-chat-api
# Create account on https://huggingface.co/
# Login https://huggingface.co/chat/


class RAGAgent:
    def __init__(self):
        """Initialize the RAGAgent class, hugchat client, and load environment variables."""
        self.chatbot = None

        self.pinecone_interface = PineconeInterface()
        assert self.pinecone_interface.check_connection()

        uri = f"mongodb+srv://josephmolina:{os.environ.get('MONGO_PASSWORD')}@legislationchat.3brsn.mongodb.net/?appName=LegislationChat"
        self.mongo_client = MongoClient(uri, server_api=ServerApi('1'))
        res = self.mongo_client.admin.command('ping')
        assert res.get("ok", 0) == 1
        self.sign_in(os.environ.get("HUGGINGFACE_EMAIL"), os.environ.get("HUGGINGFACE_PASSWORD"))

    def sign_in(self, email, password):
        """Sign in with the provided username and password."""
        if self.chatbot is not None and self.email == email and self.password == password:
            return True
        try:
            self.email = email
            self.password = password
            cookie_path_dir = "./cookies/"
            sign = Login(email, password)
            cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
            self.chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
            return True
        except Exception as e:
            print(f"Error signing in: {e}")
            self.chatbot = None
            return False
        

    def retrieve_similar_question(self, user_query):
        """Finds the most similar question from the stored Q&A pairs and returns the embedding vector value, question, and answer.
        Focus on this in Sprint 1.
        """
        raw_retrieval_result = self.pinecone_interface.retrieve(query=user_query)

        return raw_retrieval_result
    
    def store_last_message(self, email, message):
        """Stores the last message in the database."""
        db = self.mongo_client["LegislationChat"]  # Database name
        collection = db["messages"]  # Collection name
        collection.update_one(
            {"email": email},
            {"$set": {"last_message": message}},
            upsert=True  # Ensures only one document per user email
        )
    def retrieve_last_message(self, email):
        """Retrieves the last message from the database."""
        db = self.mongo_client["LegislationChat"]
        collection = db["messages"]  # Collection name
        res = collection.find_one({"email": email})
        return str(res["last_message"]).strip() if res else None
