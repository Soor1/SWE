import chainlit as cl
from typing import Dict
import asyncio
import os
import json
from typing import Set
from data_pipeline.embedding.pinecone_interface import PineconeInterface
from agent.chatbot import RAGAgent

# Environment setup for Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if PINECONE_API_KEY is None:
    raise ValueError("PINECONE_API_KEY is not set in the environment")
os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY

# Initialize interfaces
pinecone_interface = PineconeInterface()
rag_agent = RAGAgent()

# Store conversation history per user session
@cl.cache
def get_user_session() -> Dict:
    return {
        "history": [],
        "last_retrieval": None,
        "current_topic": None
    }

# Authentication callback
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if rag_agent.sign_in(username, password):
        return cl.User(
            identifier=username, metadata={"role": "admin", "provider": "credentials", "password": password}
        )
    return None

@cl.on_chat_start
async def start_chat():
    user = cl.user_session.get("user")
    if not user:
        await cl.Message(content="Authentication required. Please sign in.").send()
        return

    # Verify Pinecone connection
    try:
        is_connected = await asyncio.get_event_loop().run_in_executor(
            None, pinecone_interface.check_connection
        )
        if not is_connected:
            await cl.Message(content="Error connecting to legislation database").send()
            return
    except Exception as e:
        await cl.Message(content=f"Connection error: {str(e)}").send()
        return

    # Sign in with RAGAgent
    res = rag_agent.sign_in(user.identifier, user.metadata["password"])
    if not res:
        await cl.Message(content="Error signing in. Please try again.").send()
        return

    # Retrieve last message
    retrieved_message = rag_agent.retrieve_last_message(user.identifier)
    await cl.Message(
        content=f"Welcome to the Legislation Chatbot! Ask me anything about legislation. Here is your last message:\n{retrieved_message}"
    ).send()

def process_message(message: str, session: Dict, user_id: str) -> tuple[str, list]:
    # Perform RAGAgent retrieval
    raw_retrieval = rag_agent.retrieve_similar_question(message)
    clean_retrieval = []
    for chunk in raw_retrieval:
        clean_retrieval.append(chunk["metadata"]["title"] + "\n" + chunk["metadata"]["chunk"])

    links = set([chunk["metadata"]["full_text_link"] for chunk in raw_retrieval])
    # Generate prompt for LLM
    prompt = f"""You are a helpful assistant that answers questions based on the context provided.
    
Context:
{"\n\n".join(clean_retrieval)}
    
Question: 
{message}
    
Answer:
""" 
    print(prompt)
    return prompt, list(links)
    # Format response with references
def format_response(message, llm_response: str, links: Set, user_id: str) -> str:
    formatted_response = f"""
References:
{"\n".join(list(links))}
""" if links else None

    # Store message pair
    message_pair = f"""
question: {message}
answer: {llm_response}
"""
    rag_agent.store_last_message(user_id, message_pair)

    return formatted_response


def format_legislation_response(data: dict) -> str:
    """Structure the Pinecone response into readable format"""
    return f"""**{data.get('title', 'Untitled Legislation')}**

Introduced: {data.get('introduced_date', 'Date unknown')}
Summary: {data.get('summary', 'No summary available')}

Ask follow-up questions about implementation, purpose, or timelines."""

@cl.on_message
async def main(message: cl.Message):
    session = get_user_session()
    user = cl.user_session.get("user")
    if not user:
        await cl.Message(content="Please sign in to continue.").send()
        return
    
    msg = cl.Message(content="")

    prompt, links = process_message(message.content, session, user.identifier)
    for resp in rag_agent.chatbot.chat(
        prompt,
        stream=True
    ):  
        if resp:
            await msg.stream_token(resp["token"])


    await msg.update()
    tag = "\n" + format_response(message.content, msg.content, links, user.identifier)
    if tag:
        await msg.stream_token(tag)
        await msg.update()
