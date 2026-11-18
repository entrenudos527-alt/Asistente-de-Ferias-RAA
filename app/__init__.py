"""
Fábrica de la aplicación Flask — Asistente de Eventos RAA.

Patrón MVC: aquí se registran controladores y servicios.
La llave de IA se lee de .env (nunca hardcodeada).
"""

import os
from flask import Flask, jsonify, render_template, request, redirect, url_for

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


def create_app():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY debe estar definida en el entorno (.env)")

    app.config.from_mapping(
        SECRET_KEY=secret_key,
    )

    # Registrar filtros de Jinja2 para formateo de fechas, horas y montos
    app.jinja_env.filters["formato_fecha"] = formato_fecha
    app.jinja_env.filters["formato_hora"] = formato_hora
    app.jinja_env.filters["formato_fecha_hora"] = formato_fecha_hora
    app.jinja_env.filters["formato_monto"] = formatear_monto
    app.jinja_env.filters["formato_rango_fechas"] = formatear_rango_fechas

    # ========================================================================
    # Rutas públicas
    # ========================================================================

    @app.route("/")
    def index():
        return redirect(url_for("inicio"))

    @app.route("/salud")
    def salud():
        return jsonify({"estado": "ok"})

    # ========================================================================
    # Rutas de pantallas (frontend)
    # ========================================================================

    @app.route("/inicio", endpoint="inicio")
    def pantalla_inicio():
        from app.services.lectura_eventos import (
            leer_eventos,
            obtener_todos_los_eventos,
        )

        datos = leer_eventos()
        eventos = datos["registros"]
        tipos_evento = datos["tipos_evento"]

        # Contadores
        total = len(eventos)
        por_tipo = {}
        for ev in eventos:
            tipo = str(ev.get("Tipo de evento", "")).strip()
            if tipo:
                por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

        # Normalizar eventos para la plantilla
        eventos_vista = []
        for ev in eventos:
            eventos_vista.append(
                {
                    "nombre": str(ev.get("Nombre del evento", "")),
                    "tipo": str(ev.get("Tipo de evento", "")),
                    "lugar": str(ev.get("Lugar del evento", "")),
                    "fecha_inicio": ev.get("Fecha de inicio"),
                    "fecha_fin": ev.get("Fecha de finalización"),
                    "hora_inicio": ev.get("Hora de inicio del evento"),
                    "hora_fin": ev.get("Hora finalización del evento"),
                }
            )

        return render_template(
            "inicio.html",
            eventos=eventos_vista,
            total_registros=total,
            tipos_evento=tipos_evento,
            conteo_por_tipo=por_tipo,
        )

    @app.route("/detalle/<nombre_evento>", endpoint="detalle")
    def pantalla_detalle(nombre_evento):
        from app.services.lectura_eventos import obtener_evento_por_nombre

        registro = obtener_evento_por_nombre(nombre_evento)
        if registro is None:
            return jsonify({"error": f"Evento '{nombre_evento}' no encontrado"}), 404

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
            preguntas_sugeridas=[
                "¿Cuándo es el evento?",
                "¿Dónde se lleva a cabo?",
                "¿Cuál es el costo de participación?",
                "¿Hay cupos disponibles?",
                "¿Cuál es el coordinador?",
            ],
        )

    # ========================================================================
    # Ruta de envío de chat (agente de IA)
    # ========================================================================

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
            preguntas_sugeridas=[
                "¿Cuándo es el evento?",
                "¿Dónde se lleva a cabo?",
                "¿Cuál es el costo de participación?",
                "¿Hay cupos disponibles?",
                "¿Cuál es el coordinador?",
            ],
        )

    # ========================================================================
    # Rutas de administración
    # ========================================================================

    @app.route("/admin", endpoint="admin_panel")
    def admin_panel():
        from app.services.lectura_eventos import leer_eventos

        datos = leer_eventos()
        eventos = datos["registros"]

        return render_template("inicio.html", eventos=eventos, admin=True)

    return app
