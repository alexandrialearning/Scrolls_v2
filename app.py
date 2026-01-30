import os
import json
import time
import asyncio
import requests
import pandas as pd
import streamlit as st 
from io import BytesIO
from pathlib import Path
from openai import OpenAI
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv
from src.graph.builder import GraphBuilder
from src.core.vector_db.vdb_update import UpdateVectorDB


load_dotenv()

# Dummy login database
USERS_DB_DUMMY = {
    "eugeniosalasi@outlook.com": "123",
    "1":"1"
}

IMG_LOGO = "src/visualizations/Alexandr.ia_1.png"
IMG_BOT = "src/visualizations/chatbot.png"
IMG_USER = "src/visualizations/usuario.png"
URL_AZURE_STORAGE = "https://sachatbotdeveusa.blob.core.windows.net/rag/alexandria/visualizations/"

def type_learning_to_int(type_learning: str) -> int:
    mapping = {
        "Kinestésico": 1,
        "Visual": 2,
    }
    return mapping.get(type_learning, 0)


async def chat(user_question: str, user_id: str, alexandria_type_learning: int):
    try:
        graph_builder = GraphBuilder()
        graph = graph_builder.build()

        response = await graph.ainvoke({
            "user_id": user_id,
            "user_question": user_question,
            "alexandria_type_learning": alexandria_type_learning
        })

    except Exception as e:
        print(f"Error graph: {e}")
        raise

    return response.get('node_retrieve_docs', []), response.get('chatbot_answer', ".|."), response.get('chatbot_answer_visualization', ".|.")


def run_async(func, *args, **kwargs):
    return asyncio.run(func(*args, **kwargs))


def run_clean_chat_history():
    return True, ""


def loggin_screen_dummy():
    st.title("Inicio de sesión")
    st.write("Ingresa tus credenciales para acceder a la app")

    email = st.text_input("Email: ")
    password = st.text_input("Contraseña: ")

    if st.button("Iniciar sesión", type="secondary", icon="🔑"):
        if email in USERS_DB_DUMMY and USERS_DB_DUMMY[email] == password:
            st.session_state.logged_in = True
            st.session_state.email = email
            st.rerun()
        else:
            st.error("Credenciales incorrectas")


def init_page():
    st.set_page_config(page_title="Alexandr.ia Scrolls_v2", page_icon="🤖", initial_sidebar_state="collapsed")
    
    try:
        st.image(IMG_LOGO, width=300)
    except:
        pass
        
    
    st.title("Alexandr.ia Scrolls_v2")
    
    # Inicializar estado de sesión
    if "messages" not in st.session_state:
        st.session_state.messages = []


def run_update_vector_db():
    node_vector_db = UpdateVectorDB(index_name="langchain-vector-demo")
    
    # Option B: Direct Google Drive API
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id or "PASTE" in folder_id:
        st.error("Error: GOOGLE_DRIVE_FOLDER_ID not set correctly in .env")
        return False
    
    node_vector_db._drive_upload_vector_store(folder_id=folder_id)
    return True

# ---------- Callbacks ----------
def on_drection_change():
    st.session_state.run_pill = True
    st.session_state.direction = st.session_state.direction_pill
    st.session_state.direction_pill = None

def on_audio_change():
    st.session_state.audio_ready = True

# ---------- Estado inicial -----
st.session_state.setdefault("audio_ready", False)
st.session_state.setdefault("run_pill", False)


