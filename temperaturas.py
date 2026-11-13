"""temperaturas.py — 1.6: el mismo clasificador a 0.1 y a 0.9."""
from clasificador import resumir, validar

CASOS = [
    "no he recibido la factura de mi servicio de internet este mes.",
    "no me llegan los correos.",
    "Olvidé la contraseña de mi cuenta de correo electrónico.",
    "no va.",
    "cuando pueda, me gustaría cambiar mi foto de perfil.",
    "La luna esta hecha de queso y brilla mucho por la noche.",
]
TIRADAS = 3

for temp in (0.1, 0.9):
    print(f"\n=== temperature = {temp} ===")
    fallos = 0
    inestables = 0
    comentarios = set()
    for caso in CASOS:
        etiquetas = set()
        for _ in range(TIRADAS):
            try:
                d = validar(resumir(caso, temperature=temp))
            except ValueError:
                fallos += 1
                continue
            etiquetas.add((d["categoria"], d["urgencia"], d["estado"]))
            comentarios.add(d["comentario"])
        if len(etiquetas) > 1:
            inestables += 1
        print(f"  {len(etiquetas)} etiqueta(s) | {caso[:38]}")
    print(
        f"  -> inestables: {inestables}/{len(CASOS)}"
        f" | comentarios distintos: {len(comentarios)}"
        f" | fallos de validación: {fallos}"
    )
