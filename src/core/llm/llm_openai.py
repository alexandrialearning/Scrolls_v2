import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from typing import Any
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from src.graph.state.graph_state import ChatResponseGeneric

load_dotenv()

class LLMOpenAI:

    def __init__(self):
        self.api_key = os.getenv("AZURE_OPEN_AI_KEY")
        self.endpoint = os.getenv("AZURE_OPEN_AI_ENDPOINT")

        self.embedding_deployment = os.getenv("AZURE_OPEN_AI_EMBEDDING_DEPLOYMENT_NAME")
        self.chat_deployment = os.getenv("AZURE_OPEN_AI_CHAT_DEPLOYMENT_NAME")

        self.embeddings = None


#region Chat
    def _init_chat_client(self):
        try:
            client: AzureOpenAI = AzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.endpoint,
                api_version="2025-03-01-preview",
            )

        except Exception as e:
            print(f"Error initializing AzureOpenAI client: {e}")
            raise

        self.client = client


    def _get_chat_client(self):
        self._init_chat_client()
        return self.client


    def _get_chat_response(self, max_tokens: int = 4096, temperature: float = 0.0, system_message: str = "", developer_message: str = "", user_message: str = "", text_format: Any = ChatResponseGeneric):
        try:
            client = self._get_chat_client()

            # response = client.chat.completions.create(
            response = client.responses.parse(
                input=[
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
                max_output_tokens=max_tokens,
                temperature=temperature,
                model=self.chat_deployment,
                text_format=text_format
            )

        except Exception as e:
            print(f"Error getting chat response: {e}")
            raise

        # return response.choices[0].message.content
        return response.output_parsed
    
    
    def _get_chat_response_instructions(self, max_tokens: int = 4096, temperature: float = 0.0, instructions_message: str = "", input_message: str = "", text_format: Any = ChatResponseGeneric):
        try:
            client = self._get_chat_client()

            # response = client.chat.completions.create(
            response = client.responses.parse(
                instructions=instructions_message,
                input=input_message,
                max_output_tokens=max_tokens,
                temperature=temperature,
                model=self.chat_deployment,
                text_format=text_format
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
            embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
                api_key=self.api_key,
                azure_endpoint=self.endpoint,
                openai_api_version="2024-12-01-preview",
                azure_deployment=self.embedding_deployment,
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