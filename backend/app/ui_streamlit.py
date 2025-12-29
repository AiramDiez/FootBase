import json
import streamlit as st
import requests
import time

API_URL = "http://localhost:8000/api/query/public"

st.set_page_config(
    page_title="FootBase - Seleccionador Inteligente ⚽",
    page_icon="⚽",
    layout="wide",
)

st.markdown("""
<style>
.chat-bubble-user {
    background-color: #DCF8C6;
    border-radius: 12px;
    padding: 10px 14px;
    margin: 8px 0;
    max-width: 80%;
    align-self: flex-end;
}
.chat-bubble-ai {
    background-color: #F1F0F0;
    border-radius: 12px;
    padding: 10px 14px;
    margin: 8px 0;
    max-width: 80%;
    align-self: flex-start;
    white-space: pre-wrap;   /* 👈 IMPORTANTE PARA FORMATO */
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "ai", "content": "¡Hola! 👋 Soy *FootBase*, tu seleccionador inteligente. Pídeme convocatorias, ajustes o estadísticas de jugadores."}
    ]

st.title("⚽ FootBase - Seleccionador Inteligente v2.1")
st.markdown("#### Tu asistente de selección nacional basado en IA 🧠")

# Mostrar historial
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-bubble-user'><b>Tú:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-ai'><b>FootBase:</b><br>{msg['content']}</div>", unsafe_allow_html=True)

user_input = st.text_input("Escribe tu consulta aquí...")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.spinner("SIBI está pensando... 🧩"):
        try:
            start_time = time.time()
            response = requests.get(API_URL, params={"pregunta": user_input}, timeout=120)
            duration = round(time.time() - start_time, 2)

            if response.status_code == 200:
                data = response.json()

                # 🔥 Protección total contra None o respuestas raras
                if not isinstance(data, dict):
                    ai_msg = f"⚠️ Respuesta inesperada del backend: {data}"
                else:
                    ai_msg = data.get("respuesta", "⚠️ Respuesta no válida del servidor.")

                # Si la respuesta es lista o dict → formatear bonito en JSON
                if isinstance(ai_msg, (list, dict)):
                    ai_msg = json.dumps(ai_msg, indent=2, ensure_ascii=False)


                st.session_state["messages"].append({"role": "ai", "content": ai_msg})
                st.markdown(
                    f"<div class='chat-bubble-ai'><b>FootBase:</b><br>{ai_msg}</div>",
                    unsafe_allow_html=True
                )
                st.caption(f"⏱️ Respondido en {duration}s")
            else:
                st.session_state["messages"].append({"role": "ai", "content": "❌ Error: backend no disponible."})
                st.error("❌ Error al conectar con el backend.")
        except Exception as e:
            st.session_state["messages"].append({"role": "ai", "content": f"❌ Error de conexión: {e}"})
            st.error(f"❌ Error de conexión: {e}")