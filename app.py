from flask import Flask, request, Response
import pandas as pd
from rapidfuzz import process
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# cargar Excel
df = pd.read_excel("insumos.xlsx")
df.columns = df.columns.str.upper()

# detectar columna producto
col_producto = [c for c in df.columns if "PRODUCTO" in c][0]

# crear lista de productos
df["BUSCAR"] = df[col_producto].astype(str).str.upper()

# buscar producto (con control)
def buscar(pregunta):
    lista = df["BUSCAR"].tolist()
    mejor = process.extractOne(pregunta.upper(), lista)

    # ⚠️ SOLO aceptar si confianza > 85
    if mejor and mejor[1] > 85:
        return df[df["BUSCAR"] == mejor[0]].iloc[0]

    return None

# endpoint WhatsApp
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg = request.form.get("Body", "").strip()

    resp = MessagingResponse()

    # saludo
    if msg.lower() in ["hola", "buenas"]:
        resp.message("👋 Hola, soy tu asistente agrícola 🌱\nEscribe un producto o plaga.")
        return Response(str(resp), mimetype="application/xml")

    fila = buscar(msg)

    if fila is None:
        resp.message("❌ No encontré ese producto")
    else:
        respuesta = f"""🌱 {fila[col_producto]}

🧪 Ingrediente:
{fila.get('COMPOSICIÓN/INGREDIENTE ACTIVO', 'No disponible')}

💧 Dosis:
{fila.get('DOSIS CAPIRO', 'No disponible')}

🐛 Controla:
{fila.get('BLANCO BIOLOGICO', 'No disponible')}
"""
        resp.message(respuesta)

    return Response(str(resp), mimetype="application/xml")

@app.route("/")
def home():
    return "✅ Bot funcionando"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
