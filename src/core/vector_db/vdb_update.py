import logging
from src.core.llm.llm_openai import LLMOpenAI
from src.core.vector_db.vdb_pinecone import PineconeVectorDB
from langchain_text_splitters import CharacterTextSplitter
from src.core.database.azure_storage_blob import AzureStorageBlobDatabase
from src.core.database.google_drive import GoogleDriveDatabase
from src.core.database.local_file_system import LocalFileSystemDatabase

class UpdateVectorDB:
    
    def __init__(self, index_name: str, chunk_size: int = 1000, chunk_overlap: int = 200):
        # Getting pdf documents from Azure Blob Storage / Google Drive / Local
        self.azure_storage_blob_db = AzureStorageBlobDatabase()
        self.google_drive_db = GoogleDriveDatabase()
        self.local_fs_db = LocalFileSystemDatabase()

        # Setting up embedding
        self.llmOpenAI = LLMOpenAI()
        self.embeddingOpenAI = self.llmOpenAI._get_embedding()

        # Setting up Pinecone Vector Store
        self.index_name = index_name
        self.vector_store_model = PineconeVectorDB(embedding=self.embeddingOpenAI, 
                                                         index_name=self.index_name)

        # Setting up text splitter
        self.text_splitter = CharacterTextSplitter(chunk_size=chunk_size, 
                                                   chunk_overlap=chunk_overlap)


    def _azure_upload_vector_store(self, name_folder: str):
        # NOTE: Keeping method name for compatibility if called elsewhere, but logic is Pinecone now
        # Ideally should rename to _upload_to_vector_store generic
        try:
            self.vector_store_model._delete_vector_store_index()
            self.vector_store_model._create_vector_store_index()

            docs_loaded = self.azure_storage_blob_db._load_pdfs_blob(name_folder=name_folder)

            if not docs_loaded:
                logging.warning(f"No documents found in folder '{name_folder}'")
                return
            
            docs = self.text_splitter.split_documents(docs_loaded)
            vector_store = self.vector_store_model._get_vector_store()

            vector_store.add_texts(
                texts=[doc.page_content for doc in docs],
                metadatas = [{
                    "name": doc.metadata.get("name", ""),
                    "page_number": str(doc.metadata.get("page_number", "")),
                    "url": doc.metadata.get("url", ""),
                } for doc in docs])

            logging.info(f"Documents added to Pinecone successfully. Total documents: {len(docs)}")

        except Exception as e:
            logging.error(f"Error uploading to Pinecone: {e}")
            raise


    def _local_upload_vector_store(self, directory_path: str):
        try:
            self.vector_store_model._delete_vector_store_index()
            self.vector_store_model._create_vector_store_index()

            docs_loaded = self.local_fs_db._load_pdfs_local(directory_path=directory_path)

            if not docs_loaded:
                logging.warning(f"No documents found in directory '{directory_path}'")
                return
            
            docs = self.text_splitter.split_documents(docs_loaded)
            vector_store = self.vector_store_model._get_vector_store()

            vector_store.add_texts(
                texts=[doc.page_content for doc in docs],
                metadatas = [{
                    "name": doc.metadata.get("name", ""),
                    "page_number": str(doc.metadata.get("page_number", "")),
                    "url": doc.metadata.get("url", ""),
                    "source": "local_filesystem"
                } for doc in docs])

            logging.info(f"Documents from Local Directory added to Pinecone successfully. Total documents: {len(docs)}")

        except Exception as e:
            logging.error(f"Error uploading from Local Directory to Vector Store: {e}")
            raise

    def _drive_upload_vector_store(self, folder_id: str):
        try:
            self.vector_store_model._delete_vector_store_index()
            self.vector_store_model._create_vector_store_index()

            # Note: _load_files_drive now handles pdfs, images, and videos
            docs_loaded = self.google_drive_db._load_files_drive(folder_id=folder_id)

            if not docs_loaded:
                logging.warning(f"No documents found in Drive folder '{folder_id}'")
                return
            
            docs = self.text_splitter.split_documents(docs_loaded)
            vector_store = self.vector_store_model._get_vector_store()

            vector_store.add_texts(
                texts=[doc.page_content for doc in docs],
                metadatas = [{
                    "name": doc.metadata.get("name", ""),
                    "page_number": str(doc.metadata.get("page_number", "")),
                    "url": doc.metadata.get("url", ""),
                    "source": "google_drive"
                } for doc in docs])

            logging.info(f"Documents from Drive added to Pinecone successfully. Total documents: {len(docs)}")

        except Exception as e:
            logging.error(f"Error uploading from Drive to Pinecone: {e}")
            raise