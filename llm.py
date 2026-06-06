"""
Módulo LLM — OpenAI GPT-4o-mini
Dos funciones clave:
  1. extraer_perfil()      → convierte conversación en JSON estructurado
  2. generar_explicacion() → genera respuesta empática para el usuario

Cambios v2:
  - System prompts separados del user prompt (mejor control del modelo)
  - Tratamiento de datos movido al system prompt de extracción
  - Nuevo SYSTEM_DATOS: maneja SOLO el flujo de consentimiento
  - Temperatura ajustada por función
"""

import json
import os
from openai import OpenAI


def _get_client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("❌ Falta OPENAI_API_KEY en el archivo .env")
    return OpenAI(api_key=key)


# ── System Prompt 0: Consentimiento de datos (paso previo obligatorio) ───────
SYSTEM_DATOS = """
Eres el asistente virtual de CREDIBREVE. Tu ÚNICO rol en este momento es
gestionar el consentimiento de tratamiento de datos personales.

INSTRUCCIONES ESTRICTAS:
1. Presenta el siguiente mensaje de autorización tal cual, sin modificarlo.
2. Espera la respuesta del usuario.
3. Si el usuario acepta (sí, acepto, ok, claro, dale, etc.): responde ÚNICAMENTE con la palabra ACEPTADO.
4. Si el usuario rechaza o no queda claro: responde ÚNICAMENTE con la palabra RECHAZADO.
5. No hagas nada más. No recolectes datos. No expliques nada adicional.

MENSAJE DE AUTORIZACIÓN:
\"\"\"
Hola 👋 Antes de comenzar necesito tu autorización.

Al continuar, autorizas a *CREDIBREVE* a tratar tus datos personales para:
• Verificar tu identidad
• Evaluar tu solicitud de crédito
• Gestionar los servicios ofrecidos

Tus datos serán protegidos y usados únicamente para las finalidades descritas
en nuestra Política de Tratamiento de Datos Personales 📄
https://drive.google.com/file/d/1DF38Xqt8gmWPo7LB4Vx1OK7wJlapFDhO/view?usp=sharing

¿Aceptas el tratamiento de tus datos personales? (Responde *sí* o *no*)
\"\"\"
"""


# ── System Prompt 1: Extracción de perfil financiero ────────────────────────
SYSTEM_EXTRACCION = """
Eres un asistente financiero especializado en microcréditos e inclusión financiera en Colombia.

CONTEXTO:
- El usuario YA aceptó la política de tratamiento de datos de CREDIBREVE.
- Tu tarea es analizar su conversación y extraer un perfil financiero estructurado.
- Responde ÚNICAMENTE con JSON válido. Sin texto adicional. Sin bloques de código.

CAMPOS A EXTRAER:
{
  "ingreso_mensual": <número COP, 0 si no se menciona>,
  "gastos_fijos": <número COP — suma de arriendo + servicios + comida + transporte>,
  "deuda_mensual_total": <número COP — suma de TODAS las cuotas mensuales activas>,
  "dependientes": <número de personas que dependen económicamente del usuario>,
  "tipo_ingreso": <"formal" | "semiformal" | "informal" | "desconocido">,
  "proposito": <"negocio" | "capital_trabajo" | "educacion" | "salud" | "consumo" | "pago_deuda" | "otro">,
  "tiene_prestamo_informal": <true si menciona gota a gota, paga diario, cobra semanal, prestamista del barrio, chulco — false si no>,
  "historial_pago": <"bueno" | "regular" | "malo" | "desconocido">
}

DEFINICIONES DE tipo_ingreso:
- "formal": empleado con contrato y nómina fija
- "semiformal": independiente con clientes fijos (peluquero, mecánico, etc.)
- "informal": ingresos variables por rebusque, ventas ambulantes, oficios del día

REGLAS DE EXTRACCIÓN:
- Convierte texto a números: "un millón" → 1000000, "500 mil" → 500000
- Si el usuario dice "no sé" o no menciona un campo, usa el valor default del schema
- Para gastos_fijos: suma todos los rubros mencionados; si solo dice el total, úsalo
- Para tiene_prestamo_informal: detecta jerga colombiana (gota a gota, diario, el del barrio, don fulano me presta, etc.)
"""

USER_EXTRACCION = """
Analiza esta conversación y extrae el perfil financiero en JSON:

{conversacion}
"""


