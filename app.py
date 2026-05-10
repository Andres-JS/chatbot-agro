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
    print("✅ Excel cargado")
except Exception as e:
    print("❌ Error Excel:", e)
    df = None

# =========================
# LIMPIAR TEXTO
# =========================
def limpiar(texto):
    if pd.isna(texto):
        return ""
    texto = re.sub(r"\[|\]|\(.*?\)", "", str(texto))
    return texto.strip().upper()

# =========================
# PREPARAR DATOS
# =========================
if df is not None:
    try:
        col_producto = [c for c in df.columns if "PRODUCTO" in c][0]
        df["BUSCAR"] = df[col_producto].apply(limpiar)
    except:
        print("❌ Error en columnas")
        df = None

# =========================
# BUSCAR PRODUCTO
# =========================
def buscar_producto(pregunta):
    if df is None:
        return None

    lista = df["BUSCAR"].tolist()
    mejor = process.extractOne(pregunta.upper(), lista)

    if mejor and mejor[1] > 85:
        return df[df["BUSCAR"] == mejor[0]].iloc[0]

    return None

# =========================
# BUSCAR POR PLAGA
# =========================
def buscar_plaga(pregunta):
    if df is None:
        return None

    for _, fila in df.iterrows():
        if pregunta.upper() in str(fila.get("BLANCO BIOLOGICO", "")).upper():
            return fila

    return None

# =========================
# OBTENER DOSIS
# =========================
def obtener_dosis(fila):
    try:
        col_dosis = [c for c in df.columns if "DOSIS" in c][0]
        valor = fila[col_dosis]

        if pd.isna(valor) or str(valor).strip() == "":
            return "⚠️ No registrada"

        return str(valor).replace(",", ".") + " cc/L"

    except:
        return "⚠️ No disponible"

# =========================
# RESPUESTA WHATSAPP
# =========================
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    mensaje = request.form.get("Body", "").strip()
    texto = mensaje.lower()

    resp = MessagingResponse()

    try:
        # ✅ SALUDO
        if "hola" in texto:
            resp.message(
                "👋 Hola, soy tu asistente agrícola 🌱\n\n"
                "Puedes consultarme:\n"
                "✅ Productos (amistar)\n"
                "✅ Plagas (trips, botrytis)\n\n"
                "Ejemplo: 'qué uso para botrytis'"
            )
            return Response(str(resp), mimetype="application/xml")

        # ✅ BUSCAR PRODUCTO
        fila = buscar_producto(mensaje)

        # ✅ SI NO ENCUENTRA → BUSCAR POR PLAGA
        if fila is None:
            fila = buscar_plaga(mensaje)

        # ❌ SI NO ENCUENTRA
        if fila is None:
            resp.message(
                "🤔 No encontré información.\n\n"
                "Intenta con:\n"
                "• Nombre de producto (amistar)\n"
                "• Plaga (trips, roya)"
            )
            return Response(str(resp), mimetype="application/xml")

        # ✅ DOSIS
        dosis = obtener_dosis(fila)

        # ✅ RESPUESTA INTELIGENTE (TIPO CHATGPT)
        respuesta = f"""🌱 *{fila.iloc[0]}*

✅ *Recomendación agronómica*

Este producto es una buena opción para el manejo de:

🐛 {fila.get('BLANCO BIOLOGICO', 'No disponible')}

🧪 *Ingrediente activo:*
{fila.get('COMPOSICIÓN/INGREDIENTE ACTIVO', 'No disponible')}

💧 *Dosis recomendada:*
{dosis}

📌 *Consejo técnico:*
Aplicar en condiciones adecuadas y rotar modos de acción para evitar resistencia.
"""

        resp.message(respuesta)

    except Exception as e:
        print("❌ Error general:", e)
        resp.message("⚠️ Error interno, intenta de nuevo")

    return Response(str(resp), mimetype="application/xml")

# =========================
# TEST WEB
# =========================
@app.route("/")
def home():
    return "✅ Bot agrícola funcionando"

# =========================
# EJECUCIÓN
# =========================
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
