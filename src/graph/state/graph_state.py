from pydantic import BaseModel
from langchain_core.documents import Document
from typing import Optional, Union, List, TypedDict, Any

class ChatResponseGeneric(BaseModel):
    response: str

class TaskRoute(BaseModel):
    response: bool

class State(TypedDict):
    user_id: str
    user_question: str
    user_question_validation: bool

    chatbot_answer: Optional[str]
    chatbot_answer_visualization: Optional[str]

    alexandria_type_learning: Optional[int]

    node_upload_vector_store: Optional[bool]
    node_retrieve_docs: Optional[List[Document]]