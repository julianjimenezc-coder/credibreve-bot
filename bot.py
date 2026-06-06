"""
Bot de Telegram — Flujo conversacional anti gota-a-gota
Estados: START → TURNO_1 → TURNO_2 → TURNO_3 → ANALIZANDO → LISTO
"""

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from llm import extraer_perfil, generar_explicacion
from scoring import calcular_score, resumen_score
import os

# ── Estado en memoria (para MVP — en producción usar Redis o DB) ─────────────
# { chat_id: { "estado": str, "mensajes": [str] } }
sesiones: dict = {}

# ── Mensajes del bot ──────────────────────────────────────────────────────────
BIENVENIDA = """👋 ¡Hola! Soy *CréditoSeguro*, tu asesor financiero gratuito.

En 3 preguntas cortas te digo si un crédito es seguro para ti y si estás en riesgo de caer en el *gota a gota* 🛡️

Todo es confidencial. Vamos a la primera pregunta:

💰 *¿Cuánto ganas aproximadamente al mes?*
_(Puedes decirlo así: "gano un millón", "como 800 mil", "varía entre 600 y 900 mil")_"""

PREGUNTA_2 = """Perfecto, gracias 👍

Ahora cuéntame sobre tus gastos y deudas actuales:

🏠 *¿Cuánto gastas fijo al mes?* (arriendo, servicios, comida, transporte)
💳 *¿Tienes deudas ahora?* Si sí, ¿cuánto pagas al mes por ellas?
👨‍👩‍👧 *¿Cuántas personas dependen de ti economicamente?*

_(Responde todo junto, como puedas)_"""

PREGUNTA_3 = """Entendido ✅

Última pregunta, muy importante:

🎯 *¿Para qué necesitas el crédito?*
_(Negocio, mercancía, salud, educación, pagar otra deuda, consumo...)_

⚠️ *¿Alguien te está cobrando a diario o semanal ahora mismo?*
_(Gota a gota, prestamista del barrio, cobro semanal...)_

📋 *¿Cómo ha sido tu historial de pago en el pasado?*
_(Siempre he pagado / a veces me he atrasado / he tenido problemas)_"""

ANALIZANDO = """🔍 *Analizando tu perfil financiero...*

Un momento, estoy evaluando tu capacidad de pago con inteligencia artificial 🤖"""

# ── Handlers ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sesiones[chat_id] = {"estado": "TURNO_1", "mensajes": []}
    await update.message.reply_text(BIENVENIDA, parse_mode="Markdown")


async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id   = update.effective_chat.id
    texto     = update.message.text

    # Si no hay sesión activa, iniciar automáticamente
    if chat_id not in sesiones:
        sesiones[chat_id] = {"estado": "TURNO_1", "mensajes": []}
        await update.message.reply_text(BIENVENIDA, parse_mode="Markdown")
        return

    sesion = sesiones[chat_id]
    estado = sesion["estado"]

    # Acumular mensajes del usuario para el LLM
    sesion["mensajes"].append(f"Usuario: {texto}")

    if estado == "TURNO_1":
        sesion["estado"] = "TURNO_2"
        await update.message.reply_text(PREGUNTA_2, parse_mode="Markdown")

    elif estado == "TURNO_2":
        sesion["estado"] = "TURNO_3"
        await update.message.reply_text(PREGUNTA_3, parse_mode="Markdown")

    elif estado == "TURNO_3":
        sesion["estado"] = "ANALIZANDO"
        await update.message.reply_text(ANALIZANDO, parse_mode="Markdown")

        try:
            # Construir conversación completa para el LLM
            conversacion = "\n".join(sesion["mensajes"])

            # 1. Extraer perfil con LLM
            perfil = extraer_perfil(conversacion)

            # 2. Calcular score con motor de reglas
            resultado = calcular_score(perfil)

            # 3. Generar explicación humanizada con LLM
            resumen = resumen_score(resultado)
            explicacion = generar_explicacion(resumen, perfil)

            # 4. Construir mensaje final
            mensaje_final = formatear_resultado(resultado, explicacion)

            await update.message.reply_text(mensaje_final, parse_mode="Markdown")

            # Marcar sesión como completada
            sesion["estado"] = "LISTO"

        except Exception as e:
            await update.message.reply_text(
                "😕 Hubo un problema analizando tu información. Escribe /start para intentar de nuevo.",
                parse_mode="Markdown"
            )
            sesion["estado"] = "ERROR"
            print(f"Error en análisis: {e}")

    elif estado == "LISTO":
        await update.message.reply_text(
            "✅ Ya analicé tu perfil. Escribe /start si quieres hacer un nuevo análisis.",
            parse_mode="Markdown"
        )


def formatear_resultado(resultado: dict, explicacion: str) -> str:
    """
    Genera el mensaje final estructurado para Telegram.
    """
    score = resultado["score"]
    banda  = resultado["banda"]
    emoji  = resultado["emoji"]

    # Barra visual de progreso
    barras_llenas = score // 10
    barra = "🟩" * barras_llenas + "⬜" * (10 - barras_llenas)

    # Sección de alertas
    alertas_texto = ""
    if resultado["alertas"]:
        alertas_texto = "\n\n*⚠️ Alertas detectadas:*\n"
        for a in resultado["alertas"]:
            alertas_texto += f"• {a}\n"

    # Próximos pasos según banda
    if banda == "VIABLE":
        proximo_paso = (
            "\n\n*✅ ¿Qué puedes hacer?*\n"
            "• Acércate a una cooperativa o microfinanciera formal\n"
            "• Evita el gota a gota aunque te lo ofrezcan\n"
            "• Pide el crédito por escrito, con contrato"
        )
    elif banda == "RIESGO_MODERADO":
        proximo_paso = (
            "\n\n*🎯 ¿Qué puedes hacer?*\n"
            "• Reduce gastos variables antes de endeudarte más\n"
            "• Busca asesoría en tu alcaldía o banco comunal\n"
            "• No aceptes créditos informales con cobro diario"
        )
    else:
        proximo_paso = (
            "\n\n*🆘 ¿Qué debes hacer HOY?*\n"
            "• No tomes ningún crédito nuevo en este momento\n"
            "• Si ya tienes gota a gota: busca a la Defensoría del Pueblo\n"
            "• Llama a la SFC: 01 8000 120 100 (gratuito)"
        )

    return (
        f"*📊 Tu análisis de capacidad de pago*\n\n"
        f"{barra}\n"
        f"*Puntaje: {score}/100* {emoji}\n\n"
        f"{explicacion}"
        f"{alertas_texto}"
        f"{proximo_paso}\n\n"
        f"_Recuerda: este análisis es orientativo, no un crédito aprobado._\n"
        f"Escribe /start para hacer otro análisis."
    )


def crear_app(token: str) -> Application:
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))
    return app
