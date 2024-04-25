import streamlit as st
import pandas as pd
import os
import time
from judini.codegpt import CodeGPTPlus
from dotenv import load_dotenv

# Inicializar la lista de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

load_dotenv()

# connect with codegpt
api_key = os.getenv('CODEGPT_API_KEY')
agent_id = os.getenv('CODEGPT_AGENT_ID')
org_id = os.getenv('ORG_ID')

# URL del recurso en línea (archivo CSV)
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQfqO-3z-vuoBGkkT5Hx1iM9nBTqS7hWS6ykrSO1omdhXdzKT90XvOpICyV8shXZF-NhU5wX1dripgY/pub?gid=49898854&single=true&output=csv"

# Función para cargar la información desde el enlace
@st.cache_data(ttl=3600)  # Caché la función por 1 hora
def load_context_from_url(url):
    # Cargar solo la primera columna del archivo CSV desde el enlace proporcionado
    context_data = pd.read_csv(url)
    # Convertir la columna a una cadena de texto única
    context_text = ' '.join(context_data.iloc[:, 0].astype(str).tolist())
    return context_text

# Cargar el contexto desde el enlace al iniciar el chat
context_data = load_context_from_url(url)

st.set_page_config(layout="centered")

# Establecer el color de fondo y el estilo del título
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f9f9f9;
        margin: 0;
        padding: 0;
    }
    .stTitle {
        font-family: 'Open Sans', sans-serif;
        font-size: 18px;
        color: white;
    }
    .stTextInput {
        border: 0px solid #cccccc;
        border-radius: 5px;
        padding: 0px;
    }
    .st-chat {
        padding: 0px;
    }
    .stChatMessage {
        margin: 0px 0;
    }
    .send-button {
        background-color: #1C3142;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 12px;
        cursor: pointer;
        margin-left: 5px;
    }
    .send-button:hover {
        background-color: #234158;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Crear un frame inmovil arriba del sitio
st.markdown(
    """
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 55px; background-color: #1C3142; padding: 0px; z-index: 999; display: flex; justify-content: center; align-items: center;">
    <h1 class="stTitle" style='color:white; text-align: center; font-size: 18px; margin: 0; padding: 0; font-weight: normal;'>Copiloto MS</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Para inhabilitar el link al lado del título
st.markdown("""
    <style>
    /* Hide the link button */
    .stApp a:first-child {
        display: none;
    }
    
    .css-15zrgzn {display: none}
    .css-eczf16 {display: none}
    .css-jn99sy {display: none}
    </style>
    """, unsafe_allow_html=True)

# Mensaje de bienvenida permanente
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="display: flex; align-items: flex-start; margin-top: 15px;">
        <div style="margin-right: 10px;">
            <img src='https://static.wixstatic.com/media/657f14_9eac539826124907a7b1cf189e82f308~mv2.jpeg' width='30' style='vertical-align: middle; border-radius: 50%;'>
        </div>
        <div style="text-align: justify;">
            <strong>Copiloto MS</strong><br>¡Hola! Estoy aquí para apoyarte en tareas de análisis social, estrategia comunicacional y gestión de crisis. ¿En qué puedo ayudarte?
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Display chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f"""
            <div style="display: flex; align-items: flex-start; margin-top: 15px;">
                <div style="margin-right: 10px;">
                    <img src='https://static.wixstatic.com/media/657f14_47211b5098814334998cf4e0ebe7f976~mv2.png' width='30' style='vertical-align: middle;'>
                </div>
                <div style="text-align: justify;">
                    <strong>Tú</strong><br> {message['content']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="display: flex; align-items: flex-start; margin-top: 15px;">
                <div style="margin-right: 10px;">
                    <img src='https://static.wixstatic.com/media/657f14_9eac539826124907a7b1cf189e82f308~mv2.jpeg' width='30' style='vertical-align: middle; border-radius: 50%;'>
                </div>
                <div style="text-align: justify;">
                    <strong>Copiloto MS</strong><br>{message['content']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# User input
prompt = st.chat_input("Escribe aquí", key="input")

if prompt:
    # Render user message
    user_message_container = st.empty()
    user_message_container.markdown(
        f"""
        <div style="display: flex; align-items: flex-start; margin-top: 15px;">
            <div style="margin-right: 10px;">
                <img src='https://static.wixstatic.com/media/657f14_47211b5098814334998cf4e0ebe7f976~mv2.png' width='30' style='vertical-align: middle;'>
            </div>
            <div style="text-align: justify;">
                <strong>Tú</strong><br> {prompt}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Agregar el mensaje del usuario al historial SIN el contexto
    st.session_state.messages.append({"role": "user", "content": prompt})

# Render assistant message
assistant_message_container = st.empty()

try:
    st.write("<br>", unsafe_allow_html=True)  # Inserta el espacio antes del spinner
    with st.spinner("Pensando..."):
        full_response = ""

        # connect CodeGPT SDK
        codegpt = CodeGPTPlus(api_key=api_key, org_id=org_id)
        messages = st.session_state.messages

        if messages:
            messages_with_context = [{"role": msg["role"], "content": msg["content"]} for msg in messages]

            # Añadir el contexto al último mensaje del usuario ANTES de enviarlo al asistente
            # Pero NO mostrar este contexto en la interfaz de usuario
            messages_with_context[-1]["content"] = f"CONTEXTO ACTUAL: {context_data} PROMT: {prompt}"

            response_completion = codegpt.chat_completion(agent_id=agent_id, messages=messages_with_context, stream=True)

            for response in response_completion:
                time.sleep(0.05)
                full_response += (response or "")
                assistant_message_container.markdown(
                    f"""
                    <div style="display: flex; align-items: flex-start; margin-top: 15px;">
                        <div style="margin-right: 10px;">
                            <img src='https://static.wixstatic.com/media/657f14_9eac539826124907a7b1cf189e82f308~mv2.jpeg' width='30' style='vertical-align: middle; border-radius: 50%;'>
                        </div>
                        <div style="text-align: justify;">
                            <strong>Copiloto MS</strong><br>{full_response}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.session_state.messages.append({"role": "assistant", "content": full_response})

except Exception as e:
    st.error(f"Se ha producido un error al llamar a la API: {e}. Por favor, intenta cargando de nuevo la página.")

    # Agrega un botón para recargar la página del navegador
    if st.button("Volver a cargar"):
        # Ejecuta JavaScript para recargar la página
        st.write("<script>parent.window.location.reload();</script>", unsafe_allow_html=True)

# Aplicar estilo al input para reducir el margen inferior
st.markdown(
    """
    <style>
    .stTextInput {
        margin-bottom: 5px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
