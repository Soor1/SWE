import chainlit as cl
from typing import Dict
import asyncio
from data_pipeline.embedding.pinecone_interface import PineconeInterface
import os

# Use the environment variable
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if PINECONE_API_KEY is None:
    raise ValueError("PINECONE_API_KEY is not set in the environment")

os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY


# Initialize Pinecone interface
pinecone_interface = PineconeInterface()

# Store conversation history per user session
@cl.cache
def get_user_session() -> Dict:
    return {
        "history": [],
        "last_retrieval": None,
        "current_topic": None
    }

@cl.on_chat_start
async def start():
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

    # Welcome message
    await cl.Message(
        content="Welcome to Legislation Chat! I can read recent bills and explain their provisions. What would you like to know?"
    ).send()

async def process_message(message: str, session: Dict) -> str:
    msg_lower = message.lower().strip()
    session["history"].append({"role": "user", "content": message})

    # Handle follow-up questions
    if session["last_retrieval"] and any(keyword in msg_lower for keyword in ["when", "why", "how", "explain", "what"]):
        return handle_followup(msg_lower, session["last_retrieval"])
        
    # New query - perform vector search
    try:
        retrieval_result = await asyncio.get_event_loop().run_in_executor(
            None, pinecone_interface.retrieve, message
        )
    except Exception as e:
        return f"Search error: {str(e)}"

    if not retrieval_result:
        return "No relevant legislation found. Try different keywords or a more specific query."
    
    # Store context for follow-up questions
    session["last_retrieval"] = retrieval_result
    session["current_topic"] = message
    
    return format_legislation_response(retrieval_result)

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
    response = await process_message(message.content, session)
    session["history"].append({"role": "assistant", "content": response})
    
    await cl.Message(
        content=response,
        elements=[cl.Text(name="full_text", content=session["last_retrieval"]["full_text"], display="hidden")] 
        if session["last_retrieval"] else []
    ).send()
