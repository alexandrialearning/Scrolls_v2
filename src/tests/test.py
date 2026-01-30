from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from src.core.llm.llm_openai import LLMOpenAI
from src.core.vector_db.vdb_azure import AzureVectorStore
from src.core.database.azure_storage_blob import AzureStorageBlobDatabase
from src.graph.state.graph_state import TaskRoute

from src.core.vector_db.vdb_update import UpdateVectorDB

# Esto no puede ser un nodo
# tengo que llamarlo como una función dentro del front
# Upload documents and create vector store index
# node_vector_db = UpdateVectorDB(index_name="langchain-vector-demo")
# node_vector_db._azure_upload_vector_store(name_folder="alexandria")

import asyncio
from src.graph.builder import GraphBuilder

async def chat():
    try:
        graph_builder = GraphBuilder()
        graph = graph_builder.build()

        response = await graph.ainvoke({
            "user_id": "user_123",
            "user_question": "¿Cuánto mide la muralla china?"
        })

        print(f"Chat answer: {response.get('chatbot_answer')}")
        # print(f"State final: {response}")
        # print(f"\n\nMetadata docs: {response.get('node_retrieve_docs')[0].metadata}")
        
        for doc in response.get('node_retrieve_docs', []):
            print(doc.metadata)

    except Exception as e:
        print(f"Error graph: {e}")
        raise

asyncio.run(chat())



# llmOpenAI = LLMOpenAI()
# embeddings = llmOpenAI._get_embedding()

# vector_store_model = AzureVectorStore(embedding=embeddings)

# vector_store_model._create_vector_store_index()
# # vector_store_model._delete_vector_store_index()

# vector_store = vector_store_model._get_vector_store()


# # user_question = "¿Qué estudió Ali Campos?"
# # user_question = "Cuéntame un chiste sobre programadores."
# user_question = "¿Cuánto mide la muralla china?"

# # Perform a hybrid search using the hybrid_search method
# docs = vector_store.hybrid_search(
#     query=user_question, k=1
# )

# # Combinar el contenido de todos los documentos en un solo bloque de texto
# combined_content = "\n".join([doc.page_content for doc in docs])

# # Imprimir los metadatos de los documentos encontrados (opcional)
# for doc in docs:
#     print(doc.metadata)



# chat_bot = llmOpenAI._get_chat_response(
#     system_message="Eres un asistente útil.",
#     developer_message="Proporciona respuestas claras y concisas.",
#     user_message=f"Basado en la siguiente información: {combined_content}, responde a la pregunta: {user_question}",
# )
# print("\n" + chat_bot.response + "\n")


# with open("src/prompts/test.txt", "r") as f:
#     prompt_template = f.read()
# chat_bot = llmOpenAI._get_chat_response_instructions(instructions_message=prompt_template,
#                                                      input_message=f"Basado en la siguiente información: {docs[0].page_content}, responde a la pregunta: {user_question}",)
# print("\n" + chat_bot.response + "\n")
