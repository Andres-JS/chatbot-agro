from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# ✅ Endpoint WhatsApp
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    # mensaje recibido
    mensaje = request.form.get("Body", "")

    # crear respuesta Twilio
    resp = MessagingResponse()

    # responder SIEMPRE (para comprobar conexión)
    resp.message(f"✅ BOT FUNCIONANDO\nRecibí: {mensaje}")

    return Response(str(resp), mimetype="application/xml")


# ✅ Ruta web prueba
@app.route("/", methods=["GET"])
def home():
    return "✅ Bot funcionando correctamente"


# ✅ Ejecutar servidor
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
