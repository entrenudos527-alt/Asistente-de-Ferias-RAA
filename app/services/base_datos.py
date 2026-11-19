"""
Base de datos de cuentas y permisos (SQLite).

Los eventos siguen viviendo en el Excel; esta base guarda únicamente
las cuentas, los roles, el estado y los intentos de ingreso.

La ruta se puede cambiar con la variable de entorno RAA_DB_PATH
(útil para Render o para llevar la base a un disco persistente).
"""

import os
import sqlite3

# Rol con permisos completos
ROL_ADMINISTRADOR = "administrador"
ROL_USUARIO = "usuario"
ROLES_VALIDOS = (ROL_ADMINISTRADOR, ROL_USUARIO)

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correo TEXT NOT NULL UNIQUE COLLATE NOCASE,
    nombre TEXT NOT NULL DEFAULT '',
    rol TEXT NOT NULL DEFAULT 'usuario'
        CHECK (rol IN ('administrador', 'usuario')),
    hash_contrasena TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1,
    debe_cambiar_contrasena INTEGER NOT NULL DEFAULT 0,
    token_sesion TEXT,
    creado_en TEXT NOT NULL,
    actualizado_en TEXT NOT NULL,
    ultimo_acceso TEXT
);

CREATE TABLE IF NOT EXISTS intentos_ingreso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correo TEXT NOT NULL,
    ip TEXT NOT NULL,
    fecha TEXT NOT NULL,
    exito INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_intentos_correo_ip
    ON intentos_ingreso (correo, ip, fecha);
