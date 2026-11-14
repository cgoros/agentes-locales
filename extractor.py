"""extractor.py — 1.6: extractor de entidades (el primer JSON con listas)."""
import argparse
import json
import re

import ollama

MODELO = "qwen3.5:9b"

SYSTEM = """Eres un extractor de entidades. Recibes un texto y devuelves SOLO las entidades que aparecen en él.
Devuelve EXCLUSIVAMENTE un JSON válido con esta forma:
{"personas": ["..."], "lugares": ["..."], "fechas": ["..."]}

Reglas:
- Las tres claves son OBLIGATORIAS y siempre contienen listas. Si no hay entidades de un tipo, devuelve [].
- Copia cada entidad tal como aparece en el texto. No traduzcas, no corrijas, no completes nombres.
- No inventes entidades que no estén en el texto.
- "personas" son personas (nombres de gente); "lugares" son ciudades, países o sitios.
- fechas: normaliza a ISO 8601, "AAAA-MM-DD" o "AAAA-MM" si no hay día. Si la fecha es relativa
  ("el martes pasado", "la próxima semana") y el texto no da la fecha de referencia, NO la incluyas.
- Máximo 10 elementos por lista, sin repetidos.
No añadas explicaciones, markdown ni texto fuera del JSON."""

# MUESTRA = ("El 15 de marzo de 2024, Marta Ruiz se reunió en Berlín con Karl Weber y Ana López. ". "La próxima semana volverá a Valencia.")
# MUESTRA = ("cuando el rio suena, agua lleva.")
# MUESTRA = ("el martes pasado me llamó Lucía")
# MUESTRA = ("Juan llamó; después Juan escribió")
MUESTRA = ("Ayer estuve en el mercado central de Bogotá")

CLAVES = {"personas", "lugares", "fechas"}
RE_FECHA = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")


def extraer(texto: str, temperature: float = 0.1) -> dict:
    resp = ollama.chat(
        model=MODELO,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": texto},
        ],
        format="json",
        think=False,
        options={"temperature": temperature, "num_predict": 400},
    )
    return json.loads(resp["message"]["content"])


def validar(dato) -> dict:
    if not isinstance(dato, dict):
        raise ValueError(f"se esperaba un objeto JSON, llegó {type(dato).__name__}")
    if set(dato) != CLAVES:
        raise ValueError(f"claves incorrectas: {sorted(dato)}; esperaba {sorted(CLAVES)}")

    for clave in sorted(CLAVES):
        lista = dato[clave]
        if not isinstance(lista, list):
            raise ValueError(f"{clave} debe ser una lista, llegó {type(lista).__name__}")
        for valor in lista:
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(f"{clave}: elemento vacío o no textual: {valor!r}")
        if len(set(lista)) != len(lista):
            raise ValueError(f"{clave}: hay elementos repetidos: {lista}")

    for fecha in dato["fechas"]:
        if not RE_FECHA.fullmatch(fecha):
            raise ValueError(f"fecha no normalizada: {fecha!r}; esperaba AAAA-MM o AAAA-MM-DD")
    return dato


def main() -> int:
    parser = argparse.ArgumentParser(description="Extractor de entidades (JSON estricto).")
    parser.add_argument("--test", type=int, default=0, metavar="N")
    args = parser.parse_args()

    if args.test <= 0:
        print(json.dumps(validar(extraer(MUESTRA)), ensure_ascii=False, indent=2))
        return 0

    aciertos = 0
    for i in range(1, args.test + 1):
        try:
            dato = validar(extraer(MUESTRA))
            aciertos += 1
            print(f"[{i}/{args.test}] OK    {dato}")
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"[{i}/{args.test}] FALLO {type(exc).__name__}: {exc}")
    print(f"\nResultado: {aciertos}/{args.test} JSON válido")
    return 0 if aciertos == args.test else 1


if __name__ == "__main__":
    raise SystemExit(main())
