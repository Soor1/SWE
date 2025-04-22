from hugchat import hugchat
from hugchat.login import Login
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from data_pipeline.embedding.pinecone_interface import PineconeInterface




# Reference: https://github.com/Soulter/hugging-chat-api
# Create account on https://huggingface.co/
# Login https://huggingface.co/chat/

import os
from dotenv import load_dotenv

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

    def retrieve_similar_question(self, user_query):
        """Finds the most similar question from the stored Q&A pairs and returns the embedding vector value, question, and answer.
        Focus on this in Sprint 1.
        """
        ...
