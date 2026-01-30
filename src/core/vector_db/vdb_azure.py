import os
import logging
from dotenv import load_dotenv
from langchain_community.vectorstores.azuresearch import AzureSearch
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    ScoringProfile,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    TextWeights,
)

load_dotenv()

class AzureVectorStore:
    
    def __init__(self, embedding, index_name: str = "langchain-vector-demo"):
        try:
            self.index_name = index_name

            self.embedding_function = embedding.embed_query

            self.fields = [
                SimpleField(
                    name="id",
                    type=SearchFieldDataType.String,
                    key=True,
                    filterable=True,
                ),
                SearchableField(
                    name="content",
                    type=SearchFieldDataType.String,
                    searchable=True,
                ),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=len(self.embedding_function("Text")),
                    vector_search_profile_name="myHnswProfile",
                ),
                SearchableField(
                    name="metadata",
                    type=SearchFieldDataType.String,
                    searchable=True,
                ),
                # Additional field to store the title
                SearchableField(
                    name="name",
                    type=SearchFieldDataType.String,
                    searchable=True,
                ),
                # Additional field to store the title
                SearchableField(
                    name="page_number",
                    type=SearchFieldDataType.String,
                    searchable=True,
                ),
                # Additional field for filtering on document source
                SimpleField(
                    name="source",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
            ]
            
            self.client = SearchIndexClient(endpoint=os.getenv("AZURE_AI_SEARCH_ENDPOINT"),
                                            credential=AzureKeyCredential(os.getenv("AZURE_AI_SEARCH_KEY")))
            
        except Exception as e:
            logging.error(f"Error initializing AzureVectorStore: {e}")
            raise

    
    def _create_vector_store_index(self):
        try:
            vector_store: AzureSearch = AzureSearch(
                azure_search_endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT"),
                azure_search_key = os.getenv("AZURE_AI_SEARCH_KEY"),
                index_name = self.index_name,
                embedding_function = self.embedding_function,
                fields=self.fields
            )

        except Exception as e:
            logging.error(f"Error creating Azure Search index: {e}")
            raise

        self.vector_store = vector_store
    

    def _get_vector_store(self):
        return self.vector_store
    

    def _delete_vector_store_index(self):
        try:
            self.client.delete_index(index=self.index_name)
            logging.info("Azure Search index deleted successfully.")

        except Exception as e:
            logging.error(f"Error deleting Azure Search index: {e}")
            raise


#    _____
#   ( \/ @\____
#   /           O
#  /   (_|||||_/
# /____/  |||
#       kimba