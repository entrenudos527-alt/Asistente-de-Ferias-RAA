"""
Integración del agente de IA con la llave leída de .env.

Flujo (según AGENTS.md, sección "Coordinación y herramientas propuestas"):
  1. El visitante pregunta.
  2. El agente de consulta identifica o aclara qué evento y dato se necesitan.
  3. El agente de búsqueda recupera los datos del evento vigente.
  4. El agente de respuesta redacta una respuesta breve respaldada.
  5. Un controlador en código conserva el contexto y deriva errores.
  6. No debe continuar con una respuesta factual si falló la búsqueda.

La llave de IA se lee de .env (nunca hardcodeada).
"""

import os
import re
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

from app.services.herramientas_ia import buscar_eventos, obtener_evento
from app.services.regla_rb05_rb06 import (
    es_pregunta_fuera_de_tema,
    manejar_informacion_faltante,
    formatear_respuesta_con_respaldo,
    obtener_contacto_autorizado,
)

# Cargar variables de entorno desde .env
load_dotenv()

AVISO_SIMULACION = "Información basada en datos de la Red Alajuelita Artesanal"


def obtener_clave_ia() -> Optional[str]:
    """
    Lee la clave de API de IA desde el entorno (.env).
    Nunca se hardcodea ni se muestra en respuestas.
    """
    clave = os.environ.get("API_IA_CLAVE")
    if clave and clave != "tu_clave_aqui":
        return clave
    return None


def clave_ia_configurada() -> bool:
    """Devuelve True si existe una clave de IA configurada."""
    return obtener_clave_ia() is not None


# ============================================================================
# Agente de consulta
# ============================================================================

class ResultadoConsulta:
    """Resultado del agente de consulta."""
    def __init__(
        self,
        tipo: str,
        evento: Optional[Dict[str, Any]] = None,
        candidatas: Optional[List[Dict[str, Any]]] = None,
        mensaje_aclaracion: Optional[str] = None,
        campos_solicitados: Optional[List[str]] = None,
    ):
        self.tipo = tipo
        self.evento = evento
        self.candidatas = candidatas or []
        self.mensaje_aclaracion = mensaje_aclaracion
        self.campos_solicitados = campos_solicitados or []


def agente_consulta(
    pregunta: str,
    contexto_visible: Optional[str] = None,
) -> ResultadoConsulta:
    """
    Agente de consulta: interpreta la pregunta e identifica qué evento y dato se necesitan.

    Entrada: pregunta, contexto visible de la conversación.
    Salida: una de:
      1. Consulta identificada con código y campos solicitados.
      2. Lista de candidatas para aclaración.
      3. Sin coincidencias.
      4. Pregunta fuera del alcance.

    Restricción: no inventa una coincidencia ni modifica registros.
    """
    pregunta_lower = pregunta.strip().lower()

    # 1. Detectar si es una acción fuera del alcance (reservar, pagar, inscribir, etc.)
    from app.services.regla_rb09_rb13 import es_accion_fuera_de_alcance, respuesta_accion_fuera_de_alcance
    if es_accion_fuera_de_alcance(pregunta):
        return ResultadoConsulta(
            tipo="fuera_de_alcance",
            mensaje_aclaracion=respuesta_accion_fuera_de_alcance(),
        )

    # 2. Detectar pregunta fuera del tema (compradores, ganancias, clima, etc.)
    fuera_de_tema, campo = es_pregunta_fuera_de_tema(pregunta)
    if fuera_de_tema:
        return ResultadoConsulta(
            tipo="fuera_de_alcance",
            mensaje_aclaracion=(
                f"No puedo estimar {campo} porque no está registrado en los datos disponibles. "
                f"No buscaré fuera del conjunto de datos en esta versión."
            ),
        )

    # 3. Identificar evento por nombre
    evento, candidatas, mensaje = identificar_evento(pregunta, contexto_visible)

    if evento is None and candidatas is None and mensaje:
        if "varios eventos" in mensaje.lower():
            return ResultadoConsulta(
                tipo="ambigua",
                candidatas=candidatas or [],
                mensaje_aclaracion=mensaje,
            )
        return ResultadoConsulta(
            tipo="sin_coincidencias",
            mensaje_aclaracion=mensaje,
        )

    if evento is None and candidatas:
        return ResultadoConsulta(
            tipo="ambigua",
            candidatas=candidatas,
            mensaje_aclaracion=mensaje,
        )

    # Evento identificado
    campos = _inferir_campos_solicitados(pregunta)

    return ResultadoConsulta(
        tipo="identificada",
        evento=evento,
        campos_solicitados=campos,
    )


