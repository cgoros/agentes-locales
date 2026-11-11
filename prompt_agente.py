"""prompt_agente.py — Módulo 1.6: agente de un paso con salida JSON estricta.

Entregable del curso "De Cero a Master en LLMs Locales, Agentes y Orquestación
Multiagente". Aplica las cinco partes de un prompt de agente (rol acotado,
herramientas, formato rígido, condición de parada y presupuesto).

Uso:
    python prompt_agente.py            # una ejecución (imprime el JSON)
    python prompt_agente.py --test 10  # criterio de éxito: 10/10 JSON válido
"""

import argparse
import json
import sys

import ollama

MODELO = "qwen3.5:9b"

SYSTEM = """Eres un agente de resumen. Recibes el contenido de un archivo de texto.
Debes devolver EXCLUSIVAMENTE un JSON válido con esta forma:
{"resumen": "<3 líneas>", "palabras_clave": ["...", "..."]}
No añadas explicaciones, markdown ni texto fuera del JSON.
Si el texto tiene menos de 10 palabras, devuelve {"error": "texto demasiado corto"}.
Presupuesto: una sola respuesta, sin pasos adicionales."""

MUESTRA = "Los agentes locales permiten automatizar tareas sin enviar datos a la nube. " * 5

CLAVES_OK = {"resumen", "palabras_clave"}


def resumir(texto: str) -> dict:
    resp = ollama.chat(
        model=MODELO,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": texto},
        ],
        format="json",  # fuerza JSON válido
        think=False,  # Qwen3: sin razonamiento interno (mucho más rápido)
        options={
            "temperature": 0.1,
            "num_predict": 300,  # presupuesto: corta la generación
        },
    )
    return json.loads(resp["message"]["content"])


def validar(dato) -> dict:
    """Verificación determinista: dict con el esquema esperado (o el error pactado)."""
    if not isinstance(dato, dict):
        raise ValueError(f"se esperaba un objeto JSON, llegó {type(dato).__name__}")
    if not (CLAVES_OK <= set(dato) or "error" in dato):
        raise ValueError(f"claves inesperadas: {sorted(dato)}")
    return dato


def main() -> int:
    parser = argparse.ArgumentParser(description="Agente de resumen (JSON estricto).")
    parser.add_argument(
        "--test",
        type=int,
        default=0,
        metavar="N",
        help="ejecuta N veces y valida el JSON (criterio de éxito 10/10)",
    )
    args = parser.parse_args()

    if args.test <= 0:
        print(json.dumps(validar(resumir(MUESTRA)), ensure_ascii=False, indent=2))
        return 0

    aciertos = 0
    for i in range(1, args.test + 1):
        try:
            dato = validar(resumir(MUESTRA))
            aciertos += 1
            print(f"[{i}/{args.test}] OK    claves={sorted(dato)}")
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"[{i}/{args.test}] FALLO {type(exc).__name__}: {exc}")

    print(f"\nResultado: {aciertos}/{args.test} JSON válido")
    return 0 if aciertos == args.test else 1


if __name__ == "__main__":
    sys.exit(main())
