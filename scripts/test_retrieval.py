from app.data_pipeline.embedding.pinecone_interface import PineconeInterface

pinecone_interface = PineconeInterface()
assert pinecone_interface.check_connection()

query_string = input("Enter a query string: ")

retrieval_result = pinecone_interface.retrieve(query=query_string)
print(retrieval_result)