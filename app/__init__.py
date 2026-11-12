"""
Fábrica de la aplicación Flask.

Patrón MVC: aquí se registran controladores y servicios.
La llave de IA se lee de .env (nunca hardcodeada).
"""

import os
from flask import Flask, jsonify, render_template, request, redirect, url_for

from dotenv import load_dotenv
from app.utils.formato import formato_fecha, formato_hora, formato_fecha_hora

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
        DEMO_DATE="2026-11-04T12:00:00",
        DEMO_TIMEZONE="America/Costa_Rica",
    )

    # Registrar filtros de Jinja2 para formateo de fechas y horas
    app.jinja_env.filters["formato_fecha"] = formato_fecha
    app.jinja_env.filters["formato_hora"] = formato_hora
    app.jinja_env.filters["formato_fecha_hora"] = formato_fecha_hora

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
        from app.services.lectura_datos import leer_actividades
        from datetime import datetime

        datos = leer_actividades()
        registros = datos["registros"]
        fecha_ref = datetime.fromisoformat(app.config["DEMO_DATE"])

        actividades = []
        proximas = 0
        canceladas = 0

        for reg in registros:
            estado = str(reg.get("Estado de la feria", "")).lower()
            if estado in {"cancelada", "finalizada"}:
                canceladas += 1
            else:
                fecha_inicio = reg.get("Fecha de inicio")
                if fecha_inicio:
                    try:
                        fi = datetime.fromisoformat(str(fecha_inicio))
                        if fi >= fecha_ref:
                            proximas += 1
                    except (ValueError, TypeError):
                        pass
            actividades.append(
                {
                    "codigo": str(reg.get("Identificador", "")),
                    "nombre": str(reg.get("Actividad", "")),
                    "lugar": str(reg.get("Lugar", "")),
                    "fecha": str(reg.get("Fecha de inicio", "")),
                    "horario_atencion": reg.get("Inicio de atención simulado"),
                    "estado_actividad": str(reg.get("Estado de la feria", "")),
                    "estado_inscripcion": str(reg.get("Estado de inscripción", "")),
                }
            )

        return render_template(
            "inicio.html",
            actividades=actividades,
            total_registros=len(actividades),
            contador_proximas=proximas,
            contador_canceladas=canceladas,
        )

    @app.route("/detalle/<codigo>", endpoint="detalle")
    def pantalla_detalle(codigo):
        from app.services.lectura_datos import obtener_actividad_por_codigo

        registro = obtener_actividad_por_codigo(codigo)
        if registro is None:
            return jsonify({"error": f"Actividad {codigo} no encontrada"}), 404

        # Normalizar claves del Excel (con espacios) a snake_case para las plantillas
        actividad = {
            "codigo": str(registro.get("Identificador", "")),
            "nombre": str(registro.get("Actividad", "")),
            "organiza": str(registro.get("Organiza", "")),
            "fecha_inicio": registro.get("Fecha de inicio"),
            "fecha_finalizacion": registro.get("Fecha de finalización"),
            "dias_participacion": str(registro.get("Días de participación", "")),
            "lugar": str(registro.get("Lugar", "")),
            "direccion_exacta_practica": str(
                registro.get("Dirección exacta de práctica", "")
            ),
            "enlace_ubicacion_practica": str(
                registro.get("Enlace de ubicación de práctica", "")
            ),
            "acceso_y_parqueo": str(registro.get("Acceso y parqueo", "")),
            "ingreso_y_montaje": registro.get("Ingreso y montaje"),
            "salida_y_desmontaje": registro.get("Salida y desmontaje"),
            "inicio_atencion_simulado": registro.get("Inicio de atención simulado"),
            "cierre_atencion_simulado": registro.get("Cierre de atención simulado"),
            "costo_participacion": str(registro.get("Costo de participación", "")),
            "moneda": str(registro.get("Moneda", "")),
            "unidad_cobro": str(registro.get("Unidad de cobro", "")),
            "incluye_el_costo": str(registro.get("Incluye el costo", "")),
            "forma_de_pago": str(registro.get("Forma de pago", "")),
            "fecha_limite_de_pago": registro.get("Fecha límite de pago"),
            "requisitos": str(registro.get("Requisitos", "")),
            "productos_permitidos_y_restricciones": str(
                registro.get("Productos permitidos y restricciones", "")
            ),
            "equipo_del_participante": str(registro.get("Equipo del participante", "")),
            "equipo_y_servicios_organizacion": str(
                registro.get("Equipo y servicios de organización", "")
            ),
            "condiciones_especiales": str(registro.get("Condiciones especiales", "")),
            "quienes_pueden_inscribirse": str(
                registro.get("Quiénes pueden inscribirse", "")
            ),
            "fecha_limite_inscripcion": registro.get("Fecha límite de inscripción"),
            "hora_limite_inscripcion": registro.get("Hora límite de inscripción"),
            "procedimiento_inscripcion": str(
                registro.get("Procedimiento de inscripción", "")
            ),
            "canal_inscripcion_practica": str(
                registro.get("Canal de inscripción de práctica", "")
            ),
            "documentos_requeridos": str(registro.get("Documentos requeridos", "")),
            "confirmacion_participacion": str(
                registro.get("Confirmación de participación", "")
            ),
            "estado_inscripcion": str(registro.get("Estado de inscripción", "")),
            "espacios_disponibles": str(registro.get("Espacios disponibles", "")),
            "verificacion_espacios": registro.get("Verificación de espacios"),
            "lista_de_espera": str(registro.get("Lista de espera", "")),
            "contacto_autorizado_practica": str(
                registro.get("Contacto autorizado de práctica", "")
            ),
            "cargo_del_contacto": str(registro.get("Cargo del contacto", "")),
            "telefono_whatsapp_practica": str(
                registro.get("Teléfono o WhatsApp de práctica", "")
            ),
            "correo_practica": str(registro.get("Correo de práctica", "")),
            "horario_del_contacto": str(registro.get("Horario del contacto", "")),
            "fuente_oficial_practica": str(
                registro.get("Fuente oficial de práctica", "")
            ),
            "responsable_actualizacion": str(
                registro.get("Responsable de actualización", "")
            ),
            "ultima_actualizacion": registro.get("Última actualización"),
            "estado_feria": str(registro.get("Estado de la feria", "")),
            "cambios_avisos_practica": str(
                registro.get("Cambios y avisos de práctica", "")
            ),
            "informacion_pendiente": str(registro.get("Información pendiente", "")),
            "regla_asistente": str(registro.get("Regla para el asistente", "")),
            "naturaleza_datos": str(registro.get("Naturaleza de los datos", "")),
            "campos_simulados": str(registro.get("Campos simulados", "")),
        }

        return render_template("detalle.html", actividad=actividad)

    @app.route("/chat", endpoint="chat")
    def pantalla_chat():
        codigo = request.args.get("codigo")
        nombre = request.args.get("nombre")

        actividad_seleccionada = None
        if codigo:
            from app.services.lectura_datos import obtener_actividad_por_codigo

            actividad_seleccionada = obtener_actividad_por_codigo(codigo)

        return render_template(
            "resultados.html",
            actividad_seleccionada=actividad_seleccionada,
            historial=[],
            preguntas_sugeridas=[
                "¿Cuánto cuesta participar?",
                "¿Qué debo llevar?",
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
        contexto = datos.get("codigo")

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
            actividad_seleccionada=None,
            historial=[],
            preguntas_sugeridas=[
                "¿Cuánto cuesta participar?",
                "¿Qué debo llevar?",
            ],
        )

    # ========================================================================
    # Rutas de administración
    # ========================================================================

    @app.route("/admin", endpoint="admin_panel")
    def admin_panel():
        from app.services.lectura_datos import leer_actividades

        datos = leer_actividades()
        actividades = datos["registros"]

        return render_template("inicio.html", actividades=actividades, admin=True)

    return app
