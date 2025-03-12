import chainlit as cl # https://docs.chainlit.io/get-started/pure-python 


from agent.chatbot import RAGAgent
"""
    Main entry point for the application.
"""

ragAgent = RAGAgent()

@cl.on_message
async def main(message: cl.Message):
    response = ragAgent.chatbot.chat(message.content).wait_until_done()

    await cl.Message(
        content=response,
    ).send()