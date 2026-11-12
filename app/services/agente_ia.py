"""
Integración del agente de IA con la llave leída de .env.

Flujo (según AGENTS.md, sección "Coordinación y herramientas propuestas"):
  1. El visitante pregunta.
  2. El agente de consulta identifica o aclara qué actividad y dato se necesitan.
  3. El agente de búsqueda recupera la ficha vigente.
  4. El agente de respuesta redacta una respuesta breve respaldada.
  5. Un controlador en código conserva el contexto y deriva errores.
  6. No debe continuar con una respuesta factual si falló la búsqueda.

La llave de IA se lee de .env (nunca hardcodeada).
"""

import os
import json
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

from app.services.herramientas_ia import buscar_ferias, obtener_ficha, listar_proximas_ferias
from app.services.regla_rb02 import obtener_fecha_referencia
from app.services.regla_rb03_rb04 import identificar_actividad, obtener_proxima_actividad
from app.services.regla_rb05_rb06 import (
    es_pregunta_fuera_de_tema,
    manejar_informacion_faltante,
    formatear_respuesta_con_respaldo,
    obtener_contacto_autorizado,
)
from app.services.regla_rb07_rb08 import evaluar_inscripcion_disponibilidad
from app.utils.formato import formato_fecha, formato_hora, formato_fecha_hora
from app.services.regla_rb09_rb13 import es_accion_fuera_de_alcance, respuesta_accion_fuera_de_alcance

# Cargar variables de entorno desde .env
load_dotenv()

AVISO_SIMULACION = "Demostración con datos simulados"


