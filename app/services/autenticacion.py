"""
Autenticación de cuentas con hash seguro de contraseñas.

Se usa Werkzeug (la utilidad de autenticación que trae Flask):
  generate_password_hash / check_password_hash con PBKDF2-SHA256.
Las contraseñas nunca se guardan ni se muestran en texto plano.

Reglas:
  - No existe registro público: solo una persona administradora crea cuentas.
  - Las cuentas nuevas reciben una contraseña temporal y deben cambiarla.
  - Tras 5 intentos fallidos en 15 minutos se bloquea ese correo desde esa IP.
"""

import re
import secrets
import string

from werkzeug.security import check_password_hash, generate_password_hash

from app.services import base_datos

# Límite de intentos repetidos
MAX_INTENTOS = 5
VENTANA_MINUTOS = 15

# Contraseñas
LARGO_MINIMO = 8
_METODO_HASH = "pbkdf2:sha256:600000"

_RE_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


# ============================================================================
# Contraseñas
# ============================================================================


def hash_contrasena(contrasena: str) -> str:
    """Devuelve el hash PBKDF2-SHA256 de una contraseña."""
    return generate_password_hash(contrasena, method=_METODO_HASH)


def verificar_contrasena(hash_guardado: str, contrasena: str) -> bool:
    """Compara una contraseña con su hash (False si el hash es inválido)."""
    if not hash_guardado or not contrasena:
        return False
    try:
        return check_password_hash(hash_guardado, contrasena)
    except (ValueError, TypeError):
        return False


def validar_correo(correo: str):
    """Valida el formato del correo. Devuelve (valido, mensaje)."""
    correo = str(correo or "").strip()
    if not correo:
        return False, "Ingresá el correo electrónico."
    if not _RE_CORREO.match(correo):
        return False, "El correo electrónico no tiene un formato válido."
    return True, ""


def validar_contrasena(contrasena: str, confirmacion: str = None):
    """Valida una contraseña nueva. Devuelve (valido, mensaje)."""
    contrasena = str(contrasena or "")
    if len(contrasena) < LARGO_MINIMO:
        return False, f"La contraseña debe tener al menos {LARGO_MINIMO} caracteres."
    if contrasena.strip() == "":
        return False, "La contraseña no puede estar vacía."
    if contrasena != contrasena.strip():
        return False, "La contraseña no puede empezar ni terminar con espacios."
    if confirmacion is not None and contrasena != confirmacion:
        return False, "Las contraseñas no coinciden."
    return True, ""


def generar_contrasena_temporal(largo: int = 12) -> str:
    """
    Genera una contraseña temporal aleatoria y legible.

    Incluye al menos una mayúscula, una minúscula y un dígito.
    No se guarda en ningún registro visible: solo se muestra una vez.
    """
    letras_min = "abcdefghijkmnpqrstuvwxyz"
    letras_may = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    digitos = "23456789"
    alfabeto = string.ascii_letters + string.digits

    obligatorios = [
        secrets.choice(letras_may),
        secrets.choice(letras_min),
        secrets.choice(digitos),
    ]
    resto = [secrets.choice(alfabeto) for _ in range(max(0, largo - len(obligatorios)))]
    caracteres = obligatorios + resto
    secrets.SystemRandom().shuffle(caracteres)
    return "".join(caracteres)


# ============================================================================
# Ingreso y bloqueo por intentos
# ============================================================================


def esta_bloqueado(correo: str, ip: str) -> bool:
    """True si se superaron los intentos permitidos en la ventana de tiempo."""
    return base_datos.contar_intentos_fallidos(correo, ip) >= MAX_INTENTOS


