import logging
from src.graph.state.graph_state import State
from src.core.database.json_chat_history import JsonChatHistory

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