import os
import json
import logging
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import streamlit as st

class GoogleSheetsHistory:
    def __init__(self):
        self.creds = None
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        
        # Load credentials using the existing logic (Streamlit Secrets priority)
        if "GOOGLE_TOKEN_JSON" in st.secrets:
            try:
                token_info = json.loads(st.secrets["GOOGLE_TOKEN_JSON"])
                self.creds = Credentials.from_authorized_user_info(token_info, SCOPES)
            except Exception as e:
                logging.error(f"Error loading GOOGLE_TOKEN_JSON for Sheets History: {e}")
        elif os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        if self.creds:
            self.service = build('sheets', 'v4', credentials=self.creds)
        else:
            self.service = None

    def append_log(self, spreadsheet_id: str, user_id: str, question: str, answer: str):
        """Appends a new conversation log to the specified Google Sheet."""
        if not self.service:
            logging.error("Sheets service not initialized.")
            return

        # Attempt to find the correct sheet name
        possible_names = ["Sheet1", "sheets1", "Hoja1", "Logs"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        values = [[timestamp, user_id, question, answer]]
        body = {'values': values}

        for sheet_name in possible_names:
            try:
                self.service.spreadsheets().values().append(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_name}!A1",
                    valueInputOption="RAW",
                    body=body
                ).execute()
                logging.info(f"Log appended successfully to {sheet_name}")
                return # Success!
            except Exception as e:
                # If it's a "not found" error, try next one. Otherwise log error.
                if "not found" in str(e).lower():
                    continue
                else:
                    logging.error(f"Error appending to Google Sheets ({sheet_name}): {e}")
                    break
