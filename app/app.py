import chainlit as cl
from typing import Dict
import asyncio
import os
import json
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

async def process_message(message: str, session: Dict, user_id: str) -> tuple[str, list]:
    msg_lower = message.lower().strip()
    session["history"].append({"role": "user", "content": message})

    # Handle follow-up questions using stored Pinecone context
    if session["last_retrieval"] and any(keyword in msg_lower for keyword in ["when", "why", "how", "explain", "what"]):
        response = handle_followup(msg_lower, session["last_retrieval"])
        return response, []

    # Perform RAGAgent retrieval
    raw_retrieval = rag_agent.retrieve_similar_question(message)
    clean_retrieval = []
    for chunk in raw_retrieval:
        clean_retrieval.append(chunk["metadata"]["title"] + "\n" + chunk["metadata"]["chunk"])

    # Generate prompt for LLM
    prompt = f"""You are a helpful assistant that answers questions based on the context provided.
    
Context:
{"\n\n".join(clean_retrieval)}
    
Question: 
{message}
    
Answer:
"""
    llm_response = rag_agent.chatbot.chat(prompt).wait_until_done()

    # Format response with references
    formatted_response = f"""
{llm_response}
References:
{"\n".join([chunk["metadata"]["full_text_link"] for chunk in raw_retrieval])}
"""

    # Store message pair
    message_pair = f"""
question: {message}
answer: {llm_response}
"""
    rag_agent.store_last_message(user_id, message_pair)

    # Perform Pinecone vector search for additional context
    try:
        pinecone_result = await asyncio.get_event_loop().run_in_executor(
            None, pinecone_interface.retrieve, message
        )
        if pinecone_result:
            session["last_retrieval"] = pinecone_result
            session["current_topic"] = message
            formatted_response += f"\n\nAdditional Context:\n{format_legislation_response(pinecone_result)}"
    except Exception as e:
        formatted_response += f"\n\nSearch error: {str(e)}"

    elements = [cl.Text(name="full_text", content=session["last_retrieval"]["full_text"], display="hidden")] if session["last_retrieval"] else []
    return formatted_response, elements

def handle_followup(query: str, context: dict) -> str:
    """Process follow-up questions using stored context"""
    if "when" in query:
        return f"This legislation was introduced on {context.get('introduced_date', 'an unspecified date')}"
    elif "why" in query:
        return f"The primary purpose is: {context.get('purpose', 'not specified in the document')}"
    elif "how" in query:
        return f"Implementation plan: {context.get('implementation', 'details not available')}"
    return f"More details: {context.get('summary', 'No additional information available')}"

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

    response, elements = await process_message(message.content, session, user.identifier)
    session["history"].append({"role": "assistant", "content": response})

    await cl.Message(
        content=response,
        elements=elements
    ).send()