"""
Reglas RB-03 y RB-04.

RB-03: Próxima actividad
- Buscar la fecha de inicio más cercana que sea igual o posterior a la fecha de referencia,
  excluyendo actividades canceladas y finalizadas.
- Si varias actividades comparten la primera fecha, mencionarlas o pedir cuál interesa.

RB-04: Identificar la actividad
- Buscar por código, nombre, fecha o lugar.
- Conservar como contexto la actividad que la persona seleccionó o aclaró.
- Si una pregunta permite identificar varias actividades, pedir aclaración antes de responder
  costos, horarios, cupos o requisitos.
- No elegir una actividad por defecto.
- El identificador de una prueba no cuenta como contexto del chat salvo que la persona
  haya seleccionado esa actividad.
- Si no hay coincidencias, decirlo y ofrecer consultar las actividades registradas.
- Si la persona cambia de feria, actualizar el contexto.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.services.lectura_datos import leer_actividades
from app.services.regla_rb02 import obtener_fecha_referencia

# Encabezados clave del Excel
ENC_IDENTIFICADOR = "Identificador"
ENC_ACTIVIDAD = "Actividad"
ENC_LUGAR = "Lugar"
ENC_FECHA_INICIO = "Fecha de inicio"
ENC_ESTADO = "Estado de la feria"

# Estados que excluyen de "próxima actividad"
ESTADOS_EXCLUIDOS = {"cancelada", "finalizada"}


def _parse_fecha(valor) -> Optional[datetime]:
    """Convierte un valor de fecha (datetime o string) a datetime. Devuelve None si no se puede."""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, str):
        try:
            return datetime.fromisoformat(valor)
        except ValueError:
            return None
    return None


def _estado_es_valido(registro: dict) -> bool:
    """Devuelve True si el estado de la feria no está excluido (no cancelada ni finalizada)."""
    estado = str(registro.get(ENC_ESTADO, "")).strip().lower()
    return estado not in ESTADOS_EXCLUIDOS


def obtener_proxima_actividad() -> Tuple[Optional[dict], List[dict]]:
    """
    Busca la próxima actividad a partir de la fecha fija de demostración.
    Excluye actividades canceladas y finalizadas.

    Returns:
        (actividad_principal, candidatas_misma_fecha)
        - actividad_principal: la primera actividad encontrada o None.
        - candidatas_misma_fecha: otras actividades que comparten la misma fecha de inicio.
    """
    datos = leer_actividades()
    fecha_ref_str = obtener_fecha_referencia()
    fecha_ref = datetime.fromisoformat(fecha_ref_str)

    # Filtrar actividades no excluidas y con fecha válida >= fecha_ref
    candidatas: List[dict] = []
    for registro in datos["registros"]:
        if not _estado_es_valido(registro):
            continue
        fecha_inicio = _parse_fecha(registro.get(ENC_FECHA_INICIO))
        if fecha_inicio is None:
            continue
        if fecha_inicio >= fecha_ref:
            candidatas.append(registro)

    if not candidatas:
        return None, []

    # Ordenar por fecha de inicio
    candidatas.sort(key=lambda r: _parse_fecha(r.get(ENC_FECHA_INICIO)))

    primera_fecha = _parse_fecha(candidatas[0].get(ENC_FECHA_INICIO))
    misma_fecha: List[dict] = []
    for registro in candidatas:
        f = _parse_fecha(registro.get(ENC_FECHA_INICIO))
        if f == primera_fecha:
            misma_fecha.append(registro)

    return misma_fecha[0], misma_fecha[1:]


def identificar_actividad(
    consulta: str, contexto_actual: Optional[str] = None
) -> Tuple[Optional[dict], Optional[List[dict]], str]:
    """
    Identifica una actividad a partir de una consulta del usuario.

    Args:
        consulta: texto de la pregunta del usuario.
        contexto_actual: código de actividad ya seleccionado en la conversación, si existe.

    Returns:
        (actividad_identificada, lista_candidatas, mensaje_aclaracion)
        - actividad_identificada: dict con los datos o None.
        - lista_candidatas: lista de dicts si hay ambigüedad, o None.
        - mensaje_aclaracion: texto para pedir aclaración, o "" si no se necesita.
    """
    datos = leer_actividades()
    consulta_lower = consulta.strip().lower()

    # Si hay contexto de una actividad previamente seleccionada, intentar usarla
    if contexto_actual:
        for registro in datos["registros"]:
            if str(registro.get(ENC_IDENTIFICADOR, "")).lower() == contexto_actual.lower():
                return registro, None, ""

    # Búsqueda por código exacto
    for registro in datos["registros"]:
        codigo = str(registro.get(ENC_IDENTIFICADOR, ""))
        if codigo.lower() == consulta_lower:
            return registro, None, ""

    # Búsqueda por nombre (la consulta está en el nombre o el nombre en la consulta)
    coincidencias_nombre: List[dict] = []
    for registro in datos["registros"]:
        nombre = str(registro.get(ENC_ACTIVIDAD, ""))
        if consulta_lower in nombre.lower() or nombre.lower() in consulta_lower:
            coincidencias_nombre.append(registro)

    # Búsqueda por lugar (la consulta está en el lugar o el lugar en la consulta)
    coincidencias_lugar: List[dict] = []
    for registro in datos["registros"]:
        lugar = str(registro.get(ENC_LUGAR, ""))
        if consulta_lower in lugar.lower() or lugar.lower() in consulta_lower:
            coincidencias_lugar.append(registro)

    # Combinar coincidencias sin duplicados
    coincidencias: List[dict] = []
    vistos = set()
    for reg in coincidencias_nombre + coincidencias_lugar:
        codigo = str(reg.get(ENC_IDENTIFICADOR, ""))
        if codigo not in vistos:
            coincidencias.append(reg)
            vistos.add(codigo)

    if len(coincidencias) == 0:
        return None, None, (
            "No encontramos una actividad que coincida con tu consulta. "
            "Puedes consultar las actividades registradas por nombre, fecha o lugar."
        )

    if len(coincidencias) == 1:
        return coincidencias[0], None, ""

    # Varias coincidencias: pedir aclaración
    opciones = "\n".join(
        f"- {r.get(ENC_ACTIVIDAD)} ({r.get(ENC_IDENTIFICADOR)}) - {r.get(ENC_LUGAR)} - {r.get(ENC_FECHA_INICIO)}"
        for r in coincidencias
    )
    mensaje = (
        f"Se encontraron varias actividades que coinciden con tu consulta. "
        f"Indica cuál te interesa:\n{opciones}"
    )
    return None, coincidencias, mensaje


def obtener_todas_actividades() -> List[dict]:
    """Devuelve todas las actividades registradas."""
    datos = leer_actividades()
    return datos["registros"]
