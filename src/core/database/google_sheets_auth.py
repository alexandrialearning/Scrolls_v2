import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# We need both Drive (to find the file) and Sheets (to read it)
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

class GoogleSheetsAuth:
    def __init__(self):
        self.creds = None
        if os.path.exists('token.json'):
            # Note: If adding new scopes, the existing token.json must be deleted
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception:
                    self.creds = None

            if not self.creds:
                client_secrets_file = os.getenv("GOOGLE_CLIENT_SECRETS_FILE", "credentials.json")
                if os.path.exists(client_secrets_file):
                    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                    with open('token.json', 'w') as token:
                        token.write(self.creds.to_json())

        if self.creds:
            self.service = build('sheets', 'v4', credentials=self.creds)
        else:
            self.service = None

    def get_users_dict(self, spreadsheet_id: str):
        """
        Reads a Google Sheet and returns a dictionary of {email: password}.
        Tries to discover sheet names automatically.
        """
        try:
            if not self.service:
                return {}
            
            # 1. Get spreadsheet metadata to find all sheet names
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheet_names = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
            
            # 2. Try common ones first, then any others
            priority_names = ["Sheet1", "Hoja1", "Hoja 1", "Users", "Usuarios"]
            # Reorder sheet_names to put priority_names first if they exist
            ordered_names = [n for n in priority_names if n in sheet_names] + [n for n in sheet_names if n not in priority_names]

            for sheet_name in ordered_names:
                try:
                    range_name = f"{sheet_name}!A:B"
                    result = self.service.spreadsheets().values().get(
                        spreadsheetId=spreadsheet_id, 
                        range=range_name
                    ).execute()
                    
                    values = result.get('values', [])
                    if not values:
                        continue

                    users = {}
                    for row in values:
                        if len(row) >= 2:
                            email = str(row[0]).strip().lower()
                            password = str(row[1]).strip()
                            if email and password: # Ensure neither is empty
                                users[email] = password
                    
                    if users:
                        logging.info(f"Successfully loaded users from sheet: {sheet_name}")
                        return users
                except Exception:
                    continue
            
            return {}
        except Exception as e:
            logging.error(f"Error discovering sheets: {e}")
            return {}