def _inferir_campos_solicitados(pregunta: str) -> List[str]:
    """Infere qué campos se solicitan según la pregunta."""
    campos: List[str] = []
    pregunta_lower = pregunta.lower()

    mapeo = {
        "cuándo": "fecha", "cuando": "fecha", "fecha": "fecha",
        "dónde": "lugar", "donde": "lugar", "lugar": "lugar",
        "hora": "horario", "a qué hora": "horario", "qué hora": "horario",
        "cuánto": "costo", "cuanto": "costo", "precio": "costo", "costo": "costo",
        "cuánto cuesta": "costo",
        "cupo": "cupos", "cupos": "cupos", "espacio": "cupos",
        "contacto": "contacto", "coordinador": "contacto",
        "inscribir": "inscripción", "inscripción": "inscripción",
        "requisito": "requisitos", "requisitos": "requisitos",
        "equipo": "equipo", "llevar": "equipo",
        "parqueo": "parqueo", "toldo": "toldo",
        "alimentación": "alimentación", "comer": "alimentación",
        "acompañante": "acompañante",
    }

    for palabra, campo in mapeo.items():
        if palabra in pregunta_lower and campo not in campos:
            campos.append(campo)

    if not campos:
        campos = ["general"]

    return campos


def identificar_evento(
    consulta: str, contexto_actual: Optional[str] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[List[Dict[str, Any]]], str]:
    """
    Identifica un evento a partir de una consulta del usuario.

    Args:
        consulta: texto de la pregunta del usuario.
        contexto_actual: nombre de evento ya seleccionado en la conversación.

    Returns:
        (evento_identificado, lista_candidatas, mensaje_aclaracion)
    """
    from app.services.lectura_eventos import leer_eventos, obtener_evento_por_nombre

    datos = leer_eventos()
    consulta_lower = consulta.strip().lower()

    # Si hay contexto de un evento previamente seleccionado
    if contexto_actual:
        for registro in datos["registros"]:
            nombre = str(registro.get("Nombre del evento", ""))
            if nombre.lower() == contexto_actual.lower():
                return registro, None, ""

    # Búsqueda por nombre exacto
    for registro in datos["registros"]:
        nombre = str(registro.get("Nombre del evento", ""))
        if nombre.lower() == consulta_lower:
            return registro, None, ""

    # Búsqueda por nombre contenido en consulta o viceversa
    coincidencias: List[Dict[str, Any]] = []
    vistos = set()
    for registro in datos["registros"]:
        nombre = str(registro.get("Nombre del evento", ""))
        nombre_lower = nombre.lower()
        if consulta_lower in nombre_lower or nombre_lower in consulta_lower:
            if nombre not in vistos:
                coincidencias.append(registro)
                vistos.add(nombre)

    if len(coincidencias) == 0:
        return None, None, (
            "No encontramos un evento que coincida con tu consulta. "
            "Puedes consultar los eventos registrados por nombre, fecha o lugar."
        )

    if len(coincidencias) == 1:
        return coincidencias[0], None, ""

    # Varias coincidencias: pedir aclaración
    opciones = "\n".join(
        f"- {r.get('Nombre del evento')} ({r.get('Tipo de evento')}) - {r.get('Lugar del evento')} - {r.get('Fecha de inicio')}"
        for r in coincidencias
    )
    mensaje = (
        f"Se encontraron varios eventos que coinciden con tu consulta. "
        f"Indica cuál te interesa:\n{opciones}"
    )
    return None, coincidencias, mensaje


# ============================================================================
# Agente de búsqueda
# ============================================================================