# ── System Prompt 2: Explicación humanizada del resultado ───────────────────
SYSTEM_EXPLICACION = """
Eres un asesor financiero empático de CREDIBREVE que ayuda a personas de bajos
ingresos en Colombia a entender su situación crediticia.

PERSONALIDAD:
- Tono cercano, cálido y motivador — como un amigo que sabe de finanzas
- Lenguaje colombiano natural (sin "vosotros", sin tecnicismos)
- Nunca juzgues ni hagas sentir mal al usuario
- Emojis con moderación (máximo 4 en toda la respuesta)

ESTRUCTURA OBLIGATORIA (6 líneas cortas):
1. Resultado en palabras simples (ej: "Tu solicitud tiene riesgo alto 🔴")
2. La razón principal en UNA frase
3. Si hay alerta de gota a gota: explica el peligro concreto para su caso
   Si NO hay alerta: da un dato positivo de su perfil
4. UN paso concreto que puede tomar HOY mismo
5. Una alternativa formal si el riesgo es alto (Bancamía, cooperativas, FGA)
   O un mensaje de siguiente paso si el riesgo es bajo/medio
6. Cierre motivador de máximo 10 palabras

IMPORTANTE: No repitas los números exactos del JSON. Habla en términos cotidianos.
"""

USER_EXPLICACION = """
Genera la explicación para este usuario:

Resultado del análisis de riesgo:
{resumen_score}

Perfil:
- Propósito del crédito: {proposito}
- Tipo de ingreso: {tipo_ingreso}
- Tiene préstamo informal activo: {tiene_informal}
"""


# ── Funciones públicas ───────────────────────────────────────────────────────

def solicitar_consentimiento() -> str:
    """
    Retorna el mensaje de consentimiento formateado para enviarlo al usuario.
    Llama a esta función ANTES de cualquier recolección de datos.
    """
    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=300,
        temperature=0.0,  # determinista: siempre el mismo mensaje
        messages=[
            {"role": "system", "content": SYSTEM_DATOS},
            {"role": "user", "content": "Inicia el proceso de autorización."}
        ]
    )
    return response.choices[0].message.content.strip()


def verificar_consentimiento(respuesta_usuario: str) -> bool:
    """
    Evalúa si la respuesta del usuario es una aceptación del tratamiento de datos.
    Retorna True si aceptó, False si rechazó o no fue claro.
    """
    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=10,
        temperature=0.0,
        messages=[
            {"role": "system", "content": SYSTEM_DATOS},
            {"role": "user", "content": respuesta_usuario}
        ]
    )
    resultado = response.choices[0].message.content.strip().upper()
    return resultado == "ACEPTADO"


def extraer_perfil(conversacion: str) -> dict:
    """
    Llama al LLM para convertir la conversación en un perfil financiero JSON.
    PRECONDICIÓN: el usuario ya aceptó el tratamiento de datos.
    Retorna dict con los campos del perfil.
    """
    _perfil_vacio = {
        "ingreso_mensual": 0,
        "gastos_fijos": 0,
        "deuda_mensual_total": 0,
        "dependientes": 0,
        "tipo_ingreso": "desconocido",
        "proposito": "otro",
        "tiene_prestamo_informal": False,
        "historial_pago": "desconocido",
    }

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=500,
            temperature=0.1,  # bajo para consistencia en extracción
            messages=[
                {"role": "system", "content": SYSTEM_EXTRACCION},
                {"role": "user", "content": USER_EXTRACCION.format(conversacion=conversacion)}
            ]
        )
        texto = response.choices[0].message.content.strip()
        # Limpieza defensiva por si el modelo añade backticks
        texto = texto.replace("```json", "").replace("```", "").strip()
        return json.loads(texto)

    except json.JSONDecodeError:
        # Fallback: perfil vacío que generará score bajo y alertas
        return _perfil_vacio

    except Exception as e:
        raise RuntimeError(f"Error llamando a OpenAI en extraer_perfil(): {e}")


def generar_explicacion(resumen_score: str, perfil: dict) -> str:
    """
    Genera la explicación humanizada del resultado para enviar al usuario.
    PRECONDICIÓN: el usuario ya aceptó el tratamiento de datos.
    """
    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=350,
        temperature=0.7,  # más creativo para respuestas empáticas
        messages=[
            {"role": "system", "content": SYSTEM_EXPLICACION},
            {
                "role": "user",
                "content": USER_EXPLICACION.format(
                    resumen_score=resumen_score,
                    proposito=perfil.get("proposito", "no especificado"),
                    tipo_ingreso=perfil.get("tipo_ingreso", "desconocido"),
                    tiene_informal=perfil.get("tiene_prestamo_informal", False),
                )
            }
        ]
    )
    return response.choices[0].message.content.strip()