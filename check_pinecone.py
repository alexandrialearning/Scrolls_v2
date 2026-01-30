
import os
from pinecone import Pinecone
from dotenv import load_dotenv

# Force reload of .env
load_dotenv(override=True)

api_key = os.getenv("PINECONE_API_KEY")
print(f"API Key found: '{api_key}' (Length: {len(api_key) if api_key else 0})")

try:
    pc = Pinecone(api_key=api_key)
    print("Connecting to Pinecone...")
    indexes = pc.list_indexes()
    print(f"Success! Indexes found: {[i.name for i in indexes]}")
except Exception as e:
    print(f"Connection failed: {e}")
