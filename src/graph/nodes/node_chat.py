import random
import logging
from src.graph.state.graph_state import State
from src.core.llm.llm_openai import LLMOpenAI

class NodeChat:

    def __init__(self):
        self.llmOpenAI = LLMOpenAI()


    def run(self, state:State):
        try:
            question = state.get("user_question", "")
            retrieve_docs = state.get("node_retrieve_docs", [])
            alexandria_type_learning = state.get("alexandria_type_learning", 0)

            combined_content = "\n".join([doc.page_content for doc in retrieve_docs])


            print("Alexandria Type Learning in NodeChat:", alexandria_type_learning)

            if alexandria_type_learning == 1:
                with open("src/prompts/node_chat_kinestesico.txt", "r") as f:
                    prompt_template = f.read()

            elif alexandria_type_learning == 2:
                with open("src/prompts/node_chat_visual.txt", "r") as f:
                    prompt_template = f.read()
            else:
                # Default fallback
                with open("src/prompts/node_chat_visual.txt", "r") as f:
                    prompt_template = f.read()
            

            chat_response = self.llmOpenAI._get_chat_response_instructions(
                instructions_message=prompt_template,
                input_message=f"Basado en la siguiente información: {combined_content}, responde a la pregunta: {question}",
            )

            state["chatbot_answer"] = chat_response.response
            state["chatbot_answer_visualization"] = self._select_visualization(retrieve_docs)

        except Exception as e:
            logging.error(f"Error in NodeChat run: {e}")
            raise

        return dict(state)
    

    def _select_visualization(self, retrieve_docs: list):
        try:
            # Logic: Look for the first document that has a media URL in metadata
            for doc in retrieve_docs:
                url = doc.metadata.get("url", "")
                # Google Drive WebView links or direct image extensions
                if url:
                   # If we want to be strict about images/videos, we can check extensions
                   # However, docs from Drive might just be web links.
                   # Let's check if the metadata knows the type
                   source_type = doc.metadata.get("source", "")
                   content_type = doc.metadata.get("content_type", "")
                   
                   # If we explicitly tagged it as image/video in google_drive.py
                   if "image/" in content_type or "video/" in content_type:
                       return url
                   
                   # Or fallback to file extensions if available in URL or Name
                   name = doc.metadata.get("name", "").lower()
                   if name.endswith((".jpg", ".png", ".jpeg", ".mp4", ".mov", ".gif")):
                       return url
            
            return None

        except Exception as e:
            logging.error(f"Error in _select_visualization: {e}")
            return None    

#    _____
#   ( \/ @\____
#   /           O
#  /   (_|||||_/
# /____/  |||
#       kimba
