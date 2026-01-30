import os
import glob
import logging
from typing import List
from pypdf import PdfReader
from langchain_core.documents import Document

class LocalFileSystemDatabase:
    
    def __init__(self):
        pass

    def _load_pdfs_local(self, directory_path: str) -> List[Document]:
        """
        Loads all PDF files from a specific local directory (recursive or flat).
        """
        docs_loaded = []
        
        if not os.path.exists(directory_path):
            logging.error(f"Directory not found: {directory_path}")
            return docs_loaded

        # Find all PDFs in the directory
        # Using glob for potential recursive search if needed, here just flat for simplicity 
        # or use os.walk for recursive
        pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
        
        # If flat search yielded nothing, maybe try recursive? 
        # Let's stick to flat for now unless requested.
        
        if not pdf_files:
            logging.warning(f"No PDF files found in directory: {directory_path}")
            return docs_loaded
            
        logging.info(f"Found {len(pdf_files)} PDF files in {directory_path}")

        for file_path in pdf_files:
            try:
                logging.info(f"--> Processing file: {file_path}")
                
                # Read PDF
                with open(file_path, "rb") as f:
                    pdf_reader = PdfReader(f)
                    total_pages = len(pdf_reader.pages)
                    name = os.path.basename(file_path)
                    name_no_ext = os.path.splitext(name)[0]
                    
                    # For local files, the 'url' might be the file path itself 
                    # or a file:// URI
                    file_uri = f"file://{os.path.abspath(file_path)}"

                    for i, page in enumerate(pdf_reader.pages):
                        text_page = page.extract_text()
                        if text_page:
                            metadata = {
                                "name": name_no_ext,
                                "page_number": i + 1,
                                "url": file_uri, 
                                "total_pages": total_pages,
                                "source_type": "local_filesystem"
                            }
                            
                            doc = Document(page_content=text_page, metadata=metadata)
                            docs_loaded.append(doc)
                            
            except Exception as e:
                logging.error(f"Error parsing PDF {file_path}: {e}")
                continue

        logging.info(f"Total pages loaded from local directory: {len(docs_loaded)}")
        return docs_loaded
