"""
test_scoring.py — Prueba el motor de scoring de forma aislada
Ejecutar: python test_scoring.py
No requiere Telegram ni OpenAI — perfecto para verificar la lógica en 2 minutos
"""

from scoring import calcular_score, resumen_score

casos = [
    {
        "nombre": "✅ CASO VERDE — Vendedor con negocio estable",
        "perfil": {
            "ingreso_mensual": 2_500_000,
            "gastos_fijos": 800_000,
            "deuda_mensual_total": 150_000,
            "dependientes": 2,
            "tipo_ingreso": "semiformal",
            "proposito": "capital_trabajo",
            "tiene_prestamo_informal": False,
            "historial_pago": "bueno",
        }
    },
    {
        "nombre": "⚠️  CASO AMARILLO — Empleado con deudas medianas",
        "perfil": {
            "ingreso_mensual": 1_800_000,
            "gastos_fijos": 900_000,
            "deuda_mensual_total": 400_000,
            "dependientes": 3,
            "tipo_ingreso": "formal",
            "proposito": "consumo",
            "tiene_prestamo_informal": False,
            "historial_pago": "regular",
        }
    },
    {
        "nombre": "🔴 CASO ROJO — Víctima activa del gota a gota",
        "perfil": {
            "ingreso_mensual": 900_000,
            "gastos_fijos": 600_000,
            "deuda_mensual_total": 350_000,
            "dependientes": 4,
            "tipo_ingreso": "informal",
            "proposito": "pago_deuda",
            "tiene_prestamo_informal": True,
            "historial_pago": "malo",
        }
    },
]

print("=" * 60)
print("  MOTOR DE SCORING — CréditoSeguro MVP")
print("  Herramienta anti gota-a-gota")
print("=" * 60)

for caso in casos:
    print(f"\n{caso['nombre']}")
    print("-" * 50)
    resultado = calcular_score(caso["perfil"])
    print(resumen_score(resultado))
    if resultado["alertas"]:
        print("\nAlertas:")
        for a in resultado["alertas"]:
            print(f"  {a}")
    print(f"\n→ RESULTADO: {resultado['emoji']} {resultado['banda']} ({resultado['score']}/100)")

print("\n" + "=" * 60)
print("✅ Motor de scoring funcionando correctamente")
