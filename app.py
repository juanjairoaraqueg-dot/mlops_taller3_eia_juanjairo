"""API de predicción de salarios en ciencia de datos - Taller 3 MLOps EIA.

Expone el pipeline entrenado (modelo_salarios.pkl) mediante FastAPI. El pipeline
recibe los datos CRUDOS del perfil (sin transformaciones) y devuelve el salario
estimado en USD.

Autor: Juan Jairo Araque Giraldo (completado con asistencia de Claude / Anthropic).

Ejecución local:
    uvicorn app:app --host 0.0.0.0 --port 8000
"""

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

# Se carga el pipeline una sola vez al iniciar la aplicación
pipeline = joblib.load("modelo_salarios.pkl")

# Orden de columnas que espera el pipeline
COLUMNAS_ENTRADA = [
    "año_trabajo", "nivel_experiencia", "tipo_empleo", "titulo_trabajo",
    "residencia_empleado", "ratio_remoto", "ubicacion_empresa", "tamaño_empresa",
]

app = FastAPI(
    title="API Predicción de Salarios - Taller 3 MLOps EIA",
    description="Recibe un perfil crudo de ciencia de datos y estima el salario en USD.",
    version="1.0.0",
)


class EntradaSalario(BaseModel):
    """Esquema de entrada: datos crudos del perfil (sin transformaciones)."""

    año_trabajo: str = Field(..., examples=["2023"])
    nivel_experiencia: str = Field(..., examples=["SE"])
    tipo_empleo: str = Field(..., examples=["FT"])
    titulo_trabajo: str = Field(..., examples=["Data Scientist"])
    residencia_empleado: str = Field(..., examples=["US"])
    ratio_remoto: str = Field(..., examples=["100"])
    ubicacion_empresa: str = Field(..., examples=["US"])
    tamaño_empresa: str = Field(..., examples=["M"])


@app.get("/")
def health_check():
    """Endpoint de salud para verificar que el servicio está arriba."""
    return {"estado": "ok", "mensaje": "API de predicción de salarios activa"}


@app.post("/predict")
def predict(entrada: EntradaSalario):
    """Recibe el perfil crudo y devuelve el salario estimado en USD."""
    # Se arma un DataFrame de una fila con el orden de columnas esperado
    fila = pd.DataFrame([entrada.model_dump()])[COLUMNAS_ENTRADA].astype(str)
    prediccion = float(pipeline.predict(fila)[0])
    return {"salario_en_usd_estimado": round(prediccion, 2)}
