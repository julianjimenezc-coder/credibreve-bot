# 🛡️ CrediBreve Bot — Inclusión Financiera Preventiva

> **Herramienta anti gota-a-gota** · Análisis de capacidad de pago vía Telegram con IA Generativa

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4.svg)](https://core.telegram.org/bots)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991.svg)](https://openai.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/Licencia-MIT-green.svg)](LICENSE)

---

## 🎯 El Problema

En Colombia, **más de 3 millones de personas** recurren al *gota a gota* — préstamos informales con tasas equivalentes al **200% – 400% anual**. No por ignorancia, sino porque:

- Los bancos formales son lentos, excluyentes y burocráticos
- El prestamista informal está en el barrio, es rápido y no pide papeles
- **No existe una barrera preventiva** que evalúe la capacidad de pago antes de caer en la trampa

## 💡 La Solución

**CrediBreve** convierte Telegram — una app que millones ya usan — en una herramienta de inclusión financiera preventiva.

En **3 mensajes de chat**, el sistema:

1. Recopila el perfil financiero del usuario en lenguaje natural
2. Usa IA (GPT-4o-mini) para extraer y normalizar los datos
3. Calcula un **score de capacidad de pago** (0–100 puntos)
4. Detecta si el usuario ya está en una trampa de gota a gota
5. Entrega una explicación empática y un paso concreto a tomar

> **No es un chatbot financiero. Es una barrera preventiva contra la usura.**

---

## 🏗️ Arquitectura

```
Usuario (Telegram)
       │
       ▼
  Telegram Bot
       │
       ▼
  Backend Python (FastAPI)
       │
       ├──▶ LLM (OpenAI GPT-4o-mini)
       │         │
       │         ├── Extracción de datos del lenguaje natural
       │         ├── Construcción del perfil financiero (JSON)
       │         └── Generación de explicación humanizada
       │
       └──▶ Motor de Scoring (reglas + pesos)
                 │
                 ├── DTI — Deuda/Ingreso          (30 pts)
                 ├── Estabilidad de ingreso        (25 pts)
                 ├── Propósito del crédito         (20 pts)
                 ├── Sin préstamo informal activo  (15 pts)
                 └── Historial de pago             (10 pts)
                               │
                               ▼
                    Score final 0–100 pts
                    ✅ VIABLE · ⚠️ RIESGO · 🔴 PELIGRO
```

---

## 📊 Motor de Scoring

| Variable | Peso | Descripción |
|---|---|---|
| DTI (deuda/ingreso) | 30 pts | Porcentaje del ingreso comprometido en deudas |
| Estabilidad de ingreso | 25 pts | Formal / Semiformal / Informal |
| Propósito del crédito | 20 pts | Productivo vs consumo vs pago de deuda |
| Sin gota a gota activo | 15 pts | Detección de préstamo informal vigente |
| Historial de pago | 10 pts | Comportamiento de pago pasado |

### Bandas de resultado

| Puntaje | Banda | Acción |
|---|---|---|
| 70 – 100 | ✅ VIABLE | Derivar a microfinanciera formal |
| 40 – 69 | ⚠️ RIESGO MODERADO | Plan de educación financiera |
| 0 – 39 | 🔴 PELIGRO | Alerta + recursos de ayuda |

---

## 🚀 Cómo ejecutar el proyecto

### Requisitos previos

- Python 3.12+
- Token de Telegram ([@BotFather](https://t.me/botfather))
- API Key de OpenAI ([platform.openai.com](https://platform.openai.com/api-keys))

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/credibreve-bot.git
cd credibreve-bot

# 2. Crear entorno virtual
python3 -m venv myenv
source myenv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
nano .env  # Agrega tus tokens aquí
```

### Configurar `.env`

```env
TELEGRAM_TOKEN=aqui_va_tu_token_del_bot
OPENAI_API_KEY=aqui_va_tu_api_key_de_openai
```

### Ejecutar

```bash
# Modo desarrollo (polling) — sin necesidad de dominio
python main.py --polling

# Modo producción (webhook) — requiere URL pública HTTPS
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Probar el motor de scoring (sin tokens)

```bash
python test_scoring.py
```

---

## 💬 Flujo de conversación

```
Usuario: /start

Bot: ¡Hola! En 3 preguntas te digo si un crédito es seguro para ti 🛡️
     ¿Cuánto ganas aproximadamente al mes?

Usuario: Gano como un millón doscientos vendiendo empanadas

Bot: ¿Cuánto gastas fijo al mes? ¿Tienes deudas ahora?
     ¿Cuántas personas dependen de ti?

Usuario: Gasto 500 mil, le debo a un señor que cobra cada semana,
         tengo 3 hijos

Bot: ¿Para qué necesitas el crédito?
     ¿Alguien te cobra a diario o semanal ahora mismo?

Usuario: Para pagar lo que debo, sí me cobran diario

Bot: 📊 Tu análisis de capacidad de pago
     🟥⬜⬜⬜⬜⬜⬜⬜⬜⬜
     Puntaje: 12/100 🔴

     [Explicación empática en lenguaje simple]

     🚨 ALERTA: Préstamo informal activo detectado
     🆘 ¿Qué debes hacer HOY?
     • No tomes ningún crédito nuevo
     • Llama a la SFC: 01 8000 120 100 (gratuito)
```

---

## 📁 Estructura del proyecto

```
credibreve-bot/
├── main.py           ← Punto de entrada (FastAPI + polling)
├── bot.py            ← Flujo conversacional de 3 turnos
├── llm.py            ← Integración OpenAI (extracción + explicación)
├── scoring.py        ← Motor de scoring 100 puntos
├── test_scoring.py   ← Pruebas del motor sin dependencias externas
├── .env.example      ← Plantilla de variables de entorno
├── requirements.txt  ← Dependencias del proyecto
└── .gitignore        ← Protección de tokens y archivos sensibles
```

---

## 🛠️ Stack tecnológico

| Tecnología | Uso |
|---|---|
| Python 3.12 | Lenguaje principal |
| FastAPI | Backend y webhook |
| python-telegram-bot | Integración con Telegram API |
| OpenAI GPT-4o-mini | Extracción de perfil + explicación humanizada |
| Systemd / Screen | Ejecución permanente en servidor |

**Costo por análisis:** < $0.001 USD · **Canal:** Telegram (gratuito, sin app nueva)

---

## 📈 Impacto esperado

- **Población objetivo:** 3+ millones de colombianos vulnerables al gota a gota
- **Barrera de entrada:** cero — solo necesitan Telegram
- **Costo por usuario:** prácticamente nulo
- **Escalabilidad:** un solo servidor atiende miles de consultas diarias
- **Marco legal:** alineado con Ley 1581 de 2012 (Habeas Data) y regulación SFC

---

## 👥 Equipo

| Nombre |
|---|
| [Elizabeth Cristina Vásquez Estrada ] | 
| [Adriana Lucía Cadavid Tabares ] |
| [Sandra Milena González Echeverri ] |
| [Sebastián Pineda Carrillo] |
| [Julián Ricardo Jiménez Carvajal ] |
---

## 📄 Licencia

MIT License — libre uso, modificación y distribución.

---

> *"No somos un chatbot financiero. Somos una barrera preventiva contra la usura."*
