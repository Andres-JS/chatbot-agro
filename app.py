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
    texto = re.sub(r"\[|\]|\(.*?\)", "", str(texto))