def main():

    init_page()

    # Loggin Dummy
    if not st.session_state.get("logged_in"):
        loggin_screen_dummy()
        return
    else:
        st.toast(f"¡Que gusto verte de nuevo! {st.session_state.email}")
        email_user = st.session_state.email


        try:

            #region Sidebar
            st.sidebar.markdown("### Limpiar historial")
            with st.sidebar: 
                if st.button("Limpiar", type="secondary",  icon="🧹"):
                    message, _ =  run_clean_chat_history()

                    if message:
                        m = st.success("¡El historial está limpio!", icon="✅")
                    else:
                        m = st.error("¡Algo salió mal!")

                    time.sleep(1)
                    m.empty()

                
            st.sidebar.markdown("### Limpiar conversación UI")
            if st.sidebar.button("Limpiar UI", type="secondary", icon="🧼"):
                st.session_state.messages = []
                st.rerun() 


            st.sidebar.markdown("### Ejemplos")
            with st.sidebar:
                st.session_state.setdefault("direction", None)
                directions = ["¿Cuándo fue la última vez que ...?",
                              "¿Cuál es el ...?",
                            ]
                
                st.pills("Preguntas frecuentes", 
                         options=directions, 
                         on_change=on_drection_change, 
                         key="direction_pill")
                
                st.write(f"Seleccionaste: **{st.session_state.direction}**")

            st.sidebar.markdown("### Tipo de aprendizaje")
            with st.sidebar:
                alexandria_type_learning = st.sidebar.selectbox(
                    "Selecciona el tipo de aprendizaje:",
                    options=[
                        "Kinestésico",
                        "Visual",
                    ],
                    index=0
                )

            st.sidebar.markdown("### Audio")
            with st.sidebar:
                audio_file = st.audio_input(label="Presiona el icono del micro para grabar",
                                            on_change=on_audio_change,
                                            key="audio_pill")
            
            
            st.sidebar.markdown("### Actualizar DB Vectorial")
            with st.sidebar: 
                if st.button("Actualizar", type="secondary",  icon="🔄"):
                    state =  run_update_vector_db()

                    if state:
                        m = st.success("Documentos agregados a la DB vectorial", icon="✅")
                    else:
                        m = st.error("¡Algo salió mal! (DB Vectorial)", icon="❌")

                    time.sleep(1)
                    m.empty()
            #endregion


            #region Historial de conversación
            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                avatar = IMG_BOT if message["role"] == "assistant" else IMG_USER
                with st.chat_message(message["role"], avatar=avatar):
                    st.text(message["content"])
            #endregion 


            #region Escribir petición
            user_question = None
            
            # Estado pildoras (preguntas de ejemplo)          
            if st.session_state.run_pill:
                user_question = st.session_state.direction
                st.session_state.run_pill = False

            # STT OpenAI
            # if st.session_state.audio_ready:
            #     st.session_state.audio_ready = False
            #     # Llamar OpenAI API
            #     if audio_file is not None:
            #         transcription = CLIENT.audio.transcriptions.create(model="gpt-4o-mini-transcribe",
            #                                                        file=audio_file)
            #     user_question = transcription.text
     
            # Usuario escribe su petición
            if manual_input := st.chat_input("Ingresa tu consulta: "):
                user_question = manual_input
            #endregion


            if user_question:

                st.session_state.messages.append({"role": "user", "content": user_question})
                with st.chat_message("user", avatar=IMG_USER):
                    st.markdown(user_question)

                try:
                    with st.spinner("Consultando..."):

                        start = time.time()
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(run_async, chat, user_question, email_user,  type_learning_to_int(alexandria_type_learning))
                            metada, respuesta, url = future.result()
                        end = time.time()

                        # Guardar respuesta
                        st.session_state.messages.append({"role": "assistant", "content": respuesta})

                        # Mostrar metadatos
                        for doc in metada:
                            st.caption(f"Fuente: {doc.metadata.get('name', 'N/A')} || Página: {doc.metadata.get('page_number', 'N/A')}")
                            st.caption(f"URL: {doc.metadata.get('url', 'N/A')}")

                        # Mostrar respuesta
                        with st.chat_message("assistant", avatar=IMG_BOT):
                            st.markdown(respuesta)

                        # Mostrar imagen o video
                        if url:
                            if url.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
                                st.image(f"{URL_AZURE_STORAGE}{url}")
                            elif url.lower().endswith((".mp4", ".webm", ".mov", ".ogg")):
                                st.video(f"{URL_AZURE_STORAGE}{url}")
                            else:
                                st.error("Tipo de archivo no reconocido")


                        # Mostrar tiempo
                        st.caption(f"⏳ Tiempo de respuesta: {end - start:.2f} segundos")

                except Exception as e:
                    import traceback
                    st.error(f"Ocurrió un error al procesar la solicitud: {e}")
                    print(f"Error processing request: {e}")
                    traceback.print_exc()

        except Exception as e:
            st.error("Ocurrió un error al procesar la solicitud.")
            print(f"Error in app(): {e}")
            

if __name__ == "__main__":
    main()




#    _____
#   ( \/ @\____
#   /           O
#  /   (_|||||_/
# /____/  |||
#       kimba