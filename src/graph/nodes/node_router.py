import logging
from src.graph.state.graph_state import State, TaskRoute
from src.core.llm.llm_openai import LLMOpenAI


class NodeRouter:

    def __init__(self):
        self.llmOpenAI = LLMOpenAI()


    def run(self, state:State):
        try:
            with open("src/prompts/node_router.txt", "r") as f:
                prompt_template = f.read()

            chat_response = self.llmOpenAI._get_chat_response_instructions(
                instructions_message=prompt_template,
                input_message=f"Responde a la siguiente pregunta: {state['user_question']}",
                text_format=TaskRoute
            )

            state["user_question_validation"] = chat_response.response

        except Exception as e:
            logging.error(f"Error in NodeRouter run: {e}")
            raise

        return dict(state)


#    _____
#   ( \/ @\____
#   /           O
#  /   (_|||||_/
# /____/  |||
#       kimba