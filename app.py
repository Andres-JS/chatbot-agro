from flask import Flask, request, Response
import pandas as pd
from rapidfuzz import process
import re
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# ✅ Cargar Excel CON manejo de error
try:
    df = pd.read_excel("insumos.xlsx")
    df.columns = df.columns.astype(str).str.strip().str.upper()
except Exception as e:
    df = None
    print("❌ Error cargando Excel:", e)

# ✅ Limpiar texto
def limpiar(texto):
    if pd.isna(texto):
        return ""
    texto = re.sub(r'\[|\]|\(.*?\)', '', str(texto))
    texto = re.sub(r'FERTILIZANTES|PLAGUICIDA|HERBICIDA', '', texto)
    return texto.strip().upper()

# ✅ Preparar datos si Excel carga
if df is not None:
    try:
        col_producto = [c for c in df.columns if "PRODUCTO" in c][0]
        df["PRODUCTO LIMPIO"] = df[col_producto].apply(limpiar)
    except:
        df = None
        print("❌ Error columnas en Excel")

# ✅ Buscar producto
def buscar(pregunta):
    if df is None:
        return None

    lista = df["PRODUCTO LIMPIO"].tolist()
    mejor = process.extractOne(pregunta.upper(), lista)

    if mejor:
        return df[df["PRODUCTO LIMPIO"] == mejor[0]].iloc[0]

    return None

# ✅ ENDPOINT WHATSAPP (CLAVE)
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    pregunta = request.form.get("Body", "")

    resp = MessagingResponse()

    # 🔥 PRUEBA BASE (esto garantiza que siempre responda)
    if pregunta.strip() == "":
        resp.message("✅ Bot activo pero mensaje vacío")
        return Response(str(resp), mimetype="application/xml")

    fila = buscar(pregunta)

    if fila is None:
        resp.message(f"❌ No encontré el producto: {pregunta}")
    else:
        try:
            respuesta = f"""🌱 {fila.get('PRODUCTO LIMPIO', '')}

🧪 Ingrediente:
{fila.get('COMPOSICIÓN/INGREDIENTE ACTIVO', 'No disponible')}

💧 Dosis:
{fila.get('DOSIS CAPIRO', 'No disponible')}

🐛 Controla:
{fila.get('BLANCO BIOLOGICO', 'No disponible')}"""
        except:
            respuesta = "⚠️ Error leyendo datos del producto"

        resp.message(respuesta)

    return Response(str(resp), mimetype="application/xml")


# ✅ Ruta web prueba
@app.route("/", methods=["GET"])
def home():
    return "✅ Bot funcionando"

# ✅ Ejecutar servidor
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
