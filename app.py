from flask import Flask, request
import pandas as pd
from rapidfuzz import process
import re
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Cargar Excel
df = pd.read_excel("insumos.xlsx")

# limpiar nombres de columnas
df.columns = df.columns.astype(str).str.strip().str.upper()

# limpiar texto
def limpiar(texto):
    if pd.isna(texto):
        return ""
    texto = re.sub(r'\[|\]|\(.*?\)', '', str(texto))
    texto = re.sub(r'FERTILIZANTES|PLAGUICIDA|HERBICIDA', '', texto)
    return texto.strip().upper()

# detectar columna producto
col_producto = [c for c in df.columns if "PRODUCTO" in c][0]

df["PRODUCTO LIMPIO"] = df[col_producto].apply(limpiar)
