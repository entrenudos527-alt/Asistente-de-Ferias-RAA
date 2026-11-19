"""
Utilidades de seguridad de la aplicación.

- Carga de la cuenta autenticada a partir de la sesión.
- Token CSRF para todos los formularios y las peticiones JSON.
- Decorador de permisos para las rutas de administración.

La sesión firmada de Flask guarda solo el identificador de la cuenta y
un token aleatorio. Ese token también se guarda en la base; si la cuenta
se desactiva, se restablece la contraseña o se cierra sesión, el token
deja de coincidir y la sesión queda inválida.
"""

import secrets
from functools import wraps

from flask import abort, g, session

# Rutas que no requieren sesión
ENDPOINTS_PUBLICOS = {"login", "static", "salud"}

# Ruta a la que se redirige cuando hay que cambiar la contraseña temporal
ENDPOINTS_CAMBIO_OBLIGATORIO = {"cambiar_contrasena", "logout", "static"}


def obtener_csrf_token() -> str:
    """Devuelve el token CSRF de la sesión, creándolo si aún no existe."""
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def csrf_valido(token_enviado: str) -> bool:
    """Compara el token enviado con el de la sesión en tiempo constante."""
    token_sesion = session.get("csrf_token")
    if not token_sesion or not token_enviado:
        return False
    return secrets.compare_digest(str(token_enviado), str(token_sesion))


def cargar_usuario_en_contexto(obtener_usuario_por_id):
    """
    Coloca la cuenta autenticada en g.usuario y valida el token de sesión.

    Devuelve la cuenta o None. Si la sesión no es válida, la limpia.
    """
    usuario_id = session.get("usuario_id")
    token_sesion = session.get("token_sesion")

    if not usuario_id or not token_sesion:
        return None

    usuario = obtener_usuario_por_id(usuario_id)

    if usuario is None or not bool(usuario["activo"]):
        session.clear()
        return None

    token_guardado = usuario["token_sesion"]
    if not token_guardado or not secrets.compare_digest(
        str(token_sesion), str(token_guardado)
    ):
        session.clear()
        return None

    g.usuario = usuario
    return usuario


def ruta_siguiente_segura(destino: str):
    """
    Devuelve un destino local válido o None.

    Evita redirecciones abiertas: solo se aceptan rutas que empiezan con
    una sola barra y no apuntan a otro dominio.
    """
    if not destino:
        return None
    destino = str(destino).strip()
    if not destino.startswith("/") or destino.startswith("//"):
        return None
    if "\\" in destino or "\r" in destino or "\n" in destino:
        return None
    return destino


def es_administrador(usuario) -> bool:
    """True si la cuenta tiene rol de administración."""
    return bool(usuario) and usuario["rol"] == "administrador"


def solo_administrador(vista):
    """Decorador: permite el acceso únicamente al rol administrador."""

    @wraps(vista)
    def envoltura(*args, **kwargs):
        usuario = getattr(g, "usuario", None)
        if not es_administrador(usuario):
            abort(403)
        return vista(*args, **kwargs)

    return envoltura
