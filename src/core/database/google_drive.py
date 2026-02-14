import os
import io
import logging
from typing import List
# from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from pypdf import PdfReader
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GoogleDriveDatabase:
    
    def __init__(self):
        """
        Shows basic usage of the Drive v3 API.
        """
        self.creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        elif "GOOGLE_TOKEN_JSON" in os.environ:
             # Try to load from env (Streamlit Secrets)
             import json
             try:
                 token_info = json.loads(os.environ["GOOGLE_TOKEN_JSON"])
                 self.creds = Credentials.from_authorized_user_info(token_info, SCOPES)
             except Exception as e:
                 logging.error(f"Error loading GOOGLE_TOKEN_JSON from env: {e}")
        elif "GOOGLE_TOKEN_JSON" in st.secrets:
             # Try to load from streamlit secrets directly
             import json
             try:
                 token_info = json.loads(st.secrets["GOOGLE_TOKEN_JSON"])
                 self.creds = Credentials.from_authorized_user_info(token_info, SCOPES)
             except Exception as e:
                 logging.error(f"Error loading GOOGLE_TOKEN_JSON from secrets: {e}")
            
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    logging.warning(f"Error refreshing token: {e}. Re-authenticating...")
                    self.creds = None

            if not self.creds:
                # We need a credentials.json (Client ID) to identify the APP
                # This is standard OAuth requirement.
                client_secrets_file = os.getenv("GOOGLE_CLIENT_SECRETS_FILE", "credentials.json")
                if not os.path.exists(client_secrets_file):
                    logging.error(f"Client Secrets file not found: {client_secrets_file}. REQUIRED for OAuth.")
                    # Fallback to none, will fail later
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        client_secrets_file, SCOPES)
                    
                    # Run local server for auth
                    self.creds = flow.run_local_server(port=0)
                    
                    # Save the credentials for the next run
                    with open('token.json', 'w') as token:
                        token.write(self.creds.to_json())

        if self.creds:
            self.service = build('drive', 'v3', credentials=self.creds)
        else:
            self.service = None

    def _load_files_drive(self, folder_id: str) -> List[Document]:
        """
        Loads PDFs, Images, and Videos from a Google Drive folder.
        - PDFs: Content is extracted text.
        - Images/Videos: Content is the filename (for searching) and Metadata contains the URL.
        """
        docs_loaded = []
        try:
            if not self.service:
                logging.error("Google Drive service not initialized. Check credentials.")
                return []

            # Query for files in folder (excluding trash)
            # MimeTypes: application/pdf, image/*, video/*
            query = f"'{folder_id}' in parents and trashed = false and (mimeType = 'application/pdf' or mimeType contains 'image/' or mimeType contains 'video/')"
            
            results = self.service.files().list(
                q=query, 
                pageSize=100, 
                fields="nextPageToken, files(id, name, mimeType, webViewLink, webContentLink)"
            ).execute()
            
            items = results.get('files', [])

            if not items:
                logging.warning(f"No relevant files found in Drive folder ID: {folder_id}")
                return docs_loaded

            for item in items:
                file_id = item['id']
                file_name = item['name']
                mime_type = item['mimeType']
                web_view_link = item.get('webViewLink', '')
                
                logging.info(f"--> Processing Drive file: {file_name} ({mime_type})")
                
                name_no_ext = os.path.splitext(file_name)[0]
                
                if 'application/pdf' in mime_type:
                    # Process PDF
                    docs_loaded.extend(self._process_pdf(file_id, file_name, web_view_link))
                else:
                    # Process Image or Video (Metadata only)
                    # We create a document where the "content" is the filename so it can be retrieved.
                    metadata = {
                        "name": name_no_ext,
                        "page_number": 1,
                        "url": web_view_link, # Link to view in Drive
                        "total_pages": 1,
                        "source_type": "google_drive",
                        "content_type": mime_type
                    }
                    # Content is just the name for now
                    doc = Document(page_content=f"Archivo multimedia: {file_name}", metadata=metadata)
                    docs_loaded.append(doc)

            logging.info(f"Total documents loaded from Drive: {len(docs_loaded)}")

        except Exception as e:
            logging.error(f"Error interacting with Google Drive: {e}")
            raise

        return docs_loaded

    def _process_pdf(self, file_id, file_name, web_view_link):
        docs = []
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            fh.seek(0)
            
            pdf_reader = PdfReader(fh)
            total_pages = len(pdf_reader.pages)
            name_no_ext = os.path.splitext(file_name)[0]

            for i, page in enumerate(pdf_reader.pages):
                text_page = page.extract_text()
                if text_page:
                    metadata = {
                        "name": name_no_ext,
                        "page_number": i + 1,
                        "url": web_view_link,
                        "total_pages": total_pages,
                        "source_type": "google_drive",
                        "content_type": "application/pdf"
                    }
                    doc = Document(page_content=text_page, metadata=metadata)
                    docs.append(doc)
        except Exception as e:
             logging.error(f"Error parsing PDF {file_name}: {e}")
        
        return docs
