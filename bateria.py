"""bateria.py — pasa varios tickets por el clasificador y enseña la tabla."""
from clasificador import resumir, validar

CASOS = [
    "no he recibido la factura de mi servicio de internet este mes.",
    "no me llegan los correos.",
    "Olvidé la contraseña de mi cuenta de correo electrónico y no se abre el editor de texto.",
    "no va.",
    "Tengo un software de ultimo modelo que cuando arranca hace que se puedan hacer cosas, aunque algunas de las cosas que hace no se por qué las hace y no tengo ni idea de si esto puede ser porque lo estoy haciendo bien o mal, o si el software es bueno o me han engañado como a un chino.",
    "cuando pueda, me gustaría cambiar mi foto de perfil."
    # ← AQUÍ VA TU TRABAJO: 6 tickets, uno por línea   
]

for i, caso in enumerate(CASOS, 1):
    try:
        d = validar(resumir(caso))
        print(f"[{i}] {d['estado']:12} {d['categoria']:18} {d['urgencia']:6} | {caso[:40]}")

    except ValueError as exc:
        print(f"[{i}] FALLO: {exc} | {caso[:45]}")
