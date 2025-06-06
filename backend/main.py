from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

# Cargar el modelo de clasificación de texto
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Definir las etiquetas de clasificación
etiquetas = [
    "Necesita atención inmediata (Urgente)",
    "Puede esperar un poco (Moderado)",
    "No requiere atención (Normal)"
]

# Definir el modelo de datos para la entrada
class Mensaje(BaseModel):
    texto: str

@app.post("/clasificar/")
def clasificar(data: Mensaje):
    resultado = classifier(data.texto, etiquetas)
    
    # Extraer la categoría y confianza del resultado
    categoria_completa = resultado["labels"][0]
    confianza = resultado["scores"][0]

    # Verificar si la categoría es "Necesita atención inmediata" y ajustar si la confianza es baja
    if "inmediata" in categoria_completa and confianza < 0.85:
        categoria_completa = resultado["labels"][1]
        confianza = resultado["scores"][1]

    # Extraer la categoría sin el texto adicional
    if "(" in categoria_completa and ")" in categoria_completa:
        categoria = categoria_completa.split("(")[-1].replace(")", "").strip()
    else:
        categoria = categoria_completa

    # Preparar los detalles de la clasificación
    detalles = {
        lbl.split("(")[-1].replace(")", "").strip(): round(score * 100, 2)
        for lbl, score in zip(resultado["labels"], resultado["scores"])
    }

    return {
        "categoria": categoria,
        "confianza": round(confianza * 100, 2),
        "detalles": detalles
    }
