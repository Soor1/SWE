from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os


load_dotenv()
uri = f"mongodb+srv://josephmolina:{os.environ.get("MONGO_PASSWORD")}@legislationchat.3brsn.mongodb.net/?appName=LegislationChat"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    res = client.admin.command('ping')
    print(res)
except Exception as e:
        print(e)
