from hugchat import hugchat
from hugchat.login import Login


# Reference: https://github.com/Soulter/hugging-chat-api
# Create account on https://huggingface.co/
# Login https://huggingface.co/chat/

class RAGAgent:
    def __init__(self):
        """Initialize the RAGAgent class, hugchat client, and load environment variables."""
        ...

    def retrieve_similar_question(self, user_query):
        """Finds the most similar question from the stored Q&A pairs and returns the embedding vector value, question, and answer.
        Focus on this in Sprint 1.
        """
        ...
