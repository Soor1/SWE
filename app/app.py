import chainlit as cl # https://docs.chainlit.io/get-started/pure-python 
import json

from agent.chatbot import RAGAgent

"""
    Main entry point for the application.
"""
rag_agent = RAGAgent()


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if rag_agent.sign_in(username, password):
        return cl.User(
            identifier=username, metadata={"role": "admin", "provider": "credentials", "password": password}
        )
    else:
        return None
    
@cl.on_chat_start
async def start_chat():
    user = cl.user_session.get("user")
    print(user.identifier, user.metadata["password"])
    res = rag_agent.sign_in(user.identifier, user.metadata["password"])
    if not res:
        await cl.Message(
            content="Error signing in. Please try again.",
        ).send()
    else:
        retrieved_message = rag_agent.retrieve_last_message(user.identifier)
        await cl.Message(
            content="Welcome to the Legislation Chatbot! Ask me anything about legislation. Here is your last message:\n" + retrieved_message,
        ).send()
    
@cl.on_message
async def main(message: cl.Message):
    raw_retrieval = rag_agent.retrieve_similar_question(message.content)
    await cl.Message(
        content=raw_retrieval,
    ).send()

    clean_retrieval = []
    for chunk in raw_retrieval:
        clean_retrieval.append(chunk["metadata"]["title"] + "\n" + chunk["metadata"]["chunk"])
    
    prompt = f"""You are a helpful assistant that answers questions based on the context provided.
    
Context:
{"\n\n".join(clean_retrieval)}
    
Question: 
{message.content}
    
Answer:
"""


    llm_response = rag_agent.chatbot.chat(prompt).wait_until_done()
    formatted_response = f"""
    {llm_response}
    references:
    {"\n".join([chunk["metadata"]["full_text_link"] for chunk in raw_retrieval])}
    """

    message_pair = f"""
    question: {message.content}
    answer: {llm_response}
    """
    print(message.author)
    rag_agent.store_last_message(message.author, message_pair)

    await cl.Message(
        content=formatted_response,
    ).send()

