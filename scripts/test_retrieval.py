from app.data_pipeline.embedding.pinecone_interface import PineconeInterface

pincone_inteface = PineconeInterface()
assert pincone_inteface.check_connection()

query_string = input("Enter a query string: ")

retrieval_result = pincone_inteface.retrieve(query=query_string)
print(retrieval_result)

""""
You are a legislation chatbot. 
Answer the following question based on the retrieved information. 
Question: (query_string) Retrieved data{: retrieval_result)
"""