import logging
from langgraph.graph import END, START, StateGraph
from langchain_core.runnables import RunnableConfig

from src.graph.state.graph_state import State
from src.graph.nodes.node_chat import NodeChat
from src.graph.nodes.node_crack import NodeCrack
from src.graph.nodes.node_router import NodeRouter
from src.graph.nodes.node_retrieve import NodeRetrieve
from src.graph.nodes.node_chat_history import NodeChatHistory


class GraphBuilder:

    def __init__(self):
        # Router
        self.node_router = NodeRouter()

        # Retrieve
        self.node_retrieve = NodeRetrieve()

        # Nodes Chat
        self.node_chat = NodeChat()
        self.node_crack = NodeCrack()
        self.node_chat_history = NodeChatHistory()


    def build(self):
        try:
            builder = StateGraph(State)

            # region ADD NODES 
            builder.add_node("router", self.node_router.run)
            builder.add_node("retrieve", self.node_retrieve.run)
            builder.add_node("chat", self.node_chat.run)
            builder.add_node("crack", self.node_crack.run)
            builder.add_node("chat_history", self.node_chat_history.run)
            # endregion

            builder.set_entry_point("router")

            builder.add_conditional_edges("router",
                                          self._router_conditional,
                                          {
                                              "RETRIEVE": "retrieve",
                                              "CRACK": "crack",
                                          })
            
            builder.add_edge("retrieve", "chat")

            builder.add_edge("chat", "chat_history")
            builder.add_edge("crack", "chat_history")
            builder.add_edge("chat_history", END)
            
            graph = builder.compile()
            self.graph = graph

        except Exception as e:
            logging.error(f"Error building graph: {e}")
            raise

        return graph


    def _router_conditional(self, state:State):
        try:
            user_question_validation = state.get("user_question_validation", False)

            if user_question_validation:
                return "RETRIEVE"
            else:
                return "CRACK"
            
        except Exception as e:
            logging.error(f"Error in _router_conditional: {e}")
            raise

    
    async def run(self, user_question:str, user_id:str, alexandria_type_learning: int):
        try:
            initial_state: State = {
                "user_id": user_id,
                "user_question": user_question,
                "user_question_validation": False,

                "chatbot_answer": None,
                "node_retrieve_docs": None,
                "alexandria_type_learning": alexandria_type_learning,
            }

            config = RunnableConfig()
            final_state = await self.graph.ainvoke(initial_state, 
                                                   config=config)

        except Exception as e:
            logging.error(f"Error running graph: {e}")
            raise
        
        return final_state
    
#    _____
#   ( \/ @\____
#   /           O
#  /   (_|||||_/
# /____/  |||
#       kimba