import logging
from src.graph.state.graph_state import State
from src.core.database.json_chat_history import JsonChatHistory
from src.core.database.google_sheets_history import GoogleSheetsHistory
import os
import streamlit as st

class NodeChatHistory:

    def __init__(self):
        pass


    def run(self, state:State):
        try:
            user_id = state.get("user_id", "")
            user_question = state.get("user_question", "")
            chatbot_answer = state.get("chatbot_answer", "")

            json_chat_history = JsonChatHistory()
            json_chat_history.add_responses(user_id, user_question, chatbot_answer)

            # --- Log to Google Sheets ---
            spreadsheet_id = os.getenv("CHAT_LOGS_SPREADSHEET_ID") or st.secrets.get("CHAT_LOGS_SPREADSHEET_ID")
            if spreadsheet_id:
                try:
                    gs_history = GoogleSheetsHistory()
                    gs_history.append_log(spreadsheet_id, user_id, user_question, chatbot_answer)
                except Exception as e:
                    logging.error(f"Failed to log to Google Sheets: {e}")

        except Exception as e:
            logging.error(f"Error in NodeChatHistory run: {e}")
            raise

        return dict(state)

#    _____
#   ( \/ @\____
#   /           O
#  /   (_|||||_/
# /____/  |||
#       kimba