def autenticar(correo: str, contrasena: str, ip: str = "") -> dict:
    """
    Verifica credenciales y registra el intento.

    Returns:
        dict con: ok (bool), usuario (fila o None), mensaje (str)
    """
    correo = base_datos.normalizar_correo(correo)

    if esta_bloqueado(correo, ip):
        return {
            "ok": False,
            "usuario": None,
            "mensaje": (
                "Demasiados intentos fallidos. Esperá unos minutos e intentá de nuevo "
                "o pedile a la persona administradora que restablezca tu contraseña."
            ),
        }

    usuario = base_datos.obtener_usuario_por_correo(correo)

    # Mensaje genérico: no se revela si el correo existe o no.
    credenciales_invalidas = {
        "ok": False,
        "usuario": None,
        "mensaje": "El correo o la contraseña no son correctos.",
    }

    if usuario is None:
        base_datos.registrar_intento(correo, ip, exito=False)
        return credenciales_invalidas

    if not bool(usuario["activo"]):
        # Cuenta desactivada: se informa sin revelar datos adicionales.
        base_datos.registrar_intento(correo, ip, exito=False)
        return {
            "ok": False,
            "usuario": None,
            "mensaje": "La cuenta está desactivada. Consultá con la persona administradora.",
        }

    if not verificar_contrasena(usuario["hash_contrasena"], contrasena):
        base_datos.registrar_intento(correo, ip, exito=False)
        return credenciales_invalidas

    base_datos.registrar_intento(correo, ip, exito=True)
    base_datos.limpiar_intentos(correo, ip)

    return {"ok": True, "usuario": usuario, "mensaje": ""}


# ============================================================================
# Gestión de cuentas (solo administración)
# ============================================================================


def crear_cuenta(correo: str, nombre: str, rol: str):
    """
    Crea una cuenta con contraseña temporal.

    Returns:
        dict con: ok, mensaje, usuario_id, contrasena_temporal
    """
    valido, mensaje = validar_correo(correo)
    if not valido:
        return {"ok": False, "mensaje": mensaje}

    rol = str(rol or "").strip().lower()
    if rol not in base_datos.ROLES_VALIDOS:
        return {"ok": False, "mensaje": "Seleccioná un rol válido."}

    if base_datos.existe_correo(correo):
        return {"ok": False, "mensaje": "Ya existe una cuenta con ese correo."}

    temporal = generar_contrasena_temporal()
    usuario_id = base_datos.crear_usuario(
        correo=correo,
        nombre=nombre,
        rol=rol,
        hash_contrasena=hash_contrasena(temporal),
        debe_cambiar_contrasena=True,
        activo=True,
    )

    return {
        "ok": True,
        "mensaje": "Cuenta creada. La contraseña temporal se muestra una sola vez.",
        "usuario_id": usuario_id,
        "contrasena_temporal": temporal,
    }


def restablecer_temporal(usuario_id: int):
    """
    Asigna una nueva contraseña temporal a una cuenta.

    No se puede consultar la contraseña anterior: solo se genera una nueva.
    """
    usuario = base_datos.obtener_usuario_por_id(usuario_id)
    if usuario is None:
        return {"ok": False, "mensaje": "La cuenta no existe."}
    if not bool(usuario["activo"]):
        return {
            "ok": False,
            "mensaje": "Activá la cuenta antes de restablecer su contraseña.",
        }

    temporal = generar_contrasena_temporal()
    base_datos.restablecer_contrasena(usuario_id, hash_contrasena(temporal))
    return {
        "ok": True,
        "mensaje": "Contraseña temporal generada. Se muestra una sola vez.",
        "contrasena_temporal": temporal,
        "correo": usuario["correo"],
    }


def cambiar_contrasena_propia(usuario_id: int, actual: str, nueva: str, confirmacion: str):
    """Cambia la contraseña de la propia cuenta verificando la actual."""
    usuario = base_datos.obtener_usuario_por_id(usuario_id)
    if usuario is None:
        return {"ok": False, "mensaje": "La cuenta no existe."}

    if not verificar_contrasena(usuario["hash_contrasena"], actual):
        return {"ok": False, "mensaje": "La contraseña actual no es correcta."}

    valido, mensaje = validar_contrasena(nueva, confirmacion)
    if not valido:
        return {"ok": False, "mensaje": mensaje}

    if verificar_contrasena(usuario["hash_contrasena"], nueva):
        return {
            "ok": False,
            "mensaje": "La contraseña nueva debe ser distinta de la actual.",
        }

    base_datos.actualizar_contrasena(usuario_id, hash_contrasena(nueva))
    return {"ok": True, "mensaje": "Contraseña actualizada correctamente."}