def obtener_clave_ia() -> Optional[str]:
    """
    Lee la clave de API de IA desde el entorno (.env).
    Nunca se hardcodea ni se muestra en respuestas (RB-09).
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
        tipo: str,  # "identificada", "candidatas", "sin_coincidencias", "fuera_de_alcance", "ambigua"
        actividad: Optional[Dict[str, Any]] = None,
        candidatas: Optional[List[Dict[str, Any]]] = None,
        mensaje_aclaracion: Optional[str] = None,
        campos_solicitados: Optional[List[str]] = None,
    ):
        self.tipo = tipo
        self.actividad = actividad
        self.candidatas = candidatas or []
        self.mensaje_aclaracion = mensaje_aclaracion
        self.campos_solicitados = campos_solicitados or []


def agente_consulta(
    pregunta: str,
    contexto_visible: Optional[str] = None,
    fecha_demo: Optional[str] = None,
) -> ResultadoConsulta:
    """
    Agente de consulta: interpreta la pregunta e identifica qué actividad y dato se necesitan.
    
    Entrada: pregunta, contexto visible de la conversación, fecha de demostración.
    Salida: una de:
      1. Consulta identificada con código y campos solicitados.
      2. Lista de candidatas para aclaración.
      3. Sin coincidencias.
      4. Pregunta fuera del alcance.
    
    Restricción: no inventa una coincidencia ni modifica registros.
    """
    if fecha_demo is None:
        fecha_demo = obtener_fecha_referencia()

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

    # 3. Si es una pregunta sobre "próxima actividad" sin feria específica
    if "próxima" in pregunta_lower or "proxima" in pregunta_lower:
        from app.services.regla_rb03_rb04 import obtener_proxima_actividad
        actividad, candidatas_misma_fecha = obtener_proxima_actividad()
        if actividad is None:
            return ResultadoConsulta(
                tipo="sin_coincidencias",
                mensaje_aclaracion=(
                    "No encontré actividades próximas según la fecha de demostración. "
                    "Puedes consultar las actividades registradas."
                ),
            )
        if candidatas_misma_fecha:
            opciones = "\n".join(
                f"- {c.get('Actividad')} ({c.get('Identificador')}) - {c.get('Lugar')} - {c.get('Fecha de inicio')}"
                for c in candidatas_misma_fecha
            )
            return ResultadoConsulta(
                tipo="ambigua",
                actividad=actividad,
                candidatas=candidatas_misma_fecha,
                mensaje_aclaracion=(
                    f"Varias actividades comparten la primera fecha ({actividad.get('Fecha de inicio')}). "
                    f"¿Cuál te interesa?\n{opciones}"
                ),
            )
        return ResultadoConsulta(
            tipo="identificada",
            actividad=actividad,
            campos_solicitados=["fecha", "lugar", "horario"],
        )

    # 4. Identificar actividad por código, nombre, fecha o lugar
    actividad, candidatas, mensaje = identificar_actividad(pregunta, contexto_visible)
    
    if actividad is None and candidatas is None and mensaje:
        # Sin coincidencias o pregunta ambigua sin contexto
        if "varias actividades" in mensaje.lower():
            return ResultadoConsulta(
                tipo="ambigua",
                candidatas=candidatas or [],
                mensaje_aclaracion=mensaje,
            )
        return ResultadoConsulta(
            tipo="sin_coincidencias",
            mensaje_aclaracion=mensaje,
        )

    if actividad is None and candidatas:
        # Varias candidatas, pedir aclaración
        return ResultadoConsulta(
            tipo="ambigua",
            candidatas=candidatas,
            mensaje_aclaracion=mensaje,
        )

    # Actividad identificada
    # Inferir campos solicitados de la pregunta
    campos = _inferir_campos_solicitados(pregunta)
    
    return ResultadoConsulta(
        tipo="identificada",
        actividad=actividad,
        campos_solicitados=campos,
    )


def _inferir_campos_solicitados(pregunta: str) -> List[str]:
    """Infere qué campos se solicitan según la pregunta."""
    campos: List[str] = []
    pregunta_lower = pregunta.lower()
    
    mapeo = {
        "cuánto": "costo", "cuanto": "costo", "precio": "costo", "costo": "costo",
        "hora": "horario", "a qué": "horario", "qué hora": "horario",
        "dónde": "lugar", "donde": "lugar", "lugar": "lugar",
        "cuándo": "fecha", "cuando": "fecha", "fecha": "fecha",
        "requisito": "requisitos", "requisitos": "requisitos",
        "equipo": "equipo", "llevar": "equipo",
        "inscribir": "inscripción", "inscripción": "inscripción",
        "cupo": "cupos", "cupos": "cupos", "espacio": "cupos",
        "contacto": "contacto", "consultar": "contacto",
    }
    
    for palabra, campo in mapeo.items():
        if palabra in pregunta_lower and campo not in campos:
            campos.append(campo)
    
    if not campos:
        campos = ["general"]
    
    return campos


# ============================================================================
# Agente de búsqueda
# ============================================================================

class ResultadoBusqueda:
    """Resultado del agente de búsqueda."""
    def __init__(
        self,
        exito: bool,
        ficha: Optional[Dict[str, Any]] = None,
        ultima_actualizacion: Optional[str] = None,
        fecha_verificacion_cupos: Optional[str] = None,
        campos_desconocidos: Optional[List[str]] = None,
        inconsistencias: Optional[List[str]] = None,
        error: Optional[str] = None,
    ):
        self.exito = exito
        self.ficha = ficha or {}
        self.ultima_actualizacion = ultima_actualizacion
        self.fecha_verificacion_cupos = fecha_verificacion_cupos
        self.campos_desconocidos = campos_desconocidos or []
        self.inconsistencias = inconsistencias or []
        self.error = error


def agente_busqueda(
    identificador: str,
    campos_necesarios: Optional[List[str]] = None,
) -> ResultadoBusqueda:
    """
    Agente de búsqueda: recupera los valores de la fuente de trabajo vigente.
    
    Entrada: identificador y campos necesarios.
    Herramientas: obtener_ficha y, para consultas generales, listar_proximas_ferias.
    
    Salida: datos recuperados, campos desconocidos, inconsistencias, código,
    versión o última actualización y fecha de verificación de cupos.
    
    Restricción: si una herramienta falla, devuelve un error explícito.
    Aplica la prioridad de datos simulados y no combina valores contradictorios.
    """
    try:
        resultado = obtener_ficha(identificador)
        
        if resultado.get("error"):
            return ResultadoBusqueda(
                exito=False,
                error=resultado["error"],
            )
        
        ficha = resultado.get("ficha", {})
        
        # Si se solicitan campos específicos, verificar si están disponibles
        if campos_necesarios:
            campos_faltantes = []
            for campo in campos_necesarios:
                if campo not in ficha or ficha[campo] is None or str(ficha[campo]).strip() == "":
                    campos_faltantes.append(campo)
            # Los campos faltantes se reportan como desconocidos
            resultado["campos_desconocidos"] = list(
                set(resultado.get("campos_desconocidos", []) + campos_faltantes)
            )
        
        return ResultadoBusqueda(
            exito=True,
            ficha=ficha,
            ultima_actualizacion=resultado.get("ultima_actualizacion"),
            fecha_verificacion_cupos=resultado.get("fecha_verificacion_cupos"),
            campos_desconocidos=resultado.get("campos_desconocidos", []),
            inconsistencias=resultado.get("inconsistencias", []),
            error=None,
        )
    
    except Exception as e:
        return ResultadoBusqueda(
            exito=False,
            error=str(e),
        )


def buscar_proximas_actividades(
    fecha_referencia: Optional[str] = None,
    filtros: Optional[Dict[str, Optional[str]]] = None,
) -> ResultadoBusqueda:
    """
    Busca próximas actividades para consultas generales sin identificador específico.
    Usa la herramienta listar_proximas_ferias.
    """
    try:
        if fecha_referencia is None:
            from app.services.regla_rb02 import obtener_fecha_referencia
            fecha_referencia = obtener_fecha_referencia()
        
        resultado = listar_proximas_ferias(
            fecha_referencia=fecha_referencia,
            filtros=filtros,
        )
        
        if resultado.get("error"):
            return ResultadoBusqueda(
                exito=False,
                error=resultado["error"],
            )
        
        return ResultadoBusqueda(
            exito=True,
            ficha={"actividades": resultado.get("actividades", [])},
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
        referencia_registro: Optional[str] = None,
        es_practica: bool = False,
    ):
        self.texto = texto
        self.referencia_registro = referencia_registro
        self.es_practica = es_practica


def agente_respuesta(
    pregunta: str,
    datos_recuperados: Optional[Dict[str, Any]] = None,
    estado_aclaracion: Optional[str] = None,
    estado_error: Optional[str] = None,
) -> ResultadoRespuesta:
    """
    Agente de respuesta: redacta una respuesta breve y respaldada.
    
    Entrada: pregunta, datos recuperados y estados de aclaración o error.
    Reglas: aplica las reglas del insumo 2 (RB-02 a RB-10) para inscripción,
    plazos, cupos y actividades canceladas.
    
    Salida: texto para el visitante y una referencia visible al registro.
    
    Restricción: si falta información, lo explica; si la consulta es ambigua,
    pide aclaración. No afirma reservas, pagos ni inscripciones y no rellena
    valores con conocimiento general.
    """
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
    if not datos_recuperados or not datos_recuperados.get("ficha"):
        return ResultadoRespuesta(
            texto="No encontré información sobre esa actividad en el registro.",
            referencia_registro=None,
        )
    
    ficha = datos_recuperados["ficha"]
    identificador = ficha.get("Identificador", "No disponible")
    ultima_actualizacion = datos_recuperados.get("ultima_actualizacion")
    
    # Construir referencia visible al registro
    referencia = f"Código: {identificador}"
    if ultima_actualizacion:
        referencia += f" | Última actualización: {ultima_actualizacion}"
    
    # Verificar si hay campos desconocidos relevantes
    campos_desconocidos = datos_recuperados.get("campos_desconocidos", [])
    inconsistencias = datos_recuperados.get("inconsistencias", [])
    
    # Construir respuesta basada en la pregunta
    pregunta_lower = pregunta.lower()
    
    # Detectar tipo de consulta
    texto_respuesta = _construir_texto_respuesta(
        pregunta_lower, ficha, datos_recuperados
    )
    
    # Añadir información sobre campos desconocidos si es relevante
    if campos_desconocidos:
        campos_txt = ", ".join(campos_desconocidos[:3])
        texto_respuesta += f"\n\nNota: No consta en el registro: {campos_txt}."
    
    # Añadir inconsistencias si las hay
    if inconsistencias:
        texto_respuesta += f"\n\nObservación: Se detectó una inconsistencia: {inconsistencias[0]}."
    
    # Aplicar formateo con respaldo (RB-05/RB-06)
    from app.services.regla_rb05_rb06 import formatear_respuesta_con_respaldo
    texto_final = formatear_respuesta_con_respaldo(
        respuesta_texto=texto_respuesta,
        registro=ficha,
        es_practica=True,
        incluir_verificacion_cupos=bool(datos_recuperados.get("fecha_verificacion_cupos")),
    )
    
    return ResultadoRespuesta(
        texto=texto_final,
        referencia_registro=referencia,
        es_practica=True,
    )


def _construir_texto_respuesta(
    pregunta_lower: str,
    ficha: Dict[str, Any],
    datos_recuperados: Dict[str, Any],
) -> str:
    """Construye el texto de la respuesta según el tipo de consulta."""
    
    # Consulta sobre costo
    if any(p in pregunta_lower for p in ["cuánto", "cuanto", "costo", "precio", "pagar"]):
        costo = ficha.get("Costo de participación", "No disponible")
        moneda = ficha.get("Moneda", "")
        unidad = ficha.get("Unidad de cobro", "")
        incluye = ficha.get("Incluye el costo", "")
        if costo and str(costo).strip() not in ("", "Por confirmar", "Por definir", "No indicado"):
            partes = [f"El costo es de {costo}"]
            if moneda:
                partes.append(f"{moneda}")
            if unidad:
                partes.append(f"por {unidad}")
            if incluye:
                partes.append(f". Incluye: {incluye}")
            return " ".join(partes) + "."
        return "No consta el costo de participación en el registro."
    
    # Consulta sobre montaje (debe ir antes que horario, porque "hora" también aparece en "¿a qué hora llego a montar?")
    if any(p in pregunta_lower for p in ["montar", "montaje", "ingreso", "llego"]):
        montaje = ficha.get("Ingreso y montaje", "")
        atencion = ficha.get("Inicio de atención simulado", "")
        if montaje:
            partes = [f"El ingreso y montaje es a las {formato_hora(montaje)}."]
            if atencion:
                partes.append(f" La atención empieza a las {formato_hora(atencion)}.")
            return "".join(partes)
        return "No consta el horario de ingreso y montaje en el registro."

    # Consulta sobre horario de atención
    if any(p in pregunta_lower for p in ["a qué hora", "qué hora", "horario de atención", "empieza", "inicia"]):
        inicio = ficha.get("Inicio de atención simulado", "")
        cierre = ficha.get("Cierre de atención simulado", "")
        if inicio and cierre:
            return f"El horario de atención es de {formato_hora(inicio)} a {formato_hora(cierre)}."
        if inicio:
            return f"El inicio de atención es a las {formato_hora(inicio)}."
        return "No consta el horario de atención en el registro."
    
    # Consulta sobre desmontaje
    if any(p in pregunta_lower for p in ["desmontar", "desmontaje", "salida", "retiro", "retirar"]):
        desmontaje = ficha.get("Salida y desmontaje", "")
        if desmontaje:
            return f"La salida y desmontaje es a las {formato_hora(desmontaje)}."
        return "No consta el horario de salida y desmontaje en el registro."
    
    # Consulta sobre ubicación
    if any(p in pregunta_lower for p in ["dónde", "donde", "lugar", "dirección", "direccion"]):
        lugar = ficha.get("Lugar", "")
        direccion = ficha.get("Dirección exacta de práctica", "")
        acceso = ficha.get("Acceso y parqueo", "")
        partes = []
        if lugar:
            partes.append(f"El lugar es {lugar}.")
        if direccion:
            partes.append(f" Dirección: {direccion}.")
        if acceso:
            partes.append(f" Acceso: {acceso}.")
        if partes:
            return " ".join(partes)
        return "No consta la ubicación en el registro."
    
    # Consulta sobre cupos/inscripción
    if any(p in pregunta_lower for p in ["cupo", "espacio", "inscribir", "disponible", "campo"]):
        from datetime import datetime
        from app.services.regla_rb07_rb08 import evaluar_inscripcion_disponibilidad
        
        fecha_ref = datetime.fromisoformat(obtener_fecha_referencia())
        evaluacion = evaluar_inscripcion_disponibilidad(ficha, fecha_ref)
        return evaluacion["mensaje"]
    
    # Consulta sobre contacto
    if any(p in pregunta_lower for p in ["contacto", "consultar con", "quién", "quien"]):
        from app.services.regla_rb05_rb06 import obtener_contacto_autorizado
        contacto = obtener_contacto_autorizado(ficha)
        if contacto:
            return (
                f"El contacto autorizado es {contacto['nombre']} ({contacto['cargo']}). "
                f"Teléfono: {contacto['telefono']}. "
                f"Correo: {contacto['correo']}. "
                f"Horario: {contacto['horario']}."
            )
        return "No consta un contacto autorizado en el registro."
    
    # Consulta sobre fecha
    if any(p in pregunta_lower for p in ["qué día", "qué día es", "fecha", "cuándo", "cuando"]):
        fecha = ficha.get("Fecha de inicio", "")
        if fecha:
            return f"La actividad está programada para el {formato_fecha(fecha)}."
        return "No consta la fecha de inicio en el registro."
    
    # Consulta general
    actividad = ficha.get("Actividad", "Esta actividad")
    lugar = ficha.get("Lugar", "")
    fecha = ficha.get("Fecha de inicio", "")
    partes = [f"Información sobre {actividad}."]
    if fecha:
        partes.append(f" Fecha: {formato_fecha(fecha)}.")
    if lugar:
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
    fecha_demo: Optional[str] = None,
) -> ResultadoFlujo:
    """
    Controlador que ejecuta el flujo completo:
    consulta → búsqueda → respuesta.
    
    Restricción del sistema: No debe continuar con una respuesta factual
    si falló la búsqueda.
    """
    if fecha_demo is None:
        fecha_demo = obtener_fecha_referencia()
    
    # Paso 1: Agente de consulta
    resultado_consulta = agente_consulta(pregunta, contexto_visible, fecha_demo)
    
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
    
    # Paso 2: Agente de búsqueda (solo si se identificó una actividad)
    if resultado_consulta.tipo != "identificada" or not resultado_consulta.actividad:
        return ResultadoFlujo(
            texto_respuesta="No pude identificar la actividad a consultar. ¿Podrías indicarme el nombre, código, fecha o lugar?",
            tipo_consulta="error_identificacion",
            exito=False,
        )
    
    identificador = resultado_consulta.actividad.get("Identificador")
    campos = resultado_consulta.campos_solicitados
    
    resultado_busqueda = agente_busqueda(identificador, campos)
    
    # Paso 3: Verificar si falló la búsqueda - NO continuar con respuesta factual
    if not resultado_busqueda.exito:
        return ResultadoFlujo(
            texto_respuesta=(
                "No fue posible recuperar los datos de la actividad. "
                "Por favor, inténtalo de nuevo más tarde."
            ),
            tipo_consulta="error_busqueda",
            exito=False,
            error=resultado_busqueda.error,
        )
    
    # Paso 4: Agente de respuesta
    datos_para_respuesta = {
        "ficha": resultado_busqueda.ficha,
        "ultima_actualizacion": resultado_busqueda.ultima_actualizacion,
        "fecha_verificacion_cupos": resultado_busqueda.fecha_verificacion_cupos,
        "campos_desconocidos": resultado_busqueda.campos_desconocidos,
        "inconsistencias": resultado_busqueda.inconsistencias,
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
