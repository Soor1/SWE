import json
import os

from typing import Literal, Union

from ingestion.data_retrieval import load_chunked_data_to_json
from embedding.pinecone_interface import PineconeInterface


def load_data(
        data_path: Union[
            Literal["data/complete_data.json"], 
            Literal["data/tagged_chunks.json"], 
            Literal["data/chunked_data.json"]
            ]):
    try:
        print("loading chunked data...")
        if not os.path.exists(data_path):
            print("Chunked data not found, loading from API")
            load_chunked_data_to_json()
        with open(data_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading chunked data: {e}")
        data = []
    return data
 
def tag_chunks(complete_data):
    tagged_chunks = []
    for bill in complete_data:
        if bill.get("chunked_text", "No XML available") == "No XML available":
            continue
        chunks = bill.pop("chunked_text")
        bill.pop("full_text")
        for chunk in chunks:
            tagged_chunks.append(
                {
                    **bill,
                    "chunk": chunk
                }
            )
    with open("data/tagged_chunks.json", "w") as f:
        json.dump(tagged_chunks, f, indent=4)
    return tagged_chunks


pincone_inteface = PineconeInterface()
assert pincone_inteface.check_connection()

chunked_data = load_data(data_path="data/chunked_data.json")
assert len(chunked_data) != 0 

tagged_chunks = tag_chunks(chunked_data)
tagged_chunks = load_data(data_path="data/tagged_chunks.json")
assert len(tagged_chunks) != 0


print("Storing data in Pinecone...")
status = pincone_inteface.store(tagged_chunks, key_to_be_embedded="chunk")
print(status)
assert "error" not in status