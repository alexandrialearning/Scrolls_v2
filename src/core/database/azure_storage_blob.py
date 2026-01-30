import io
import os
import logging
from pypdf import PdfReader
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from langchain_core.documents import Document

load_dotenv()

class AzureStorageBlobDatabase:
    
    def __init__(self):
        connection_string = os.getenv("AZURE_BLOB_CONNECTION_STRING")
        container_name = os.getenv("AZURE_BLOB_CONTAINER_NAME")

        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)


    def _load_pdfs_blob(self, name_folder:str="") -> list:
        try:
            docs_loaded = []
            
            if name_folder == "":
                return docs_loaded
            
            blob_list = self.container_client.list_blobs()

            for blob in blob_list:
                logging.info(f"--> Leyendo blob: {blob.name}")

                blob_client = self.container_client.get_blob_client(blob.name)
                blob_content_bytes =blob_client.download_blob().readall()

                pdf_stream = io.BytesIO(blob_content_bytes)
                pdf_reader = PdfReader(pdf_stream)

                total_pages = len(pdf_reader.pages)

                name = os.path.basename(blob.name)
                name_no_ext = os.path.splitext(name)[0]

                for i, page in enumerate(pdf_reader.pages):

                    text_page = page.extract_text()

                    metadata = {
                        "name": name_no_ext,
                        "page_number": i + 1,
                        "url": f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_client.container_name}/{blob.name}",
                        "total_pages": total_pages,
                    }

                    doc = Document(page_content=text_page,
                                   metadata=metadata)
                    
                    docs_loaded.append(doc)

            logging.info(f"Total blobs cargados desde '{name_folder}': {len(docs_loaded)}")

        except Exception as e:
            logging.error(f"Error loading blobs: {e}")
            raise

        return docs_loaded
    

#    _____
#   ( \/ @\____
#   /           O
#  /   (_|||||_/
# /____/  |||
#       kimba