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
        Tries multiple common sheet names.
        """
        possible_ranges = ["Sheet1!A:B", "Hoja1!A:B", "Hoja 1!A:B"]
        
        for range_name in possible_ranges:
            try:
                if not self.service:
                    continue
                
                sheet = self.service.spreadsheets()
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
                values = result.get('values', [])

                if not values:
                    continue

                users = {}
                for row in values:
                    if len(row) >= 2:
                        email = str(row[0]).strip().lower()
                        password = str(row[1]).strip()
                        users[email] = password
                
                if users:
                    return users
            except Exception as e:
                logging.debug(f"Range {range_name} not found or error: {e}")
                continue
        
        return {}
