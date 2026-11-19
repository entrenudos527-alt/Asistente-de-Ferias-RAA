"""
Fábrica de la aplicación Flask — Asistente de Eventos RAA.

Patrón MVC: aquí se registran controladores y servicios.

Seguridad:
  - Pantalla de ingreso obligatoria antes de ver los eventos.
  - Dos roles: administrador y usuario.
  - Contraseñas con hash PBKDF2-SHA256 (Werkzeug), nunca en texto plano.
  - Token CSRF en todos los formularios y en el chat.
  - Sesiones firmadas con token de sesión guardado en la base.
  - Límite de intentos fallidos de ingreso.

Los eventos se siguen leyendo del Excel; las cuentas viven en SQLite.
"""

import os
import secrets
from datetime import timedelta

import click
from flask import (
    Flask,
    abort,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from dotenv import load_dotenv
from app.utils.formato import (
    formatear_fecha as formato_fecha,
    formatear_hora as formato_hora,
    formatear_fecha_hora as formato_fecha_hora,
    formatear_monto,
    formatear_rango_fechas,
)

# Cargar variables de entorno desde .env si existe
load_dotenv()


# ============================================================================
# Utilidades de presentación
# ============================================================================


def _dias_del_evento(fecha_inicio, fecha_fin):
    """
    Devuelve la lista de días (ISO) que abarca el evento.

    Se usa para que el filtro de fecha encuentre también eventos de varios
    días cuando la fecha consultada está entre el inicio y la finalización.
    """
    from datetime import date, datetime, timedelta

    def _a_fecha(valor):
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        from app.utils.formato import _parse_valor

        parseado = _parse_valor(valor)
        if isinstance(parseado, datetime):
            return parseado.date()
        if isinstance(parseado, date):
            return parseado
        return None

    inicio = _a_fecha(fecha_inicio)
    if inicio is None:
        return []

    fin = _a_fecha(fecha_fin) or inicio
    if fin < inicio:
        fin = inicio

    dias = []
    actual = inicio
    while actual <= fin and len(dias) < 120:
        dias.append(actual.isoformat())
        actual += timedelta(days=1)
    return dias


def _normalizar_eventos(eventos):
    """Prepara los registros del Excel para las plantillas del listado."""
    eventos_vista = []
    for ev in eventos:
        fecha_inicio = ev.get("Fecha de inicio")
        fecha_fin = ev.get("Fecha de finalización")
        eventos_vista.append(
            {
                "nombre": str(ev.get("Nombre del evento", "")),
                "tipo": str(ev.get("Tipo de evento", "")),
                "lugar": str(ev.get("Lugar del evento", "")),
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "hora_inicio": ev.get("Hora de inicio del evento"),
                "hora_fin": ev.get("Hora finalización del evento"),
                "rango_fechas": formatear_rango_fechas(fecha_inicio, fecha_fin),
                "fechas_iso": _dias_del_evento(fecha_inicio, fecha_fin),
            }
        )
    return eventos_vista


def _conteo_por_tipo(eventos):
    """Cuenta los eventos registrados por tipo."""
    por_tipo = {}
    for ev in eventos:
        tipo = str(ev.get("Tipo de evento", "")).strip()
        if tipo:
            por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
    return por_tipo


def _ip_cliente() -> str:
    """IP del cliente, considerando el proxy de Render."""
    reenviada = request.headers.get("X-Forwarded-For", "")
    if reenviada:
        return reenviada.split(",")[0].strip()
    return request.remote_addr or ""


PREGUNTAS_SUGERIDAS = [
    "¿Cuándo es el evento?",
    "¿Dónde se lleva a cabo?",
    "¿Cuál es el costo de participación?",
    "¿Hay cupos disponibles?",
    "¿Cuál es el coordinador?",
]


# ============================================================================
# Aplicación
# ============================================================================


def _crear_admin_desde_entorno(app) -> None:
    """
    Crea la primera cuenta administradora desde variables de entorno.

    Pensado para servidores donde no es cómodo abrir una consola (Render,
    por ejemplo). Solo actúa cuando la base todavía no tiene ninguna cuenta:
    nunca sobrescribe cuentas ni contraseñas existentes.
    """
    from app.services import autenticacion, base_datos

    correo = os.environ.get("RAA_ADMIN_CORREO", "").strip()
    clave = os.environ.get("RAA_ADMIN_CLAVE", "")
    nombre = os.environ.get("RAA_ADMIN_NOMBRE", "").strip() or "Administración RAA"

    if not correo or not clave:
        return

    if base_datos.contar_usuarios() > 0:
        return

    valido, mensaje = autenticacion.validar_correo(correo)
    if not valido:
        app.logger.warning("RAA_ADMIN_CORREO no es válido: %s", mensaje)
        return

    valido, mensaje = autenticacion.validar_contrasena(clave)
    if not valido:
        app.logger.warning("RAA_ADMIN_CLAVE no es válida: %s", mensaje)
        return

    try:
        base_datos.crear_usuario(
            correo=correo,
            nombre=nombre,
            rol=base_datos.ROL_ADMINISTRADOR,
            hash_contrasena=autenticacion.hash_contrasena(clave),
            debe_cambiar_contrasena=False,
            activo=True,
        )
        app.logger.info(
            "Cuenta administradora inicial creada desde variables de entorno: %s",
            correo,
        )
    except Exception as error:  # noqa: BLE001
        # Con varios workers puede ocurrir que otro proceso la cree primero.
        # No se debe impedir el arranque por eso.
        app.logger.warning(
            "No se creó la cuenta administradora desde el entorno: %s", error
        )


def create_app():
    """Crea y configura la aplicación Flask."""
    from app.services import base_datos, autenticacion
    from app.seguridad import (
        ENDPOINTS_CAMBIO_OBLIGATORIO,
        ENDPOINTS_PUBLICOS,
        cargar_usuario_en_contexto,
        csrf_valido,
        es_administrador,
        obtener_csrf_token,
        ruta_siguiente_segura,
        solo_administrador,
    )

    app = Flask(__name__)

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY debe estar definida en el entorno (.env)")

    app.config.from_mapping(
        SECRET_KEY=secret_key,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("RAA_COOKIE_SEGURA", "").lower()
        in ("1", "true", "si", "sí"),
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        MAX_CONTENT_LENGTH=10 * 1024 * 1024,  # 10 MB para el Excel
    )

    # Base de datos de cuentas (tablas creadas si faltan)
    base_datos.inicializar_base_datos()

    # Primera cuenta administradora desde variables de entorno (Render)
    _crear_admin_desde_entorno(app)

    # Registrar filtros de Jinja2 para formateo de fechas, horas y montos
    app.jinja_env.filters["formato_fecha"] = formato_fecha
    app.jinja_env.filters["formato_hora"] = formato_hora
    app.jinja_env.filters["formato_fecha_hora"] = formato_fecha_hora
    app.jinja_env.filters["formato_monto"] = formatear_monto
    app.jinja_env.filters["formato_rango_fechas"] = formatear_rango_fechas

    # ========================================================================
    # Contexto para las plantillas
    # ========================================================================

    @app.context_processor
    def inyectar_contexto():
        usuario = getattr(g, "usuario", None)
        return {
            "usuario_actual": usuario,
            "es_admin": es_administrador(usuario),
            "csrf_token": obtener_csrf_token,
        }

    # ========================================================================
    # Protección general: CSRF, sesión y contraseña temporal
    # ========================================================================

    @app.before_request
    def proteger_peticion():
        modificacion = request.method in ("POST", "PUT", "PATCH", "DELETE")

        def token_csrf_enviado() -> str:
            token = request.form.get("csrf_token", "")
            if not token:
                token = request.headers.get("X-CSRF-Token", "")
            if not token and request.is_json:
                token = (request.get_json(silent=True) or {}).get("csrf_token", "")
            return token or ""

        # 1. Cuenta autenticada en g.usuario (valida el token de sesión)
        usuario = cargar_usuario_en_contexto(base_datos.obtener_usuario_por_id)

        # 2. Rutas públicas: solo el ingreso acepta envío de formulario
        if request.endpoint in ENDPOINTS_PUBLICOS:
            if request.endpoint == "login" and modificacion:
                if not csrf_valido(token_csrf_enviado()):
                    return _formulario_vencido()
            return None

        # 3. Sin sesión: pedir ingreso conservando el destino
        if usuario is None:
            if request.endpoint == "chat_enviar":
                return (
                    jsonify(
                        {
                            "exito": False,
                            "texto_respuesta": "Tu sesión venció. Volvé a ingresar para consultar.",
                            "referencia_registro": None,
                            "requiere_ingreso": True,
                        }
                    ),
                    401,
                )
            destino = request.full_path if request.query_string else request.path
            return redirect(url_for("login", siguiente=destino))

        # 4. CSRF en toda petición autenticada que modifica datos
        if modificacion and not csrf_valido(token_csrf_enviado()):
            return _formulario_vencido()

        # 5. Contraseña temporal pendiente de cambio
        if bool(usuario["debe_cambiar_contrasena"]) and (
            request.endpoint not in ENDPOINTS_CAMBIO_OBLIGATORIO
        ):
            return redirect(url_for("cambiar_contrasena"))

        return None

    def _formulario_vencido():
        return (
            render_template(
                "error.html",
                codigo=400,
                titulo="Formulario vencido",
                mensaje=(
                    "La sesión del formulario venció o el token de seguridad no es válido. "
                    "Volvé a cargar la página e intentá de nuevo."
                ),
            ),
            400,
        )

    @app.after_request
    def cabeceras_seguridad(respuesta):
        respuesta.headers.setdefault("X-Content-Type-Options", "nosniff")
        respuesta.headers.setdefault("X-Frame-Options", "DENY")
        respuesta.headers.setdefault("Referrer-Policy", "same-origin")
        if getattr(g, "usuario", None) is not None:
            respuesta.headers.setdefault("Cache-Control", "no-store")
        return respuesta

    # ========================================================================
    # Manejo de errores
    # ========================================================================

    @app.errorhandler(403)
    def sin_permiso(_error):
        return (
            render_template(
                "sin_permiso.html",
                mensaje="Tu cuenta no tiene permisos para acceder a esta sección.",
            ),
            403,
        )

    @app.errorhandler(404)
    def no_encontrado(_error):
        return (
            render_template(
                "error.html",
                codigo=404,
                titulo="Página no encontrada",
                mensaje="La dirección solicitada no existe o el evento ya no está disponible.",
            ),
            404,
        )

    @app.errorhandler(413)
    def archivo_muy_grande(_error):
        return (
            render_template(
                "error.html",
                codigo=413,
                titulo="Archivo demasiado grande",
                mensaje="El archivo supera el tamaño máximo permitido (10 MB).",
            ),
            413,
        )

    # ========================================================================
    # Sesión
    # ========================================================================

    def iniciar_sesion(usuario_id: int) -> None:
        """Crea una sesión nueva, con token aleatorio guardado en la base."""
        token = secrets.token_urlsafe(32)
        base_datos.guardar_token_sesion(usuario_id, token)
        session.clear()
        session["usuario_id"] = usuario_id
        session["token_sesion"] = token
        session.permanent = True
        obtener_csrf_token()

    @app.route("/login", methods=["GET", "POST"], endpoint="login")
    def pantalla_login():
        if getattr(g, "usuario", None) is not None:
            return redirect(url_for("inicio"))

        siguiente = ruta_siguiente_segura(
            request.values.get("siguiente", "")
        )

        if request.method == "POST":
            correo = request.form.get("correo", "")
            contrasena = request.form.get("contrasena", "")

            resultado = autenticacion.autenticar(
                correo, contrasena, ip=_ip_cliente()
            )

            if not resultado["ok"]:
                return (
                    render_template(
                        "login.html",
                        correo=correo,
                        error=resultado["mensaje"],
                        siguiente=siguiente,
                    ),
                    401,
                )

            usuario = resultado["usuario"]
            iniciar_sesion(usuario["id"])

            if bool(usuario["debe_cambiar_contrasena"]):
                return redirect(url_for("cambiar_contrasena"))

            return redirect(siguiente or url_for("inicio"))

        return render_template("login.html", correo="", error=None, siguiente=siguiente)

    @app.route("/logout", methods=["POST"], endpoint="logout")
    def cerrar_sesion():
        usuario_id = session.get("usuario_id")
        if usuario_id:
            base_datos.cerrar_token_sesion(usuario_id)
        session.clear()
        flash("Cerraste sesión correctamente.", "exito")
        return redirect(url_for("login"))

    @app.route("/cambiar-contrasena", methods=["GET", "POST"], endpoint="cambiar_contrasena")
    def cambiar_contrasena():
        usuario = g.usuario
        obligatorio = bool(usuario["debe_cambiar_contrasena"])
        error = None

        if request.method == "POST":
            resultado = autenticacion.cambiar_contrasena_propia(
                usuario_id=usuario["id"],
                actual=request.form.get("actual", ""),
                nueva=request.form.get("nueva", ""),
                confirmacion=request.form.get("confirmacion", ""),
            )
            if resultado["ok"]:
                # La contraseña cambió: se renueva la sesión
                iniciar_sesion(usuario["id"])
                flash(resultado["mensaje"], "exito")
                return redirect(url_for("inicio"))
            error = resultado["mensaje"]

        return render_template(
            "cambiar_contrasena.html", error=error, obligatorio=obligatorio
        )

    # ========================================================================
    # Rutas públicas mínimas
    # ========================================================================

    @app.route("/")
    def index():
        if getattr(g, "usuario", None) is None:
            return redirect(url_for("login"))
        return redirect(url_for("inicio"))

    @app.route("/salud")
    def salud():
        return jsonify({"estado": "ok"})

    # ========================================================================
    # Eventos (requieren sesión; ambos roles pueden consultar)
    # ========================================================================

    @app.route("/inicio", endpoint="inicio")
    def pantalla_inicio():
        from app.services.lectura_eventos import leer_eventos

        datos = leer_eventos()
        eventos = datos["registros"]

        return render_template(
            "inicio.html",
            eventos=_normalizar_eventos(eventos),
            total_registros=len(eventos),
            tipos_evento=datos["tipos_evento"],
            conteo_por_tipo=_conteo_por_tipo(eventos),
        )

    @app.route("/detalle/<path:nombre_evento>", endpoint="detalle")
    def pantalla_detalle(nombre_evento):
        from app.services.lectura_eventos import obtener_evento_por_nombre

        registro = obtener_evento_por_nombre(nombre_evento)
        if registro is None:
            abort(404)

        return render_template("detalle.html", evento=registro)

    @app.route("/chat", endpoint="chat")
    def pantalla_chat():
        nombre = request.args.get("nombre")

        evento_seleccionado = None
        if nombre:
            from app.services.lectura_eventos import obtener_evento_por_nombre

            evento_seleccionado = obtener_evento_por_nombre(nombre)

        return render_template(
            "resultados.html",
            evento_seleccionado=evento_seleccionado,
            historial=[],
            preguntas_sugeridas=PREGUNTAS_SUGERIDAS,
        )

    @app.route("/chat/enviar", methods=["POST"], endpoint="chat_enviar")
    def chat_enviar():
        from app.services.agente_ia import (
            clave_ia_configurada,
            procesar_pregunta,
        )

        if not clave_ia_configurada():
            return jsonify(
                {
                    "exito": False,
                    "texto_respuesta": (
                        "El servicio de IA no está configurado. "
                        "Contacte al administrador para configurar la llave de API."
                    ),
                    "referencia_registro": None,
                }
            ), 503

        datos = request.get_json(silent=True) or {}
        pregunta = datos.get("pregunta", "")
        contexto = datos.get("nombre")

        resultado = procesar_pregunta(pregunta, contexto_visible=contexto)

        return jsonify(
            {
                "exito": resultado.exito,
                "texto_respuesta": resultado.texto_respuesta,
                "referencia_registro": resultado.referencia_registro,
            }
        )

    @app.route("/chat/nueva", endpoint="chat_nueva")
    def chat_nueva():
        return render_template(
            "resultados.html",
            evento_seleccionado=None,
            historial=[],
            preguntas_sugeridas=PREGUNTAS_SUGERIDAS,
        )

    # ========================================================================
    # Administración: usuarios
    # ========================================================================

    @app.route("/admin", endpoint="admin_panel")
    @solo_administrador
    def admin_panel():
        return redirect(url_for("admin_usuarios"))

    @app.route("/admin/usuarios", endpoint="admin_usuarios")
    @solo_administrador
    def admin_usuarios():
        usuarios = base_datos.listar_usuarios()
        return render_template(
            "admin_usuarios.html",
            usuarios=usuarios,
            max_intentos=autenticacion.MAX_INTENTOS,
            ventana_minutos=autenticacion.VENTANA_MINUTOS,
            largo_minimo=autenticacion.LARGO_MINIMO,
        )

    @app.route(
        "/admin/usuarios/crear", methods=["POST"], endpoint="admin_usuarios_crear"
    )
    @solo_administrador
    def admin_usuarios_crear():
        resultado = autenticacion.crear_cuenta(
            correo=request.form.get("correo", ""),
            nombre=request.form.get("nombre", ""),
            rol=request.form.get("rol", ""),
        )
        if resultado["ok"]:
            flash(
                f"Cuenta creada: {request.form.get('correo', '').strip().lower()}. "
                f"Contraseña temporal: {resultado['contrasena_temporal']} — "
                "entregala a la persona y pedile que la cambie al ingresar.",
                "credencial",
            )
        else:
            flash(resultado["mensaje"], "error")
        return redirect(url_for("admin_usuarios"))

    @app.route(
        "/admin/usuarios/<int:usuario_id>/estado",
        methods=["POST"],
        endpoint="admin_usuario_estado",
    )
    @solo_administrador
    def admin_usuario_estado(usuario_id):
        usuario = base_datos.obtener_usuario_por_id(usuario_id)
        if usuario is None:
            flash("La cuenta no existe.", "error")
            return redirect(url_for("admin_usuarios"))

        if usuario_id == g.usuario["id"]:
            flash("No podés desactivar tu propia cuenta.", "error")
            return redirect(url_for("admin_usuarios"))

        activar = request.form.get("accion") == "activar"

        if (
            not activar
            and usuario["rol"] == "administrador"
            and base_datos.contar_administradores_activos() <= 1
        ):
            flash("Debe quedar al menos una cuenta administradora activa.", "error")
            return redirect(url_for("admin_usuarios"))

        base_datos.cambiar_estado(usuario_id, activar)
        flash(
            f"La cuenta {usuario['correo']} quedó "
            f"{'activa' if activar else 'desactivada'}.",
            "exito",
        )
        return redirect(url_for("admin_usuarios"))

    @app.route(
        "/admin/usuarios/<int:usuario_id>/rol",
        methods=["POST"],
        endpoint="admin_usuario_rol",
    )
    @solo_administrador
    def admin_usuario_rol(usuario_id):
        usuario = base_datos.obtener_usuario_por_id(usuario_id)
        if usuario is None:
            flash("La cuenta no existe.", "error")
            return redirect(url_for("admin_usuarios"))

        nuevo_rol = request.form.get("rol", "")
        if nuevo_rol not in base_datos.ROLES_VALIDOS:
            flash("Rol no válido.", "error")
            return redirect(url_for("admin_usuarios"))

        if usuario_id == g.usuario["id"]:
            flash("No podés cambiar tu propio rol.", "error")
            return redirect(url_for("admin_usuarios"))

        if (
            usuario["rol"] == "administrador"
            and nuevo_rol == "usuario"
            and base_datos.contar_administradores_activos() <= 1
        ):
            flash("Debe quedar al menos una cuenta administradora activa.", "error")
            return redirect(url_for("admin_usuarios"))

        base_datos.cambiar_rol(usuario_id, nuevo_rol)
        flash(f"Rol actualizado: {usuario['correo']} ahora es {nuevo_rol}.", "exito")
        return redirect(url_for("admin_usuarios"))

    @app.route(
        "/admin/usuarios/<int:usuario_id>/restablecer",
        methods=["POST"],
        endpoint="admin_usuario_restablecer",
    )
    @solo_administrador
    def admin_usuario_restablecer(usuario_id):
        resultado = autenticacion.restablecer_temporal(usuario_id)
        if resultado["ok"]:
            flash(
                f"Contraseña temporal para {resultado['correo']}: "
                f"{resultado['contrasena_temporal']} — se muestra una sola vez. "
                "La persona deberá cambiarla al ingresar.",
                "credencial",
            )
        else:
            flash(resultado["mensaje"], "error")
        return redirect(url_for("admin_usuarios"))

    # ========================================================================
    # Administración: actualización del Excel de eventos
    # ========================================================================

    @app.route("/admin/eventos", endpoint="admin_eventos")
    @solo_administrador
    def admin_eventos():
        from app.services.lectura_eventos import (
            RUTA_EXCEL_INSUMOS,
            RUTA_EXCEL_TRABAJO,
            leer_eventos,
            ruta_excel_activa,
        )

        datos = leer_eventos()
        return render_template(
            "admin_eventos.html",
            eventos=datos["registros"],
            total_registros=datos["total_registros"],
            ruta_activa=ruta_excel_activa(),
            usa_copia_trabajo=os.path.exists(RUTA_EXCEL_TRABAJO),
            ruta_insumos=RUTA_EXCEL_INSUMOS,
        )

    @app.route(
        "/admin/eventos/importar",
        methods=["POST"],
        endpoint="admin_eventos_importar",
    )
    @solo_administrador
    def admin_eventos_importar():
        import tempfile

        from app.services.lectura_eventos import RUTA_EXCEL_TRABAJO

        archivo = request.files.get("archivo")
        if not archivo or not archivo.filename:
            flash("Seleccioná un archivo Excel (.xlsx).", "error")
            return redirect(url_for("admin_eventos"))

        if not archivo.filename.lower().endswith((".xlsx", ".xlsm")):
            flash("El archivo debe tener extensión .xlsx.", "error")
            return redirect(url_for("admin_eventos"))

        os.makedirs(os.path.dirname(RUTA_EXCEL_TRABAJO), exist_ok=True)

        # Archivo temporal en la misma carpeta para poder reemplazar de forma atómica.
        # Se cierra el descriptor de inmediato: en Windows el archivo no se puede
        # reemplazar mientras siga abierto.
        descriptor, ruta_temporal = tempfile.mkstemp(
            suffix=".xlsx", dir=os.path.dirname(RUTA_EXCEL_TRABAJO)
        )
        os.close(descriptor)
        try:
            archivo.save(ruta_temporal)
            total = _validar_excel_eventos(ruta_temporal)
            os.replace(ruta_temporal, RUTA_EXCEL_TRABAJO)
        except ValueError as error:
            _eliminar_si_existe(ruta_temporal)
            flash(f"No se cargó el archivo: {error}", "error")
            return redirect(url_for("admin_eventos"))
        except PermissionError:
            _eliminar_si_existe(ruta_temporal)
            flash(
                "No se pudo reemplazar el archivo porque está abierto en otro programa. "
                "Cerrá el Excel e intentá de nuevo.",
                "error",
            )
            return redirect(url_for("admin_eventos"))
        except Exception:
            _eliminar_si_existe(ruta_temporal)
            flash(
                "No se pudo leer el archivo. Verificá que sea un Excel válido "
                "con la hoja 'Eventos'.",
                "error",
            )
            return redirect(url_for("admin_eventos"))

        flash(
            f"Excel actualizado: {total} eventos cargados desde la nueva versión.",
            "exito",
        )
        return redirect(url_for("admin_eventos"))

    @app.route(
        "/admin/eventos/restaurar",
        methods=["POST"],
        endpoint="admin_eventos_restaurar",
    )
    @solo_administrador
    def admin_eventos_restaurar():
        from app.services.lectura_eventos import RUTA_EXCEL_TRABAJO

        if os.path.exists(RUTA_EXCEL_TRABAJO):
            os.remove(RUTA_EXCEL_TRABAJO)
            flash("Se restauró el Excel original de Insumos.", "exito")
        else:
            flash("No hay una copia cargada: ya se está usando el Excel original.", "error")
        return redirect(url_for("admin_eventos"))

    # ========================================================================
    # Comando para crear la primera cuenta administradora
    # ========================================================================

    @app.cli.command("crear-admin")
    @click.option("--correo", prompt="Correo de la persona administradora")
    @click.option("--nombre", prompt="Nombre completo")
    @click.option(
        "--contrasena",
        prompt="Contraseña (mínimo 8 caracteres)",
        hide_input=True,
        confirmation_prompt="Repetí la contraseña",
    )
    def crear_admin(correo, nombre, contrasena):
        """Crea la primera cuenta administradora (no hay registro público)."""
        valido, mensaje = autenticacion.validar_correo(correo)
        if not valido:
            raise click.ClickException(mensaje)

        if base_datos.existe_correo(correo):
            raise click.ClickException("Ya existe una cuenta con ese correo.")

        valido, mensaje = autenticacion.validar_contrasena(contrasena)
        if not valido:
            raise click.ClickException(mensaje)

        base_datos.crear_usuario(
            correo=correo,
            nombre=nombre,
            rol=base_datos.ROL_ADMINISTRADOR,
            hash_contrasena=autenticacion.hash_contrasena(contrasena),
            debe_cambiar_contrasena=False,
            activo=True,
        )
        click.echo("")
        click.echo(f"Cuenta administradora creada: {correo.strip().lower()}")
        click.echo("Ya podés ingresar en /login")
        click.echo("Desde ahí vas a poder crear las demás cuentas.")

    return app


def _eliminar_si_existe(ruta: str) -> None:
    """Borra un archivo temporal si existe, sin propagar errores."""
    try:
        if ruta and os.path.exists(ruta):
            os.remove(ruta)
    except OSError:
        pass


def _validar_excel_eventos(ruta: str) -> int:
    """
    Verifica que el Excel tenga la hoja 'Eventos', los encabezados
    necesarios y al menos un evento con nombre.

    Devuelve la cantidad de eventos o lanza ValueError con el motivo.
    """
    import openpyxl

    from app.services.lectura_eventos import HOJA_EVENTOS

    try:
        libro = openpyxl.load_workbook(ruta, data_only=True)
    except Exception as error:
        raise ValueError("el archivo no se puede abrir como Excel") from error

    if HOJA_EVENTOS not in libro.sheetnames:
        libro.close()
        raise ValueError("falta la hoja 'Eventos'")

    hoja = libro[HOJA_EVENTOS]
    encabezados = [
        str(hoja.cell(row=1, column=col).value or "").strip()
        for col in range(1, hoja.max_column + 1)
    ]

    if "Nombre del evento" not in encabezados:
        libro.close()
        raise ValueError("los encabezados deben estar en la fila 1 e incluir 'Nombre del evento'")

    columna_nombre = encabezados.index("Nombre del evento") + 1
    total = 0
    for fila in range(2, hoja.max_row + 1):
        valor = hoja.cell(row=fila, column=columna_nombre).value
        if valor is not None and str(valor).strip() != "":
            total += 1

    libro.close()

    if total == 0:
        raise ValueError("la hoja 'Eventos' no tiene registros con nombre de evento")

    return total
