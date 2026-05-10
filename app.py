from flask import Flask, request, Response
import pandas as pd
from rapidfuzz import process
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# =========================
# CARGAR EXCEL SEGURO
# =========================
try:
    df = pd.read_excel("insumos.xlsx")
    df.columns = df.columns.astype(str).str.strip().str.upper()
    print("✅ Excel cargado correctamente")
    print(df.columns)
except Exception as e:
    print("❌ Error cargando Excel:", e)
    df = None

# =========================
# BUSCAR PRODUCTO
# =========================
def buscar(pregunta):
    if df is None:
        return None

    try:
        col_producto = [c for c in df.columns if "PRODUCTO" in c][0]
        lista = df[col_producto].astype(str).str.upper().tolist()

        mejor = process.extractOne(pregunta.upper(), lista)

        if mejor and mejor[1] > 80:
            return df[df[col_producto].astype(str).str.upper() == mejor[0]].iloc[0]

    except Exception as e:
        print("❌ Error en búsqueda:", e)

    return None

# =========================
# FORMATEAR DOSIS
# =========================
def obtener_dosis(fila):
    try:
        col_dosis = [c for c in df.columns if "DOSIS" in c][0]
        valor = fila[col_dosis]

        if pd.isna(valor) or str(valor).strip() == "":
            return "⚠️ No registrada"

        return str(valor).replace(",", ".")
    except:
        return "⚠️ No disponible"

# =========================
# ENDPOINT WHATSAPP
# =========================
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    mensaje = request.form.get("Body", "").strip()

    resp = MessagingResponse()

    try:
        if mensaje.lower() == "hola":
            resp.message("👋 Hola, soy tu asistente agrícola 🌱")
            return Response(str(resp), mimetype="application/xml")

        fila = buscar(mensaje)

        if fila is None:
            resp.message(f"❌ No encontré: {mensaje}")
            return Response(str(resp), mimetype="application/xml")

        dosis = obtener_dosis(fila)

        respuesta = f"""🌱 {fila.iloc[0]}

🧪 Ingrediente:
{fila.get('COMPOSICIÓN/INGREDIENTE ACTIVO', 'No disponible')}

💧 Dosis:
{dosis}

🐛 Controla:
{fila.get('BLANCO BIOLOGICO', 'No disponible')}
"""

        resp.message(respuesta)

    except Exception as e:
        print("❌ ERROR CRÍTICO:", e)
        resp.message("⚠️ Error interno del bot")

    return Response(str(resp), mimetype="application/xml")

# =========================
# TEST WEB
# =========================
@app.route("/")
def home():
    return "✅ Bot funcionando"

# =========================
# RUN
# =========================
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
