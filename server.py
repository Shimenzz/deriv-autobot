from flask import Flask, request
import asyncio
import websockets
import json
import requests
import threading
import os  # IMPORTANTE para que funcione en Railway

# === TUS DATOS ===
DERIV_TOKEN = "fZH8MyIQKvukkvF"
TELEGRAM_TOKEN = "7856326276:AAEHUWRR3mjt-_0E8d_rAy2YGNBkBwuhfTg"
TELEGRAM_CHAT_ID = "519103447"
DERIV_WS_URL = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

app = Flask(__name__)

def enviar_alerta_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    requests.post(url, data=data)

async def operar_en_deriv(signal_data):
    activo = signal_data.get("activo", "frxEURJPY")
    tipo = signal_data.get("tipo", "buy").upper()
    duracion = 5

    contract_type = "CALL" if tipo == "BUY" else "PUT"

    ws = await websockets.connect(f"{DERIV_WS_URL}&token={DERIV_TOKEN}")

    buy_request = {
        "buy": "1",
        "price": 0,
        "parameters": {
            "amount": 1,
            "basis": "stake",
            "contract_type": contract_type,
            "currency": "USD",
            "duration": duracion,
            "duration_unit": "m",
            "symbol": activo
        },
        "req_id": 1
    }

    await ws.send(json.dumps(buy_request))
    response = await ws.recv()
    data = json.loads(response)

    if "buy" in data:
        transaction_id = data["buy"]["transaction_id"]
        enviar_alerta_telegram(f"🚨 Operación enviada: {activo} - {tipo} - {duracion}min")
    else:
        enviar_alerta_telegram("❌ Error al enviar operación")
        await ws.close()
        return

    await asyncio.sleep(duracion * 60 + 5)

    await ws.send(json.dumps({"portfolio": 1, "req_id": 2}))
    portfolio_data = await ws.recv()
    port = json.loads(portfolio_data)

    result_msg = "🔄 Resultado no encontrado"
    if "portfolio" in port and port["portfolio"].get("contracts"):
        for c in port["portfolio"]["contracts"]:
            if c.get("transaction_id") == transaction_id:
                profit = float(c.get("profit", 0))
                if profit > 0:
                    result_msg = "✅ Operación GANADA"
                else:
                    result_msg = "❌ Operación PERDIDA"
                break

    enviar_alerta_telegram(result_msg)
    await ws.close()

def iniciar_operacion_en_hilo(signal_data):
    asyncio.run(operar_en_deriv(signal_data))

@app.route("/webhook", methods=["POST"])
def recibir_alerta():
    signal_data = request.get_json()
    if not signal_data:
        return "⚠️ Formato inválido", 400

    threading.Thread(target=iniciar_operacion_en_hilo, args=(signal_data,)).start()
    return "✅ Señal recibida", 200

# === ESTO ES LO QUE HACE QUE FUNCIONE EN RAILWAY ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
