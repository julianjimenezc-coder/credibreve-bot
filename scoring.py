"""
Motor de Scoring Crediticio
Herramienta anti gota-a-gota — inclusión financiera preventiva
Puntuación máxima: 100 puntos
"""

def calcular_score(perfil: dict) -> dict:
    score = 0
    alertas = []
    detalles = {}

    ingresos = float(perfil.get("ingreso_mensual", 0))
    gastos   = float(perfil.get("gastos_fijos", 0))
    deudas   = float(perfil.get("deuda_mensual_total", 0))

    # ── 1. DTI — Debt-to-Income ratio (30 pts) ─────────────────────────────
    if ingresos > 0:
        dti = (deudas + gastos) / ingresos
    else:
        dti = 1.0

    if dti < 0.30:
        pts = 30
    elif dti < 0.50:
        pts = 18
    elif dti < 0.70:
        pts = 8
    else:
        pts = 0
        alertas.append("🚨 Endeudamiento crítico: más del 70% del ingreso comprometido")

    score += pts
    detalles["dti"] = {"valor": round(dti * 100, 1), "puntos": pts, "maximo": 30}

    # ── 2. Estabilidad de ingreso (25 pts) ─────────────────────────────────
    tipo = perfil.get("tipo_ingreso", "desconocido").lower()
    mapa_tipo = {
        "formal":       25,
        "semiformal":   16,
        "informal":     8,
        "desconocido":  0,
    }
    pts = mapa_tipo.get(tipo, 0)
    if pts == 0:
        alertas.append("⚠️ Ingreso no verificable o inexistente")
    score += pts
    detalles["ingreso"] = {"tipo": tipo, "puntos": pts, "maximo": 25}

    # ── 3. Propósito del crédito (20 pts) ──────────────────────────────────
    proposito = perfil.get("proposito", "otro").lower()
    mapa_proposito = {
        "negocio":         20,
        "capital_trabajo": 20,
        "educacion":       18,
        "salud":           16,
        "consumo":         8,
        "otro":            4,
        "pago_deuda":      2,
    }
    pts = mapa_proposito.get(proposito, 4)
    if proposito == "pago_deuda":
        alertas.append("⚠️ Pagar deudas con más deuda es una señal de trampa financiera")
    score += pts
    detalles["proposito"] = {"valor": proposito, "puntos": pts, "maximo": 20}

    # ── 4. Sin préstamo gota a gota activo (15 pts) ─────────────────────────
    tiene_informal = perfil.get("tiene_prestamo_informal", False)
    if not tiene_informal:
        pts = 15
    else:
        pts = 0
        alertas.append("🚨 ALERTA CRÍTICA: Préstamo informal activo (gota a gota). Riesgo muy alto de trampa de deuda.")
    score += pts
    detalles["gota_a_gota"] = {"activo": tiene_informal, "puntos": pts, "maximo": 15}

    # ── 5. Historial de pago (10 pts) ───────────────────────────────────────
    historial = perfil.get("historial_pago", "desconocido").lower()
    mapa_historial = {
        "bueno":       10,
        "regular":     5,
        "malo":        0,
        "desconocido": 3,
    }
    pts = mapa_historial.get(historial, 3)
    if historial == "malo":
        alertas.append("⚠️ Historial de pago negativo detectado")
    score += pts
    detalles["historial"] = {"valor": historial, "puntos": pts, "maximo": 10}

    # ── Banda de riesgo ─────────────────────────────────────────────────────
    if score >= 70:
        banda   = "VIABLE"
        emoji   = "✅"
        mensaje = "Capacidad de pago saludable"
    elif score >= 40:
        banda   = "RIESGO_MODERADO"
        emoji   = "⚠️"
        mensaje = "Capacidad de pago limitada"
    else:
        banda   = "PELIGRO"
        emoji   = "🔴"
        mensaje = "Alto riesgo de sobreendeudamiento"

    return {
        "score":    score,
        "banda":    banda,
        "emoji":    emoji,
        "mensaje":  mensaje,
        "alertas":  alertas,
        "detalles": detalles,
    }


def resumen_score(resultado: dict) -> str:
    """Genera texto corto del score para enviar al LLM."""
    lines = [
        f"Score: {resultado['score']}/100",
        f"Banda: {resultado['banda']}",
        f"Alertas: {'; '.join(resultado['alertas']) if resultado['alertas'] else 'Ninguna'}",
        "Detalles por variable:",
    ]
    for k, v in resultado["detalles"].items():
        lines.append(f"  - {k}: {v['puntos']}/{v['maximo']} pts")
    return "\n".join(lines)
