
# Deriv Autobot - Automatización con TradingView

## Requisitos
- Python 3.10+
- Instalar dependencias:
  pip install -r requirements.txt

## Uso
1. Ejecutar el servidor:
   python server.py

2. En TradingView, crear alerta con Webhook:
   http://TU_IP_PUBLICA_O_RAILWAY_URL:5000/webhook

3. Mensaje de alerta:
   {"activo": "frxEURJPY", "tipo": "buy"}  o  {"activo": "frxEURJPY", "tipo": "sell"}

4. El bot operará automáticamente en Deriv (cuenta demo) y enviará los resultados a Telegram.
