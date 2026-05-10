from flask import Flask, request, Response
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

# buscar producto
def buscar(pregunta):
    lista = df["PRODUCTO LIMPIO"].tolist()
    mejor = process.extractOne(pregunta.upper(), lista)

    if mejor:
        return df[df["PRODUCTO LIMPIO"] == mejor[0]].iloc[0]

    return None

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    pregunta = request.form.get("Body")

    fila = buscar(pregunta)

    resp = MessagingResponse()

    if fila is None:
        resp.message("❌ No encontré ese producto")
    else:
        respuesta = f"""🌱 {fila['PRODUCTO LIMPIO']}

🧪 Ingrediente:
{fila['COMPOSICIÓN/INGREDIENTE ACTIVO']}

💧 Dosis:
{fila['DOSIS CAPIRO']}

🐛 Controla:
{fila['BLANCO BIOLOGICO']}"""

        resp.message(respuesta)

    return Response(str(resp), mimetype="application/xml")

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot funcionando"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
