import chainlit as cl # https://docs.chainlit.io/get-started/pure-python 

"""
    Main entry point for the application.
"""

@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...

    # Send a response back to the user
    await cl.Message(
        content=f"Received: {message.content}",
    ).send()