"""


def ruta_base_datos() -> str:
    """Devuelve la ruta del archivo SQLite y crea la carpeta si falta."""
    ruta = os.environ.get("RAA_DB_PATH")
    if ruta:
        carpeta = os.path.dirname(os.path.abspath(ruta))
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        return ruta

    raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    carpeta = os.path.join(raiz, "datos")
    os.makedirs(carpeta, exist_ok=True)
    return os.path.join(carpeta, "raa.db")


def conectar() -> sqlite3.Connection:
    """Abre una conexión con filas tipo diccionario y claves foráneas activas."""
    conexion = sqlite3.connect(ruta_base_datos())
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def inicializar_base_datos() -> None:
    """Crea las tablas necesarias si no existen (idempotente)."""
    with conectar() as conexion:
        conexion.executescript(_ESQUEMA)


# ============================================================================
# Usuarios
# ============================================================================


def normalizar_correo(correo: str) -> str:
    """Normaliza el correo para comparaciones (sin espacios, en minúsculas)."""
    return str(correo or "").strip().lower()


def crear_usuario(
    correo: str,
    nombre: str,
    rol: str,
    hash_contrasena: str,
    debe_cambiar_contrasena: bool = True,
    activo: bool = True,
) -> int:
    """Inserta una cuenta nueva y devuelve su identificador."""
    from datetime import datetime

    if rol not in ROLES_VALIDOS:
        raise ValueError(f"Rol no válido: {rol}")

    ahora = datetime.now().isoformat(timespec="seconds")
    with conectar() as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO usuarios
                (correo, nombre, rol, hash_contrasena, activo,
                 debe_cambiar_contrasena, creado_en, actualizado_en)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                normalizar_correo(correo),
                str(nombre or "").strip(),
                rol,
                hash_contrasena,
                1 if activo else 0,
                1 if debe_cambiar_contrasena else 0,
                ahora,
                ahora,
            ),
        )
        return int(cursor.lastrowid)


def obtener_usuario_por_id(usuario_id: int):
    """Recupera una cuenta por su identificador."""
    with conectar() as conexion:
        fila = conexion.execute(
            "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
    return fila


def obtener_usuario_por_correo(correo: str):
    """Recupera una cuenta por correo (sin distinguir mayúsculas)."""
    with conectar() as conexion:
        fila = conexion.execute(
            "SELECT * FROM usuarios WHERE correo = ?", (normalizar_correo(correo),)
        ).fetchone()
    return fila


def listar_usuarios():
    """Devuelve todas las cuentas ordenadas por rol y correo."""
    with conectar() as conexion:
        filas = conexion.execute(
            """
            SELECT * FROM usuarios
            ORDER BY CASE rol WHEN 'administrador' THEN 0 ELSE 1 END,
                     correo COLLATE NOCASE
            """
        ).fetchall()
    return filas


def existe_correo(correo: str) -> bool:
    """Indica si el correo ya está registrado."""
    return obtener_usuario_por_correo(correo) is not None


def contar_usuarios() -> int:
    """Cantidad total de cuentas (para el aviso de primera configuración)."""
    with conectar() as conexion:
        fila = conexion.execute("SELECT COUNT(*) AS total FROM usuarios").fetchone()
    return int(fila["total"]) if fila else 0


def contar_administradores_activos() -> int:
    """Cantidad de administradores activos (evita quedarse sin acceso)."""
    with conectar() as conexion:
        fila = conexion.execute(
            "SELECT COUNT(*) AS total FROM usuarios "
            "WHERE rol = 'administrador' AND activo = 1"
        ).fetchone()
    return int(fila["total"]) if fila else 0


def actualizar_contrasena(usuario_id: int, hash_contrasena: str) -> None:
    """Guarda un nuevo hash y cierra las sesiones abiertas de esa cuenta."""
    from datetime import datetime

    with conectar() as conexion:
        conexion.execute(
            """
            UPDATE usuarios
               SET hash_contrasena = ?,
                   debe_cambiar_contrasena = 0,
                   token_sesion = NULL,
                   actualizado_en = ?
             WHERE id = ?
            """,
            (hash_contrasena, datetime.now().isoformat(timespec="seconds"), usuario_id),
        )


def restablecer_contrasena(usuario_id: int, hash_contrasena: str) -> None:
    """Asigna una contraseña temporal y obliga a cambiarla al ingresar."""
    from datetime import datetime

    with conectar() as conexion:
        conexion.execute(
            """
            UPDATE usuarios
               SET hash_contrasena = ?,
                   debe_cambiar_contrasena = 1,
                   token_sesion = NULL,
                   actualizado_en = ?
             WHERE id = ?
            """,
            (hash_contrasena, datetime.now().isoformat(timespec="seconds"), usuario_id),
        )


def cambiar_estado(usuario_id: int, activo: bool) -> None:
    """Activa o desactiva una cuenta; al desactivar cierra su sesión."""
    from datetime import datetime

    with conectar() as conexion:
        conexion.execute(
            """
            UPDATE usuarios
               SET activo = ?,
                   token_sesion = CASE WHEN ? = 1 THEN token_sesion ELSE NULL END,
                   actualizado_en = ?
             WHERE id = ?
            """,
            (
                1 if activo else 0,
                1 if activo else 0,
                datetime.now().isoformat(timespec="seconds"),
                usuario_id,
            ),
        )


def cambiar_rol(usuario_id: int, rol: str) -> None:
    """Cambia el rol de una cuenta."""
    from datetime import datetime

    if rol not in ROLES_VALIDOS:
        raise ValueError(f"Rol no válido: {rol}")

    with conectar() as conexion:
        conexion.execute(
            "UPDATE usuarios SET rol = ?, actualizado_en = ? WHERE id = ?",
            (rol, datetime.now().isoformat(timespec="seconds"), usuario_id),
        )


def guardar_token_sesion(usuario_id: int, token: str) -> None:
    """Asocia un token de sesión a la cuenta y registra el último acceso."""
    from datetime import datetime

    ahora = datetime.now().isoformat(timespec="seconds")
    with conectar() as conexion:
        conexion.execute(
            "UPDATE usuarios SET token_sesion = ?, ultimo_acceso = ? WHERE id = ?",
            (token, ahora, usuario_id),
        )


def cerrar_token_sesion(usuario_id: int) -> None:
    """Invalida el token de sesión de la cuenta (cierre de sesión)."""
    with conectar() as conexion:
        conexion.execute(
            "UPDATE usuarios SET token_sesion = NULL WHERE id = ?", (usuario_id,)
        )


# ============================================================================
# Intentos de ingreso (límite de intentos repetidos)
# ============================================================================


def registrar_intento(correo: str, ip: str, exito: bool) -> None:
    """Registra un intento de ingreso, correcto o fallido."""
    from datetime import datetime

    with conectar() as conexion:
        conexion.execute(
            "INSERT INTO intentos_ingreso (correo, ip, fecha, exito) VALUES (?, ?, ?, ?)",
            (
                normalizar_correo(correo),
                str(ip or ""),
                datetime.now().isoformat(timespec="seconds"),
                1 if exito else 0,
            ),
        )


def contar_intentos_fallidos(correo: str, ip: str) -> int:
    """Cuenta los intentos fallidos recientes para ese correo y esa IP."""
    from datetime import datetime, timedelta

    desde = (datetime.now() - timedelta(minutes=15)).isoformat(timespec="seconds")
    with conectar() as conexion:
        fila = conexion.execute(
            """
            SELECT COUNT(*) AS total
              FROM intentos_ingreso
             WHERE correo = ? AND ip = ? AND exito = 0 AND fecha >= ?
            """,
            (normalizar_correo(correo), str(ip or ""), desde),
        ).fetchone()
    return int(fila["total"]) if fila else 0


def limpiar_intentos(correo: str, ip: str) -> None:
    """Borra el historial de intentos fallidos tras un ingreso correcto."""
    with conectar() as conexion:
        conexion.execute(
            "DELETE FROM intentos_ingreso WHERE correo = ? AND ip = ? AND exito = 0",
            (normalizar_correo(correo), str(ip or "")),
        )


def inicio_de_intentos(correo: str, ip: str):
    """Devuelve la fecha del primer intento fallido reciente (para el aviso)."""
    from datetime import datetime, timedelta

    desde = (datetime.now() - timedelta(minutes=15)).isoformat(timespec="seconds")
    with conectar() as conexion:
        fila = conexion.execute(
            """
            SELECT MIN(fecha) AS primera
              FROM intentos_ingreso
             WHERE correo = ? AND ip = ? AND exito = 0 AND fecha >= ?
            """,
            (normalizar_correo(correo), str(ip or ""), desde),
        ).fetchone()
    return fila["primera"] if fila else None
