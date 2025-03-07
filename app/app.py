import chainlit as cl
from typing import Dict, List
import datetime

# Store conversation history per user session
@cl.cache
def get_user_session() -> Dict:
    return {
        "history": [],
        "last_legislation": None,
        "summaries": {}  # Could store pre-fetched legislation summaries
    }

# Mock function to simulate legislation summarization
async def get_legislation_summary(topic: str) -> str:
    # In a real implementation, this would query the Congress.gov API
    mock_summaries = {
        "healthcare": "The Healthcare Reform Act of 2025, passed on Feb 15, 2025, expands coverage for pre-existing conditions and increases funding for rural hospitals by 20%.",
        "education": "The Education Equity Act of 2025, passed on Feb 20, 2025, provides free community college for qualifying students and increases teacher salaries by 15%.",
    }
    return mock_summaries.get(topic.lower(), "No recent legislation found on this topic.")

# Process message and determine response
async def process_message(message: str, session: Dict) -> str:
    msg_lower = message.lower().strip()
    session["history"].append({"role": "user", "content": message})
    
    # Initial request for legislation summary
    if any(keyword in msg_lower for keyword in ["summarize", "summary", "what's new", "recent"]):
        # Extract topic from message 
        topic = msg_lower.split("about")[-1].strip() if "about" in msg_lower else "general"
        summary = await get_legislation_summary(topic)
        session["last_legislation"] = {"topic": topic, "summary": summary}
        return f"Here's a summary of recent legislation:\n{summary}\n\nFeel free to ask follow-up questions!"
    
    # Follow-up questions
    elif session["last_legislation"] and any(keyword in msg_lower for keyword in ["when", "why", "how", "what", "who"]):
        last_topic = session["last_legislation"]["topic"]
        if "when" in msg_lower:
            return f"The legislation about {last_topic} was passed around {datetime.datetime.now().strftime('%B %d, %Y')} (placeholder date)."
        elif "why" in msg_lower:
            return f"The legislation on {last_topic} aims to address key issues in the sector (example response)."
        elif "how" in msg_lower:
            return f"It works by implementing new policies and funding (example response)."
        else:
            return f"Regarding {last_topic}: Could you please clarify your question?"
    
    # Default response
    return "I'm here to help with recent legislation summaries. You can ask me to summarize recent laws or ask follow-up questions about them. What would you like to know?"

@cl.on_message
async def main(message: cl.Message):
    # Get or create user session
    session = get_user_session()
    
    # Process the message and get response
    response = await process_message(message.content, session)
    
    # Add assistant response to history
    session["history"].append({"role": "assistant", "content": response})
    
    # Send response back to user
    await cl.Message(
        content=response
    ).send()

@cl.on_chat_start
async def start():
    # Welcome message when chat begins
    await cl.Message(
        content="Welcome! I'm here to summarize recently passed legislation and answer your questions about it. What would you like to know?"
    ).send()