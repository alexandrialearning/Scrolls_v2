import logging
from src.graph.state.graph_state import State
from src.core.llm.llm_openai import LLMOpenAI
from src.core.vector_db.vdb_pinecone import PineconeVectorDB

class NodeRetrieve:

    def __init__(self):
        self.llmOpenAI = LLMOpenAI()
        self.embeddingOpenAI = self.llmOpenAI._get_embedding()

        self.vector_store = PineconeVectorDB(embedding=self.embeddingOpenAI)
        # self.vector_store._create_vector_store_index() # Not needed to explicitly call if we just read
        self.vector_store_model_instance = self.vector_store._get_vector_store()


    def run(self, state:State, k: int = 2):
        try:
            user_question = state.get("user_question", "")

            # Using similarity_search (standard dense retrieval) instead of hybrid
            docs = self.vector_store_model_instance.similarity_search(
                query=user_question, 
                k=k
            )

            state["node_retrieve_docs"] = docs
        
        except Exception as e:
            logging.error(f"Error in NodeRetrieve run: {e}")
            raise

        return dict(state)

#    _____
#   ( \/ @\____
#   /           O
#  /   (_|||||_/
# /____/  |||
#       kimba