import logging
from src.graph.state.graph_state import State

class NodeCrack:

    def __init__(self):
        pass


    def run(self, state:State):
        try:
            state["chatbot_answer"] = "Lo siento, no puedo contestar tu pregunta."

        except Exception as e:
            logging.error(f"Error in NodeCrack run: {e}")
            raise

        return dict(state)

#    _____
#   ( \/ @\____
#   /           O
#  /   (_|||||_/
# /____/  |||
#       kimba