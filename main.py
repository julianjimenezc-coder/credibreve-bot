"""
main.py — Punto de entrada del MVP
Levanta FastAPI + registra el webhook de Telegram

Modos de ejecución:
  MODO WEBHOOK (producción/ngrok):
    uvicorn main:app --host 0.0.0.0 --port 8000

  MODO POLLING (desarrollo local sin dominio):
    python main.py --polling
"""

import os
import sys
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from dotenv import load_dotenv
from telegram import Update

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL    = os.getenv("WEBHOOK_URL")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ Falta TELEGRAM_TOKEN en el archivo .env")

# Importar bot DESPUÉS de cargar .env (necesita OPENAI_API_KEY)
from bot import crear_app

telegram_app = crear_app(TELEGRAM_TOKEN)


# ── Lifespan: inicializar y limpiar la app de Telegram ──────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await telegram_app.initialize()
    if WEBHOOK_URL:
        await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}")
        log.info(f"✅ Webhook registrado en: {WEBHOOK_URL}")
    else:
        log.warning("⚠️  WEBHOOK_URL no definida — solo funciona en modo polling")
    await telegram_app.start()
    yield
    await telegram_app.stop()
    await telegram_app.shutdown()


app = FastAPI(
    title="CréditoSeguro API",
    description="Análisis de capacidad de pago anti gota-a-gota",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Endpoint webhook ─────────────────────────────────────────────────────────
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return Response(status_code=200)


# ── Health check para verificar que el servidor corre ───────────────────────
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "bot": TELEGRAM_TOKEN[:10] + "...",
        "webhook": WEBHOOK_URL or "no configurado (usar polling)"
    }


# ── Modo polling (desarrollo sin ngrok) ──────────────────────────────────────
##async def run_polling():
##    log.info("🤖 Iniciando bot en modo POLLING (desarrollo local)...")
##    app_bot = crear_app(TELEGRAM_TOKEN)
##    await app_bot.run_polling()


##if __name__ == "__main__":
##    if "--polling" in sys.argv:
##        asyncio.run(run_polling())
##    else:
##        import uvicorn
##        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
if __name__ == "__main__":
    if "--polling" in sys.argv:
        log.info("🤖 Iniciando bot en modo POLLING (desarrollo local)...")
        app_bot = crear_app(TELEGRAM_TOKEN)
        app_bot.run_polling()
    else:
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