class ResultadoBusqueda:
    """Resultado del agente de búsqueda."""
    def __init__(
        self,
        exito: bool,
        evento: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        self.exito = exito
        self.evento = evento or {}
        self.error = error


def agente_busqueda(
    nombre_evento: str,
) -> ResultadoBusqueda:
    """
    Agente de búsqueda: recupera los valores de la fuente de trabajo vigente.

    Entrada: identificador (nombre) del evento.
    Herramienta: obtener_evento.

    Salida: datos del evento o error explícito si falla.

    Restricción: si la herramienta falla, devuelve un error explícito.
    """
    try:
        resultado = obtener_evento(nombre_evento)

        if resultado.get("error"):
            return ResultadoBusqueda(
                exito=False,
                error=resultado["error"],
            )

        return ResultadoBusqueda(
            exito=True,
            evento=resultado.get("evento", {}),
            error=None,
        )

    except Exception as e:
        return ResultadoBusqueda(
            exito=False,
            error=str(e),
        )


# ============================================================================
# Agente de respuesta
# ============================================================================

class ResultadoRespuesta:
    """Resultado del agente de respuesta."""
    def __init__(
        self,
        texto: str,
        referencia_evento: Optional[str] = None,
    ):
        self.texto = texto
        self.referencia_registro = referencia_evento


def agente_respuesta(
    pregunta: str,
    datos_recuperados: Optional[Dict[str, Any]] = None,
    estado_aclaracion: Optional[str] = None,
    estado_error: Optional[str] = None,
) -> ResultadoRespuesta:
    """
    Agente de respuesta: redacta una respuesta breve y respaldada.

    Entrada: pregunta, datos recuperados y estados de aclaración o error.
    Salida: texto para el visitante y una referencia visible al registro.

    Restricción: si falta información, lo explica; si la consulta es ambigua,
    pide aclaración. No afirma reservas, pagos ni inscripciones y no rellena
    valores con conocimiento general.
    """
    from app.utils.formato import (
        formatear_fecha,
        formatear_hora,
        formatear_fecha_hora,
        formatear_monto,
        formatear_rango_fechas,
    )
    from app.services.regla_rb05_rb06 import (
        es_valor_desconocido,
        obtener_contacto_autorizado,
    )

    # 1. Si hubo error en la búsqueda, no continuar con respuesta factual
    if estado_error:
        return ResultadoRespuesta(
            texto=(
                "No fue posible recuperar los datos solicitados. "
                "Por favor, inténtalo de nuevo más tarde."
            ),
            referencia_registro=None,
        )

    # 2. Si hay estado de aclaración (ambigua, sin coincidencias, fuera de alcance)
    if estado_aclaracion:
        return ResultadoRespuesta(
            texto=estado_aclaracion,
            referencia_registro=None,
        )

    # 3. Si no hay datos recuperados
    if not datos_recuperados or not datos_recuperados.get("evento"):
        return ResultadoRespuesta(
            texto="No encontré información sobre ese evento en el registro.",
            referencia_registro=None,
        )

    evento = datos_recuperados["evento"]
    nombre = evento.get("Nombre del evento", "No disponible")
    tipo = evento.get("Tipo de evento", "")
    lugar = evento.get("Lugar del evento", "")
    fecha_inicio = evento.get("Fecha de inicio")
    fecha_fin = evento.get("Fecha de finalización")
    hora_inicio = evento.get("Hora de inicio del evento")
    hora_fin = evento.get("Hora finalización del evento")
    hora_montaje = evento.get("Hora de montaje")
    hora_desmontaje = evento.get("Hora de desmontaje")

    # Construir referencia visible al registro
    referencia = f"Evento: {nombre}"

    # Construir respuesta basada en la pregunta
    pregunta_lower = pregunta.lower()
    texto_respuesta = _construir_texto_respuesta(
        pregunta_lower, evento
    )

    # Aplicar formateo con respaldo
    texto_final = formatear_respuesta_con_respaldo(
        respuesta_texto=texto_respuesta,
        evento=evento,
    )

    return ResultadoRespuesta(
        texto=texto_final,
        referencia_registro=referencia,
    )


def _construir_texto_respuesta(
    pregunta_lower: str,
    evento: Dict[str, Any],
) -> str:
    """Construye el texto de la respuesta según el tipo de consulta."""
    from app.utils.formato import (
        formatear_fecha,
        formatear_hora,
        formatear_fecha_hora,
        formatear_monto,
        formatear_rango_fechas,
    )

    # Consulta sobre fecha
    if any(p in pregunta_lower for p in ["cuándo", "cuando", "fecha", "día", "día es"]):
        fecha_inicio = evento.get("Fecha de inicio")
        fecha_fin = evento.get("Fecha de finalización")
        if fecha_inicio:
            rango = formatear_rango_fechas(fecha_inicio, fecha_fin)
            return f"El evento está programado para el {rango}."
        return "No consta la fecha de inicio en el registro."

    # Consulta sobre horario
    if any(p in pregunta_lower for p in ["a qué hora", "qué hora", "horario", "empieza", "inicia", "montaje", "desmontaje"]):
        partes = []
        hi = evento.get("Hora de inicio del evento")
        hf = evento.get("Hora finalización del evento")
        hm = evento.get("Hora de montaje")
        hd = evento.get("Hora de desmontaje")

        if any(p in pregunta_lower for p in ["montaje", "ingreso", "llego"]) and hm:
            partes.append(f"El ingreso y montaje es a las {formatear_hora(hm)}.")
        if any(p in pregunta_lower for p in ["desmontaje", "salida", "retiro"]) and hd:
            partes.append(f"La salida y desmontaje es a las {formatear_hora(hd)}.")

        if hi and hf and not any(p in pregunta_lower for p in ["montaje", "desmontaje", "ingreso", "salida", "retiro"]):
            partes.append(f"El horario del evento es de {formatear_hora(hi)} a {formatear_hora(hf)}.")
        elif hi and not any(p in pregunta_lower for p in ["montaje", "desmontaje", "ingreso", "salida", "retiro"]):
            partes.append(f"El evento empieza a las {formatear_hora(hi)}.")

        if partes:
            return " ".join(partes)

        return "No consta el horario en el registro."

    # Consulta sobre lugar
    if any(p in pregunta_lower for p in ["dónde", "donde", "lugar", "dirección", "direccion"]):
        lugar = evento.get("Lugar del evento", "")
        direccion = evento.get("Dirección exacta", "")
        partes = []
        if lugar and not es_valor_desconocido(lugar):
            partes.append(f"El lugar es {lugar}.")
        if direccion and not es_valor_desconocido(direccion):
            partes.append(f" Dirección exacta: {direccion}.")
        if partes:
            return " ".join(partes)
        return "No consta la ubicación en el registro."

    # Consulta sobre costo
    if any(p in pregunta_lower for p in ["cuánto", "cuanto", "costo", "precio", "pagar", "donación", "donacion"]):
        costo = evento.get("Costo de participación", "")
        donacion = evento.get("Donación monetaria", "")
        partes = []
        if costo and not es_valor_desconocido(costo):
            monto = formatear_monto(costo)
            if monto:
                partes.append(f"El costo de participación es {monto}.")
        if donacion and not es_valor_desconocido(donacion):
            monto_d = formatear_monto(donacion)
            if monto_d:
                partes.append(f" La donación sugerida es {monto_d}.")
        if partes:
            return " ".join(partes)
        return "No consta el costo de participación en el registro."

    # Consulta sobre cupos/inscripción
    if any(p in pregunta_lower for p in ["cupo", "espacio", "inscribir", "disponible", "campo", "inscripción"]):
        estado = evento.get("Quiénes pueden inscribirse", "")
        cupos_totales = evento.get("Cantidad total de cupos", "")
        cupos_disp = evento.get("Cupos disponibles", "")
        fecha_limite = evento.get("Fecha límite de inscripción", "")

        partes = []
        if estado and not es_valor_desconocido(estado):
            partes.append(f"Quiénes pueden inscribirse: {estado}.")
        if cupos_totales and not es_valor_desconocido(cupos_totales):
            partes.append(f" Total de cupos: {cupos_totales}.")
        if cupos_disp and not es_valor_desconocido(cupos_disp):
            partes.append(f" Cupos disponibles: {cupos_disp}.")
        if fecha_limite and not es_valor_desconocido(fecha_limite):
            partes.append(f" Fecha límite de inscripción: {formatear_fecha(fecha_limite)}.")

        if partes:
            return " ".join(partes)
        return "No consta información de inscripción o cupos en el registro."

    # Consulta sobre contacto
    if any(p in pregunta_lower for p in ["contacto", "coordinador", "quién", "quien", "consultar con"]):
        contacto = evento.get("Coordinador del evento", "")
        whatsapp = evento.get("WhatsApp de coordinación", "")
        partes = []
        if contacto and not es_valor_desconocido(contacto):
            partes.append(f"El coordinador es {contacto}.")
        if whatsapp and not es_valor_desconocido(whatsapp):
            partes.append(f" WhatsApp: {whatsapp}.")
        if partes:
            return " ".join(partes)
        return "No consta un contacto autorizado en el registro."

    # Consulta sobre facilidades (parqueo, toldo, acompañante, alimentación)
    if any(p in pregunta_lower for p in ["parqueo", "toldo", "acompañante", "acompanante", "alimentación", "alimentacion", "comer", "calentar", "almuerzo", "stand"]):
        partes = []
        parqueo = evento.get("Parqueo disponible", "")
        toldo = evento.get("Debe llevar toldo", "")
        acompanante = evento.get("Se permite acompañante", "")
        calentar = evento.get("Lugar para calentar alimentos", "")
        almorzar = evento.get("Lugar para almorzar", "")
        comer_stand = evento.get("Se permite comer en el stand", "")

        if parqueo and not es_valor_desconocido(parqueo):
            partes.append(f"Parqueo: {parqueo}.")
        if toldo and not es_valor_desconocido(toldo):
            partes.append(f"Toldo: {toldo}.")
        if acompanante and not es_valor_desconocido(acompanante):
            partes.append(f"Acompañante: {acompanante}.")
        if calentar and not es_valor_desconocido(calentar):
            partes.append(f"Calentar alimentos: {calentar}.")
        if almorzar and not es_valor_desconocido(almorzar):
            partes.append(f"Lugar para almorzar: {almorzar}.")
        if comer_stand and not es_valor_desconocido(comer_stand):
            partes.append(f"Comer en el stand: {comer_stand}.")

        if partes:
            return " ".join(partes)
        return "No consta información sobre facilidades en el registro."

    # Consulta sobre manejo del stand
    if any(p in pregunta_lower for p in ["manejo del stand", "mercadería", "mercaderia", "entre días", "entre dias"]):
        manejo = evento.get("Manejo del stand y la mercadería entre días", "")
        if manejo and not es_valor_desconocido(manejo):
            return f"Manejo del stand y mercadería: {manejo}."
        return "No consta información sobre manejo del stand en el registro."

    # Consulta general
    actividad = evento.get("Nombre del evento", "Este evento")
    tipo_ev = evento.get("Tipo de evento", "")
    lugar = evento.get("Lugar del evento", "")
    fecha = evento.get("Fecha de inicio", "")
    partes = [f"Información sobre {actividad}."]
    if tipo_ev and not es_valor_desconocido(tipo_ev):
        partes.append(f" Tipo: {tipo_ev}.")
    if fecha:
        partes.append(f" Fecha: {formatear_fecha(fecha)}.")
    if lugar and not es_valor_desconocido(lugar):
        partes.append(f" Lugar: {lugar}.")
    return " ".join(partes)


# ============================================================================
# Controlador: flujo completo consulta → búsqueda → respuesta
# ============================================================================

class ResultadoFlujo:
    """Resultado completo del flujo del agente de IA."""
    def __init__(
        self,
        texto_respuesta: str,
        referencia_registro: Optional[str] = None,
        tipo_consulta: str = "general",
        exito: bool = True,
        error: Optional[str] = None,
    ):
        self.texto_respuesta = texto_respuesta
        self.referencia_registro = referencia_registro
        self.tipo_consulta = tipo_consulta
        self.exito = exito
        self.error = error


def procesar_pregunta(
    pregunta: str,
    contexto_visible: Optional[str] = None,
) -> ResultadoFlujo:
    """
    Controlador que ejecuta el flujo completo:
    consulta → búsqueda → respuesta.

    Restricción del sistema: No debe continuar con una respuesta factual
    si falló la búsqueda.
    """
    # Paso 1: Agente de consulta
    resultado_consulta = agente_consulta(pregunta, contexto_visible)

    # Manejar casos especiales del agente de consulta
    if resultado_consulta.tipo == "fuera_de_alcance":
        return ResultadoFlujo(
            texto_respuesta=resultado_consulta.mensaje_aclaracion or "",
            tipo_consulta="fuera_de_alcance",
            exito=True,
        )

    if resultado_consulta.tipo == "sin_coincidencias":
        return ResultadoFlujo(
            texto_respuesta=resultado_consulta.mensaje_aclaracion or "",
            tipo_consulta="sin_coincidencias",
            exito=True,
        )

    if resultado_consulta.tipo == "ambigua":
        return ResultadoFlujo(
            texto_respuesta=resultado_consulta.mensaje_aclaracion or "",
            tipo_consulta="ambigua",
            exito=True,
        )

    # Paso 2: Agente de búsqueda (solo si se identificó un evento)
    if resultado_consulta.tipo != "identificada" or not resultado_consulta.evento:
        return ResultadoFlujo(
            texto_respuesta="No pude identificar el evento a consultar. ¿Podrías indicarme el nombre del evento?",
            tipo_consulta="error_identificacion",
            exito=False,
        )

    nombre_evento = resultado_consulta.evento.get("Nombre del evento")

    resultado_busqueda = agente_busqueda(nombre_evento)

    # Paso 3: Verificar si falló la búsqueda - NO continuar con respuesta factual
    if not resultado_busqueda.exito:
        return ResultadoFlujo(
            texto_respuesta=(
                "No fue posible recuperar los datos del evento. "
                "Por favor, inténtalo de nuevo más tarde."
            ),
            tipo_consulta="error_busqueda",
            exito=False,
            error=resultado_busqueda.error,
        )

    # Paso 4: Agente de respuesta
    datos_para_respuesta = {
        "evento": resultado_busqueda.evento,
    }

    resultado_respuesta = agente_respuesta(
        pregunta=pregunta,
        datos_recuperados=datos_para_respuesta,
    )

    return ResultadoFlujo(
        texto_respuesta=resultado_respuesta.texto,
        referencia_registro=resultado_respuesta.referencia_registro,
        tipo_consulta="identificada",
        exito=True,
    )
