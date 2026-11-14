"""corrector.py — 1.6: corrector con restricciones.

Comprobaciones, en orden:
  1. números preservados       4. idempotencia (cuesta 1 llamada extra)
  2. longitud ±20 %            5. nombres propios conservados
  3. coherencia texto/cambios  6. corrige pero no reescribe
"""
import argparse
import json
import re

import ollama

MODELO = "qwen3.5:9b"

SYSTEM = """Eres un corrector de textos en español. Recibes un texto y devuelves SOLO su versión corregida.
Devuelve EXCLUSIVAMENTE un JSON válido con esta forma:
{"texto": "<texto corregido>", "cambios": ["<descripción breve de cada corrección>"]}

Reglas:
- Corrige SOLO ortografía, gramática y puntuación. No mejores el estilo.
- No cambies el significado, el orden de las ideas ni añadas información nueva.
- No toques nombres propios, cifras, fechas, horas, siglas ni URLs.
- Mismo idioma y mismo registro.
- Si una palabra no existe en español, y caben varias correcciones posibles, NO la corrijas. Déjala tal cual y descríbela en "cambios".
- Si el texto no tiene errores, devuelve "texto" IDÉNTICO al original y "cambios": [].
- "cambios" es una lista de strings cortos, máximo 10. Si no hay cambios, [].
No añadas explicaciones, markdown ni texto fuera del JSON."""

def levenshtein(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def verificar_reescritura(entrada: str, salida: str, maximo: int = 2) -> None:
    """6. Corregir, no reescribir: cada palabra nueva debe parecerse a alguna del original."""
    base = [p.lower() for p in re.findall(r"[^\W\d_]+", entrada)]
    if not base:
        return  # texto sin palabras (solo cifras o signos): no hay nada que comparar
    conocidas = set(base)
    fusiones = {base[i] + base[i + 1] for i in range(len(base) - 1)}
    for palabra in re.findall(r"[^\W\d_]+", salida):
        p = palabra.lower()
        if p in conocidas:
            continue
        if p in fusiones:
            raise ValueError(f"inv 6 (reescritura): {palabra!r} une dos palabras del original")
        cerca = min(base, key=lambda b: levenshtein(p, b))
        distancia = levenshtein(p, cerca)
        if distancia > maximo:
            raise ValueError(
                f"inv 6 (reescritura): {palabra!r} no se parece a nada del original "
                f"(lo más cercano {cerca!r}, distancia {distancia})"
            )


MUESTRA = (
    "Abía mucha jente aller en el mercado. "
    "La próxima semana volverá a Valencia. "
    "el próximo viernes ya no será viernes 13 de noviembre. "
    "me llamo Carlos y estoy aprendiendo con mi curso de prompting de "
    "LLMs locales, agentes y orquestación multiagente."
)

CLAVES = {"texto", "cambios"}
RE_NUMERO = re.compile(r"\d+")


def corregir(texto: str, temperature: float = 0.1) -> dict:
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
    """Forma: dict con 'texto' (str) y 'cambios' (lista de str, máx. 10)."""
    if not isinstance(dato, dict):
        raise ValueError(f"se esperaba un objeto JSON, llegó {type(dato).__name__}")
    if set(dato) != CLAVES:
        raise ValueError(f"claves incorrectas: {sorted(dato)}; esperaba {sorted(CLAVES)}")
    if not isinstance(dato["texto"], str) or not dato["texto"].strip():
        raise ValueError(f"'texto' debe ser texto no vacío, llegó {dato['texto']!r}")
    cambios = dato["cambios"]
    if not isinstance(cambios, list):
        raise ValueError(f"'cambios' debe ser una lista, llegó {type(cambios).__name__}")
    for cambio in cambios:
        if not isinstance(cambio, str) or not cambio.strip():
            raise ValueError(f"'cambios': elemento vacío o no textual: {cambio!r}")
    if len(cambios) > 10:
        raise ValueError(f"'cambios' trae {len(cambios)} elementos; máximo 10")
    return dato


def nombres_propios(texto: str) -> set:
    """Palabras con mayúscula que NO están al inicio de frase."""
    propios = set()
    for frase in re.split(r"[.!?:]+", texto):          # trocea por signos de cierre
        palabras = re.findall(r"[^\W\d_]+", frase)     # solo letras (sin números ni signos)
        for palabra in palabras[1:]:                   # la primera es inicio de frase
            if palabra[:1].isupper():
                propios.add(palabra)
    return propios


def verificar_invariantes(entrada: str, dato: dict) -> None:
    """Propiedades que deben cumplirse SIEMPRE, sin saber el texto de salida."""
    salida, cambios = dato["texto"], dato["cambios"]

    # 1. No inventar ni perder números
    antes, despues = set(RE_NUMERO.findall(entrada)), set(RE_NUMERO.findall(salida))
    if antes != despues:
        raise ValueError(f"inv 1 (números): antes {sorted(antes)}, después {sorted(despues)}")

    # 2. No reescribir: la longitud no puede cambiar más de un 20 %
    if abs(len(salida) - len(entrada)) > 0.2 * len(entrada):
        raise ValueError(f"inv 2 (longitud): {len(entrada)} -> {len(salida)} caracteres")

    # 3. Coherencia texto/cambios: si cambió el texto, hay cambios; si no, lista vacía
    if (salida == entrada) != (cambios == []):
        raise ValueError(
            f"inv 3 (coherencia): texto {'igual' if salida == entrada else 'distinto'} "
            f"pero cambios={cambios}"
        )

    # 5. Los nombres propios no desaparecen (la mayúscula sí puede corregirse)
    en_salida = {p.lower() for p in re.findall(r"[^\W\d_]+", salida)}
    perdidos = {p for p in nombres_propios(entrada) if p.lower() not in en_salida}
    if perdidos:
        raise ValueError(f"inv 5 (nombres propios): desaparecieron {sorted(perdidos)}")

    # 6. ¿Corrige o reescribe?
    verificar_reescritura(entrada, salida)


def verificar_idempotencia(salida: str) -> None:
    """4. Corregir un texto ya corregido no debe producir cambios."""
    segunda = validar(corregir(salida))
    if segunda["cambios"]:
        raise ValueError(
            f"inv 4 (idempotencia): una segunda pasada aún cambia cosas: {segunda['cambios']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Corrector con invariantes.")
    parser.add_argument("--test", type=int, default=0, metavar="N")
    args = parser.parse_args()

    if args.test <= 0:
        try:
            dato = validar(corregir(MUESTRA))
            verificar_invariantes(MUESTRA, dato)
            verificar_idempotencia(dato["texto"])   # el 4, que no puede ir en el bucle
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"FALLO {type(exc).__name__}: {exc}")
            return 1
        print(json.dumps(dato, ensure_ascii=False, indent=2))
        return 0

    aciertos = 0
    for i in range(1, args.test + 1):
        try:
            dato = validar(corregir(MUESTRA))
            verificar_invariantes(MUESTRA, dato)
            aciertos += 1
            print(f"[{i}/{args.test}] OK    {len(dato['cambios'])} cambio(s) | {dato['texto']}")
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"[{i}/{args.test}] FALLO {type(exc).__name__}: {exc}")
    print(f"\nResultado: {aciertos}/{args.test} válido + invariantes")
    return 0 if aciertos == args.test else 1


if __name__ == "__main__":
    raise SystemExit(main())
