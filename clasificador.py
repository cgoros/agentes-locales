"""clasificador.py — Módulo 1.6: agente de un paso con salida JSON estricta.

Entregable del curso "De Cero a Master en LLMs Locales, Agentes y Orquestación
Multiagente". Aplica las cinco partes de un prompt de agente (rol acotado,
herramientas, formato rígido, condición de parada y presupuesto).

Uso:
    python clasificador.py            # una ejecución (imprime el JSON)
    python clasificador.py --test 10  # criterio de éxito: 10/10 JSON válido
"""

import argparse
import json
import sys

import ollama

MODELO = "qwen3.5:9b"

SYSTEM = """Eres un clasificador de tickets de soporte. Recibes el texto de una incidencia.
Devuelve EXCLUSIVAMENTE un JSON válido con esta forma:
{"categoria": "...", "urgencia": "...", "estado": "...", "comentario": "..."}

categoria, EXACTAMENTE uno de: hardware, software, red, facturacion, cuenta de usuario, otro.
"otro" es el ULTIMO recurso: usalo SOLO si ninguna otra categoria encaja. Si hay pistas de
hardware, software, red, facturacion o cuenta de usuario, elige esa. Cambiar datos de la
cuenta (nombre, foto, contrasena, correo) es "cuenta de usuario", nunca "otro".

urgencia, EXACTAMENTE uno de:
- alta: servicio caído, pérdida de dinero o de datos, riesgo de seguridad.
- media: puedo seguir trabajando, pero con molestias.
- baja: consulta, duda o mejora.
- nula: SOLO si estado no es "ok".

estado, EXACTAMENTE uno de:
- ok: hay datos suficientes para clasificar.
- insuficiente: es una incidencia, pero falta información para clasificarla.
- no_ticket: el texto no es una incidencia de soporte.

comentario: máximo 2 líneas, en español. Si estado no es "ok", explica qué falta o por qué no es una incidencia.

Reglas de coherencia:
- Si estado no es "ok", entonces categoria="otro" y urgencia="nula".
- Nunca devuelvas claves distintas a: categoria, urgencia, estado, comentario.
No añadas explicaciones, markdown ni texto fuera del JSON.
Presupuesto: una sola respuesta."""

CATEGORIA = {"hardware", "software", "red", "facturacion", "cuenta de usuario", "otro"}
URGENCIAS = {"alta", "media", "baja", "nula"}
ESTADOS = {"ok", "insuficiente", "no_ticket"}
CLAVES_OK = {"categoria", "urgencia", "estado", "comentario"}


def resumir(texto: str, temperature: float = 0.1) -> dict:
    resp = ollama.chat(
        model=MODELO,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": texto},
        ],
        format="json",  # fuerza JSON válido
        think=False,  # Qwen3: sin razonamiento interno (mucho más rápido)
        options={
            "temperature": temperature,
            "num_predict": 300,  # presupuesto: corta la generación
        },
    )
    return json.loads(resp["message"]["content"])


def validar(dato) -> dict:
    """Verificación determinista: dict con el esquema esperado (o el error pactado)."""

    if not isinstance(dato, dict):
        raise ValueError(f"se esperaba un objeto JSON, llegó {type(dato).__name__}")
    if set(dato) != CLAVES_OK:
        raise ValueError(f"claves incorrectas: {sorted(dato)}; esperaba {sorted(CLAVES_OK)}")
    if dato["estado"] not in ESTADOS:
        raise ValueError(f"estado no permitido: {dato['estado']!r}; esperaba {sorted(ESTADOS)}")  
    if dato["urgencia"] not in URGENCIAS:
        raise ValueError(f"urgencia no permitida: {dato['urgencia']!r}; esperaba {sorted(URGENCIAS )}")
    if dato["categoria"] not in CATEGORIA:
        raise ValueError(f"categoria no permitida: {dato['categoria']!r}; esperaba {sorted(CATEGORIA)}")
       
        # La regla de coherencia del prompt, aplicada en código:
    if dato["estado"] != "ok" and (dato["categoria"] != "otro" or dato["urgencia"] != "nula"):
        raise ValueError(
            f"incoherente: estado={dato['estado']!r} exige 'otro'/'nula'; "
            f"llegó {dato['categoria']!r}/{dato['urgencia']!r}"
        )
    comentario = dato["comentario"]
    if not isinstance(comentario, str):
        raise ValueError(f"comentario debe ser texto, llegó {type(comentario).__name__}")
    if not comentario.strip():
        raise ValueError("comentario vacío")
    if len(comentario.splitlines()) > 2:
        raise ValueError(f"comentario de {len(comentario.splitlines())} líneas; máximo 2")
    return dato


def main() -> int:
    parser = argparse.ArgumentParser(description="Agente de clasificación (JSON estricto).")
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
