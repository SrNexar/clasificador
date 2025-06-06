import streamlit as st
import requests

# URL del backend FastAPI
API_URL = "http://localhost:8000/clasificar/"

st.set_page_config(page_title="Clasificador de Mensajes", page_icon="📩")

st.title("📩 Clasificador de Mensajes")
st.markdown("Este sistema clasifica mensajes como **Urgente**, **Normal** o **Moderado** usando IA.")

mensaje = st.text_area("✏️ Escribe un mensaje:", height=150)

if st.button("Clasificar", type="primary"):
    if not mensaje.strip():
        st.warning("⚠️ Por favor, escribe un mensaje antes de clasificar.")
    else:
        with st.spinner("Clasificando..."):
            respuesta = requests.post(API_URL, json={"texto": mensaje})
            
            if respuesta.status_code == 200:
                data = respuesta.json()
                categoria = data["categoria"]
                confianza = data["confianza"]
                detalles = data["detalles"]

                # Colores según la categoría
                colores = {
                    "Urgente": "✅🟥",
                    "Moderado": "🟡",
                    "Normal": "🟩"
                }

                st.success(f"{colores.get(categoria, '')} **Clasificación:** {categoria}")
                st.markdown(f"🔍 **Confianza:** {confianza:.2f}%")

                st.markdown("### Detalles de confianza:")
                for cat, score in detalles.items():
                    st.markdown(f"- **{cat}**: {score:.2f}%")
            else:
                st.error("❌ Error al conectar con el servicio de clasificación.")
