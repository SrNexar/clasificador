from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

# Modelo Zero-Shot
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Etiquetas mejor explicadas
etiquetas = [
    "Necesita atención inmediata (Urgente)",
    "Puede esperar un poco (Moderado)",
    "No requiere atención (Normal)"
]

# Clase para recibir mensajes
class Mensaje(BaseModel):
    texto: str

@app.post("/clasificar/")
def clasificar(data: Mensaje):
    resultado = classifier(data.texto, etiquetas)
    
    # Obtener los resultados
    categoria_completa = resultado["labels"][0]
    confianza = resultado["scores"][0]

    # Regla: degradar si el score de urgente es bajo
    if "inmediata" in categoria_completa and confianza < 0.85:
        categoria_completa = resultado["labels"][1]
        confianza = resultado["scores"][1]

    # Extraer nombre corto (entre paréntesis)
    if "(" in categoria_completa and ")" in categoria_completa:
        categoria = categoria_completa.split("(")[-1].replace(")", "").strip()
    else:
        categoria = categoria_completa

    # Detalles en porcentaje
    detalles = {
        lbl.split("(")[-1].replace(")", "").strip(): round(score * 100, 2)
        for lbl, score in zip(resultado["labels"], resultado["scores"])
    }

    return {
        "categoria": categoria,
        "confianza": round(confianza * 100, 2),
        "detalles": detalles
    }
