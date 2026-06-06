import os
from dotenv import load_dotenv
load_dotenv()

from llm import extraer_perfil, generar_explicacion
from scoring import calcular_score, resumen_score

# Simula lo que diría un usuario real en Telegram
conversacion_test = """
Usuario: Gano como un millón doscientos mil al mes vendiendo empanadas
Usuario: Gasto 500 mil en arriendo y mercado, tengo una deuda de 200 mil al mes
         con un señor que me cobra cada semana, tengo 3 hijos
Usuario: Necesito plata para comprar más ingredientes, ya le debo al del barrio
         desde hace 3 meses y a veces no puedo pagar a tiempo
"""

print("Extrayendo perfil con LLM...")
perfil = extraer_perfil(conversacion_test)
print("Perfil extraído:")
for k, v in perfil.items():
    print(f"  {k}: {v}")

print("\nCalculando score...")
resultado = calcular_score(perfil)
resumen = resumen_score(resultado)
print(resumen)

print("\nGenerando explicación humanizada...")
explicacion = generar_explicacion(resumen, perfil)
print("\n--- MENSAJE FINAL AL USUARIO ---")
print(explicacion)
