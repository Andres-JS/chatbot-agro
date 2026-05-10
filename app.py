from flask import Flask, request, Response
import pandas as pd
from rapidfuzz import process
import re
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# =========================
# CARGAR EXCEL
# =========================
try:
    df = pd.read_excel("insumos.xlsx")
    df.columns = df.columns.astype(str).str.strip().str.upper()
except Exception as e:
    print("❌ Error cargando Excel:", e)
    df = None

# =========================
# LIMPIAR TEXTO
# =========================
def limpiar(texto):
    if pd.isna(texto):
        return ""
    texto = re.sub(r'\[|\]|\(.*?\)', '', str(texto))
    return texto.strip().upper()

# =========================
# PREPARAR DATOS
# =========================
if df is not None:
    try:
        col_producto = [c for c in df.columns if "PRODUCTO" in c][0]
        df["PRODUCTO LIMPIO"] = df[col_producto].apply(limpiar)
    except:
        print("❌ Error con columnas del Excel")
        df = None

# =========================
# BUSCAR PRODUCTO
# =========================
def buscar_producto(pregunta):
    if df is None:
        return None

    lista = df["PRODUCTO LIMPIO"].tolist()
    mejor = process.extractOne(pregunta.upper(), lista)

    if mejor and mejor[1] > 80:  # confianza mínima
        return df[df["PRODUCTO LIMPIO"] == mejor[0]].iloc[0]

    return None

# =========================
# BUSCAR POR PLAGA
# =========================
def buscar_plaga(pregunta):
    if df is None:
        return None

    for _, fila in df.iterrows():
