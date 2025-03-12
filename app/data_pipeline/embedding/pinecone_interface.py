from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

from datetime import datetime
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import traceback

from scipy.spatial.distance import cosine



class PineconeInterface:
    def __init__(self, hf_embedding_model_name: str = "all-mpnet-base-v2"):
        load_dotenv()

        self.model = SentenceTransformer(hf_embedding_model_name)
        self.pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        # self.pc = Pinecone(api_key="error_key")
        assert self.check_connection()


    def check_connection(self) -> bool:
        try:
            indexes = self.pc.list_indexes()
            if indexes:
                # print(f"Pinecone is live! Available indexes: {indexes}")
                return True
            else:
                # print("Pinecone is live, but no indexes found.")
                return True
        except Exception as e:
            print(f"Error connecting to Pinecone: {e}")
            return False

    def store(self, 
              input_data: List[Dict],
              index_name: str = "legislation-chat", 
              key_to_be_embedded: Optional[str] = None,
        ) -> Dict[str, str]:

        assert self.check_connection()

        try:
            texts = [data[key_to_be_embedded] for data in input_data]            
            embeddings = self.model.encode(texts)

            if not self.pc.has_index(index_name):
                self.pc.create_index(
                    name=index_name,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    ) 
                )
            
            index = self.pc.Index(index_name)

            namespace = input_data[0]["update_date"]
            today = datetime.now().strftime("%Y-%m-%d")

            if namespace == today:
                print(f"The update_date {namespace} matches today's date.")
            else:
                print(f"The update_date {namespace} does NOT match today's date. Today's date is {today}.")
                return {"status": "update_date does not match today's date."}
            
            vectors = [
                {
                    "id": str(i),
                    "values": embeddings[i].tolist(),
                    "metadata": input_data[i]
                }
                for i in range(len(input_data))
            ]
            upsert_response = index.upsert(vectors, namespace=namespace).to_dict()
            return upsert_response

        except Exception as e:
            print("An error occurred in PineconeInterface.store:")
            traceback.print_exc()
            return {"status": f"an error occurred {e}"}

    def retrieve(self, 
                  query: str, 
                  index_name: str = "legislation-chat", 
                  limit: int = 3, 
                  closeness_threshold: Optional[float] = 1,
                  namespace: str = datetime.now().strftime("%Y-%m-%d")
        ) -> Optional[List[Dict]]:
        try:
            assert self.check_connection()
            assert self.pc.has_index(index_name)
            assert namespace == datetime.now().strftime("%Y-%m-%d")

            index = self.pc.Index(index_name)
            query_embedding = self.model.encode(query).tolist()
            results = index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True,
                namespace=namespace
                )

            final_results = []
            if results and "matches" in results:
                for match in results["matches"]:
                    if match["score"] < closeness_threshold:
                        final_results.append(match)
            
            return final_results
                
        except Exception as e:
            print("An error occurred in PineconeInterface.retrieve:")
            traceback.print_exc()

   
        
    
    
    

    

