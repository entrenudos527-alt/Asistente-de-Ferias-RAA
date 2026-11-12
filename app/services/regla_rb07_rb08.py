"""
Reglas RB-07 y RB-08.

RB-07: Inscripción y disponibilidad
- Si la actividad está cancelada, indicar la cancelación antes de cualquier instrucción de participación.
- Si está finalizada, presentarla como actividad pasada.
- Si la inscripción está cerrada o venció el plazo respecto a la fecha de referencia, informarlo aunque
  todavía aparezcan espacios. No afirmar que se puede inscribir.
- Si hay 0 espacios, informar que no hay cupos y explicar la lista de espera solo si está registrada.
  No crear una inscripción en esa lista.
- Si la inscripción está abierta, el plazo está vigente y hay cupos, comunicar lo registrado con su
  fecha de verificación. No garantizar disponibilidad en tiempo real ni confirmar participación.
- Si falta el estado, el plazo o la verificación de cupos, no asegurar que puede inscribirse o que hay
  disponibilidad actual. Explicar qué dato falta.

RB-08: Actualizaciones y administración
- Solo la persona administradora podrá crear o modificar fichas mediante las funciones previstas para ello.
- El chat del visitante no modifica fechas, costos, cupos ni estados. Una solicitud como "cambiá el precio a mil"
  no altera el registro.
- Después de guardar un cambio válido, actualizar la marca de última actualización y consultar la versión
  vigente en las respuestas siguientes.
- Si un registro fue editado en la app, esa versión guardada será la fuente de trabajo; el Excel será la carga inicial.
- Una nueva importación no sobrescribirá cambios sin una acción explícita de la persona administradora.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.services.regla_rb02 import obtener_fecha_referencia
from app.utils.formato import formato_fecha_hora

# Encabezados clave
ENC_ESTADO_FERIA = "Estado de la feria"
ENC_ESTADO_INSCRIPCION = "Estado de inscripción"
ENC_FECHA_LIMITE_INSCRIPCION = "Fecha límite de inscripción"
ENC_HORA_LIMITE_INSCRIPCION = "Hora límite de inscripción"
ENC_ESPACIOS_DISPONIBLES = "Espacios disponibles"
ENC_VERIFICACION_ESPACIOS = "Verificación de espacios"
ENC_LISTA_ESPERA = "Lista de espera"
ENC_ULTIMA_ACTUALIZACION = "Última actualización"

# Estados de inscripción
INSCRIPCION_ABIERTA = "abierta"
INSCRIPCION_CERRADA = "cerrada"
INSCRIPCION_POR_CONFIRMAR = "por confirmar"

# Estados de feria
FERIA_CANCELADA = "cancelada"
FERIA_FINALIZADA = "finalizada"


def _parse_fecha(valor) -> Optional[datetime]:
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, str):
        try:
            return datetime.fromisoformat(valor)
        except ValueError:
            for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(valor, fmt)
                except ValueError:
                    continue
    return None


def _es_valor_desconocido(valor) -> bool:
    if valor is None:
        return True
    if isinstance(valor, str) and valor.strip().lower() in {"", "por confirmar", "por definir", "no indicado", "no indicada"}:
        return True
    return False


def _plazo_vencido(fecha_limite, hora_limite, fecha_ref: datetime) -> bool:
    """Devuelve True si el plazo de inscripción ya venció respecto a la fecha de referencia."""
    if _es_valor_desconocido(fecha_limite):
        return False  # No hay plazo, no se puede decir que venció
    fecha_limite_dt = _parse_fecha(fecha_limite)
    if fecha_limite_dt is None:
        return False
    if hora_limite and not _es_valor_desconocido(hora_limite):
        try:
            hora_str = str(hora_limite)
            if ":" in hora_str:
                h, m = hora_str.split(":")[:2]
                fecha_limite_dt = fecha_limite_dt.replace(hour=int(h), minute=int(m))
        except (ValueError, IndexError):
            pass
    return fecha_ref > fecha_limite_dt


def evaluar_inscripcion_disponibilidad(
    registro: Dict, fecha_ref: Optional[datetime] = None
) -> Dict[str, object]:
    """
    Evalúa el estado de inscripción y disponibilidad de una actividad aplicando RB-07.

    Returns:
        dict con:
            - estado_feria: str
            - estado_inscripcion: str
            - espacios_disponibles: int | None
            - plazo_vigente: bool
            - cupos_agotados: bool
            - mensaje: str (texto para mostrar al usuario)
            - se_puede_inscribir: bool
    """
    if fecha_ref is None:
        fecha_ref_str = obtener_fecha_referencia()
        fecha_ref = datetime.fromisoformat(fecha_ref_str)

    estado_feria = str(registro.get(ENC_ESTADO_FERIA, "")).strip().lower()
    estado_inscripcion = str(registro.get(ENC_ESTADO_INSCRIPCION, "")).strip().lower()
    espacios_raw = registro.get(ENC_ESPACIOS_DISPONIBLES)
    try:
        espacios = int(espacios_raw) if espacios_raw is not None and str(espacios_raw).strip() != "" else None
    except (ValueError, TypeError):
        espacios = None
    fecha_limite = registro.get(ENC_FECHA_LIMITE_INSCRIPCION)
    hora_limite = registro.get(ENC_HORA_LIMITE_INSCRIPCION)
    verificacion = registro.get(ENC_VERIFICACION_ESPACIOS)
    lista_espera = registro.get(ENC_LISTA_ESPERA)

    plazo_vigente = not _plazo_vencido(fecha_limite, hora_limite, fecha_ref)
    cupos_agotados = espacios == 0
    se_puede_inscribir = False
    mensajes: List[str] = []

    # 1. Actividad cancelada
    if estado_feria == FERIA_CANCELADA:
        mensajes.append("Esta actividad está cancelada. No se pueden realizar inscripciones.")
        return {
            "estado_feria": estado_feria,
            "estado_inscripcion": estado_inscripcion,
            "espacios_disponibles": espacios,
            "plazo_vigente": plazo_vigente,
            "cupos_agotados": cupos_agotados,
            "mensaje": " ".join(mensajes),
            "se_puede_inscribir": False,
        }

    # 2. Actividad finalizada
    if estado_feria == FERIA_FINALIZADA:
        mensajes.append("Esta actividad ya finalizó. Se presenta como actividad pasada.")
        return {
            "estado_feria": estado_feria,
            "estado_inscripcion": estado_inscripcion,
            "espacios_disponibles": espacios,
            "plazo_vigente": plazo_vigente,
            "cupos_agotados": cupos_agotados,
            "mensaje": " ".join(mensajes),
            "se_puede_inscribir": False,
        }

    # 3. Inscripción cerrada o plazo vencido
    if estado_inscripcion == INSCRIPCION_CERRADA or not plazo_vigente:
        if estado_inscripcion == INSCRIPCION_CERRADA:
            mensajes.append("La inscripción está cerrada.")
        if not plazo_vigente:
            mensajes.append("El plazo de inscripción ha vencido.")
        if espacios is not None and espacios > 0:
            mensajes.append(f"Aunque todavía aparecen {espacios} espacios, no se puede inscribir.")
        mensajes.append("No afirmar que se puede inscribir.")
        return {
            "estado_feria": estado_feria,
            "estado_inscripcion": estado_inscripcion,
            "espacios_disponibles": espacios,
            "plazo_vigente": plazo_vigente,
            "cupos_agotados": cupos_agotados,
            "mensaje": " ".join(mensajes),
            "se_puede_inscribir": False,
        }

    # 4. Cupos agotados (0 espacios)
    if cupos_agotados:
        mensajes.append("No hay cupos disponibles (0 espacios).")
        if not _es_valor_desconocido(lista_espera):
            mensajes.append(f"Lista de espera: {lista_espera}.")
        else:
            mensajes.append("No hay lista de espera registrada.")
        mensajes.append("No se crea una inscripción en la lista de espera.")
        return {
            "estado_feria": estado_feria,
            "estado_inscripcion": estado_inscripcion,
            "espacios_disponibles": espacios,
            "plazo_vigente": plazo_vigente,
            "cupos_agotados": True,
            "mensaje": " ".join(mensajes),
            "se_puede_inscribir": False,
        }

    # 5. Inscripción abierta, plazo vigente, hay cupos y verificación de cupos presente
    if (
        estado_inscripcion == INSCRIPCION_ABIERTA
        and plazo_vigente
        and espacios is not None
        and espacios > 0
        and not _es_valor_desconocido(verificacion)
    ):
        verificacion_txt = f" (verificados {formato_fecha_hora(verificacion)})" if not _es_valor_desconocido(verificacion) else ""
        mensajes.append(
            f"Inscripción abierta. Hay {espacios} espacios disponibles{verificacion_txt}."
        )
        mensajes.append("Esto no garantiza disponibilidad en tiempo real ni confirma la participación.")
        se_puede_inscribir = True
        return {
            "estado_feria": estado_feria,
            "estado_inscripcion": estado_inscripcion,
            "espacios_disponibles": espacios,
            "plazo_vigente": plazo_vigente,
            "cupos_agotados": False,
            "mensaje": " ".join(mensajes),
            "se_puede_inscribir": True,
        }

    # 6. Falta información (estado, plazo o verificación)
    faltantes = []
    if _es_valor_desconocido(estado_inscripcion):
        faltantes.append("estado de inscripción")
    if _es_valor_desconocido(fecha_limite):
        faltantes.append("plazo de inscripción")
    if _es_valor_desconocido(verificacion) and espacios is not None and espacios > 0:
        faltantes.append("verificación de cupos")

    if faltantes:
        mensajes.append(
            f"No se puede asegurar disponibilidad porque falta: {', '.join(faltantes)}."
        )
        return {
            "estado_feria": estado_feria,
            "estado_inscripcion": estado_inscripcion,
            "espacios_disponibles": espacios,
            "plazo_vigente": plazo_vigente,
            "cupos_agotados": cupos_agotados,
            "mensaje": " ".join(mensajes),
            "se_puede_inscribir": False,
        }

    # Default: no se puede inscribir
    mensajes.append("No se puede determinar el estado de inscripción con los datos disponibles.")
    return {
        "estado_feria": estado_feria,
        "estado_inscripcion": estado_inscripcion,
        "espacios_disponibles": espacios,
        "plazo_vigente": plazo_vigente,
        "cupos_agotados": cupos_agotados,
        "mensaje": " ".join(mensajes),
        "se_puede_inscribir": False,
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


def registrar_ultima_actualizacion() -> str:
    """
    Devuelve la marca de fecha y hora de última actualización usando la fecha fija de demostración.
    Después de guardar un cambio válido, esta marca se actualiza.
    """
    from app.services.regla_rb02 import obtener_fecha_referencia
    return obtener_fecha_referencia()
