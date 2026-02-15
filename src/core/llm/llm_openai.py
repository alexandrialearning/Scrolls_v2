import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Any
from langchain_openai import OpenAIEmbeddings
from src.graph.state.graph_state import ChatResponseGeneric

load_dotenv()

class LLMOpenAI:

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.chat_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")
        self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

        self.embeddings = None


#region Chat
    def _init_chat_client(self):
        try:
            client: OpenAI = OpenAI(
                api_key=self.api_key
            )

        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            raise

        self.client = client


    def _get_chat_client(self):
        self._init_chat_client()
        return self.client


    def _get_chat_response(self, max_tokens: int = 4096, temperature: float = 0.0, system_message: str = "", developer_message: str = "", user_message: str = "", text_format: Any = ChatResponseGeneric):
        try:
            client = self._get_chat_client()

            # response = client.chat.completions.create(
            response = client.beta.chat.completions.parse(
                messages=[
                    {
                        "role": "system",
                        "content": f"{system_message}",
                    },
                    {
                        "role": "developer",
                        "content": f"{developer_message}",
                    },
                    {
                        "role": "user",
                        "content": f"{user_message}",
                    },
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                model=self.chat_model,
                response_format=text_format
            )

        except Exception as e:
            print(f"Error getting chat response: {e}")
            raise

        # return response.choices[0].message.content
        return response.output_parsed
    
    
    def _get_chat_response_instructions(self, max_tokens: int = 4096, temperature: float = 0.0, instructions_message: str = "", input_message: str = "", text_format: Any = ChatResponseGeneric):
        try:
            client = self._get_chat_client()

            response = client.beta.chat.completions.parse(
                messages=[
                    {"role": "system", "content": instructions_message},
                    {"role": "user", "content": input_message}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                model=self.chat_model,
                response_format=text_format
            )

        except Exception as e:
            print(f"Error getting chat response: {e}")
            raise

        # return response.choices[0].message.content
        return response.output_parsed
#endregion


#region Embeddings
    def _init_embedding(self):
        try:
            embeddings: OpenAIEmbeddings = OpenAIEmbeddings(
                api_key=self.api_key,
                model=self.embedding_model,
            )

        except Exception as e:
            print(f"Error initializing AzureOpenAIEmbeddings: {e}")
            raise

        self.embeddings = embeddings

  
    def _get_embedding(self):
        self._init_embedding()
        return self.embeddings
#endregion

#    _____
#   ( \/ @\____
#   /           O
#  /   (_|||||_/
# /____/  |||
#       kimba