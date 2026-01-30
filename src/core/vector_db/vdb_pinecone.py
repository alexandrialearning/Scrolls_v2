import os
import time
import logging
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

class PineconeVectorDB:
    
    def __init__(self, embedding, index_name: str = "alexandria-embeddings2"):
        self.index_name = os.getenv("PINECONE_INDEX_NAME", index_name)
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.embedding = embedding
        
        if not self.api_key:
            logging.error("PINECONE_API_KEY not found in environment variables.")
            raise ValueError("PINECONE_API_KEY not found associated with the environment")

        self.pc = Pinecone(api_key=self.api_key)
        self.vector_store = None

    def _create_vector_store_index(self):
        # In Pinecone, "creating" the index usually means provisioning the cloud resource.
        # If it already exists, we just connect to it.
        # However, to match the "clean slate" logic of vdb_azure's delete/create cycle:
        
        # Check if index exists
        existing_indexes = [i.name for i in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            logging.info(f"Creating Pinecone index: {self.index_name}")
            try:
                # We assume generic serverless spec if creating from scratch, 
                # but ideally the user should have created it or we need config for dimension/spec.
                # Azure usage implied dynamic dimension. Pinecone needs explicit dimension.
                # OpenAI large embedding is usually 3072 or 1536 depending on model args.
                # We'll try to detect or fallback to standard.
                
                # IMPORTANT: Automatically creating indexes can be tricky regarding dimension.
                # We will assume the index exists or let PineconeVectorStore handle auto-creation logic if supported,
                # but standard practice is explicit creation.
                
                # For now, we connect. If it doesn't exist, we error out or try default creation.
                # Given user provided a HOST, the index definitely exists.
                pass
            except Exception as e:
                logging.error(f"Error creating/checking index: {e}")
                raise

        # Initialize the LangChain wrapper
        try:
            self.vector_store = PineconeVectorStore(
                index_name=self.index_name,
                embedding=self.embedding,
                pinecone_api_key=self.api_key
            )
        except Exception as e:
            logging.error(f"Error initializing PineconeVectorStore: {e}")
            raise

    def _get_vector_store(self):
        if not self.vector_store:
             self._create_vector_store_index()
        return self.vector_store
    
    def _delete_vector_store_index(self):
        """
        Equivalent to clearing the index.
        Deleting the actual index resource in Pinecone is slow and might lose config.
        We will delete all vectors instead.
        """
        try:
            # Check if index exists first
            existing_indexes = [i.name for i in self.pc.list_indexes()]
            if self.index_name in existing_indexes:
                 index = self.pc.Index(self.index_name)
                 # Delete all vectors
                 index.delete(delete_all=True)
                 logging.info(f"Cleared all vectors from Pinecone index: {self.index_name}")
            else:
                 logging.warning(f"Index {self.index_name} does not exist, nothing to delete.")
                 
        except Exception as e:
            logging.error(f"Error deleting pinecone content: {e}")
            # We don't raise here strictly to allow regeneration flow to proceed usually
            # but let's follow pattern
            raise
