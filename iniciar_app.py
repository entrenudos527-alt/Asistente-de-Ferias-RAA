"""
Lanzador local de la aplicación Asistente de Eventos RAA.

Arranca el servidor Flask en 127.0.0.1:5000 y abre el navegador
solo cuando el servidor ya está respondiendo (evita la página
"No se puede acceder a este sitio" al abrir demasiado pronto).
"""

import socket
import threading
import time
import webbrowser

from app import create_app

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}/inicio"


def _puerto_abierto() -> bool:
    try:
        with socket.create_connection((HOST, PORT), timeout=0.5):
            return True
    except OSError:
        return False


def _abrir_navegador_cuando_este_listo() -> None:
    """Espera hasta 30 segundos a que el servidor acepte conexiones."""
    for _ in range(60):
        if _puerto_abierto():
            webbrowser.open(URL)
            return
        time.sleep(0.5)


def main() -> None:
    if _puerto_abierto():
        print(f"El servidor ya está corriendo. Abriendo {URL}")
        webbrowser.open(URL)
        return

    app = create_app()

    threading.Thread(target=_abrir_navegador_cuando_este_listo, daemon=True).start()

    print("=" * 60)
    print("  Asistente de Eventos RAA — servidor local")
    print(f"  Dirección: {URL}")
    print("  Para detener el servidor: cerrá esta ventana o Ctrl + C")
    print("=" * 60)

    # use_reloader=False para no abrir dos procesos ni el navegador dos veces.
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
