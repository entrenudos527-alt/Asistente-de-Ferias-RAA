"""
Reglas RB-07 y RB-08.

RB-07: Inscripción y disponibilidad
- Si el evento tiene información sobre inscripción, mostrarla.
- Si hay cupos disponibles, informar la cantidad.
- Si falta el estado, el plazo o la verificación de cupos, no asegurar disponibilidad.

RB-08: Actualizaciones y administración
- Solo la persona administradora podrá crear o modificar eventos.
- El chat del visitante no modifica fechas, costos, cupos ni estados.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Encabezados clave del Excel
ENC_ESTADO_INSCRIPCION = "Quiénes pueden inscribirse"
ENC_FECHA_LIMITE_INSCRIPCION = "Fecha límite de inscripción"
ENC_HORA_LIMITE_INSCRIPCION = "Hora límite de inscripción"
ENC_CANTIDAD_CUPOS = "Cantidad total de cupos"
ENC_CUPOS_DISPONIBLES = "Cupos disponibles"
ENC_FECHA_VERIFICACION = "Fecha límite para cancelar la inscripción"

# Estados de inscripción conocidos
INSCRIPCION_ABIERTA = "abierta"
INSCRIPCION_CERRADA = "cerrada"


def _es_valor_desconocido(valor) -> bool:
    if valor is None:
        return True
    if isinstance(valor, str) and valor.strip().lower() in {"", "por confirmar", "por definir", "no indicado", "no indicada"}:
        return True
    return False


def evaluar_inscripcion_disponibilidad(
    registro: Dict
) -> Dict[str, object]:
    """
    Evalúa el estado de inscripción y disponibilidad de un evento aplicando RB-07.

    Returns:
        dict con:
            - estado_inscripcion: str
            - cupos_totales: int | str | None
            - cupos_disponibles: int | str | None
            - fecha_limite: str | None
            - mensaje: str
            - se_puede_inscribir: bool
    """
    estado_inscripcion = str(registro.get(ENC_ESTADO_INSCRIPCION, "")).strip().lower()
    cupos_totales_raw = registro.get(ENC_CANTIDAD_CUPOS)
    cupos_disp_raw = registro.get(ENC_CUPOS_DISPONIBLES)
    fecha_limite = registro.get(ENC_FECHA_LIMITE_INSCRIPCION)

    cupos_totales = None
    cupos_disp = None

    try:
        if cupos_totales_raw is not None and str(cupos_totales_raw).strip() != "":
            cupos_totales = int(cupos_totales_raw)
    except (ValueError, TypeError):
        pass

    try:
        if cupos_disp_raw is not None and str(cupos_disp_raw).strip() != "":
            cupos_disp = int(cupos_disp_raw)
    except (ValueError, TypeError):
        pass

    mensajes: List[str] = []
    se_puede_inscribir = False

    # Verificar si hay información suficiente
    faltantes = []
    if _es_valor_desconocido(estado_inscripcion):
        faltantes.append("estado de inscripción")
    if _es_valor_desconocido(fecha_limite):
        faltantes.append("fecha límite de inscripción")

    # Si falta información crítica, no asegurar disponibilidad
    if faltantes:
        mensajes.append(
            f"No se puede asegurar disponibilidad porque falta: {', '.join(faltantes)}."
        )
        return {
            "estado_inscripcion": estado_inscripcion or "No indicado",
            "cupos_totales": cupos_totales,
            "cupos_disponibles": cupos_disp,
            "fecha_limite": fecha_limite,
            "mensaje": " ".join(mensajes),
            "se_puede_inscribir": False,
        }

    # Construir mensaje basado en lo que se conoce
    if estado_inscripcion == INSCRIPCION_CERRADA:
        mensajes.append("La inscripción está cerrada.")
    elif estado_inscripcion == INSCRIPCION_ABIERTA:
        mensajes.append("La inscripción está abierta.")
        se_puede_inscribir = True
    else:
        mensajes.append(f"Estado de inscripción: {estado_inscripcion or 'No indicado'}.")

    if cupos_totales is not None:
        mensajes.append(f"Total de cupos: {cupos_totales}.")
    if cupos_disp is not None:
        mensajes.append(f"Cupos disponibles: {cupos_disp}.")
        if cupos_disp == 0:
            mensajes.append("No hay cupos disponibles.")
            se_puede_inscribir = False

    if fecha_limite:
        mensajes.append(f"Fecha límite de inscripción: {fecha_limite}.")

    return {
        "estado_inscripcion": estado_inscripcion or "No indicado",
        "cupos_totales": cupos_totales,
        "cupos_disponibles": cupos_disp,
        "fecha_limite": fecha_limite,
        "mensaje": " ".join(mensajes),
        "se_puede_inscribir": se_puede_inscribir,
    }


def es_usuario_administrador(permiso_administrador: bool) -> bool:
    """Devuelve True solo si el usuario tiene permiso de administrador."""
    return bool(permiso_administrador)


def validar_solicitud_cambio_desde_chat(
    solicitud: str, permiso_administrador: bool
) -> Tuple[bool, str]:
    """
    Valida si una solicitud de cambio desde el chat público puede ser procesada.
    RB-08: El chat del visitante no modifica fechas, costos, cupos ni estados.
    """
    palabras_cambio = ["cambia", "cambiá", "cambiar", "modifica", "modificar", "actualiza",
                       "actualizar", "editar", "costo", "precio", "cupo", "fecha", "estado"]
    solicitud_lower = solicitud.lower()
    es_cambio = any(palabra in solicitud_lower for palabra in palabras_cambio)

    if es_cambio and not permiso_administrador:
        return False, (
            "Esta aplicación solo informa; no modifica precios, cupos, fechas ni estados "
            "desde el chat público. Para cambios, acceda como persona administradora."
        )

    return True, "Solicitud válida."
