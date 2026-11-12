"""
Funciones compartidas de formateo de fechas y horas en español.

Se utilizan tanto en los filtros de Jinja2 (plantillas HTML) como en
el agente de IA (respuestas de texto). Los valores originales de los
datos no se modifican; solo se transforman al momento de presentar.
"""

from datetime import datetime, time

_MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def _parse_valor(valor):
    """Convierte un valor (string ISO, datetime o time) a objeto datetime o time."""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, time):
        return valor
    if isinstance(valor, str) and valor.strip() != "":
        try:
            return datetime.fromisoformat(valor.strip())
        except ValueError:
            return None
    return None


def formato_fecha(valor) -> str:
    """
    Formatea una fecha como '14 de noviembre de 2026'.
    Devuelve cadena vacía si el valor es nulo o no tiene parte de fecha.
    """
    dt = _parse_valor(valor)
    if dt is None:
        return ""
    if isinstance(dt, time):
        return ""
    return f"{dt.day} de {_MESES[dt.month - 1]} de {dt.year}"


def formato_hora(valor) -> str:
    """
    Formatea una hora como '7:00 a. m.' (sin segundos).
    Devuelve cadena vacía si el valor es nulo o no tiene parte de hora.
    """
    dt = _parse_valor(valor)
    if dt is None:
        return ""
    hora = dt.hour
    minuto = dt.minute
    am_pm = "a. m." if hora < 12 else "p. m."
    hora_12 = hora if hora <= 12 else hora - 12
    if hora == 0:
        hora_12 = 12
    return f"{hora_12}:{minuto:02d} {am_pm}"


def formato_fecha_hora(valor) -> str:
    """
    Formatea fecha y hora como '4 de noviembre de 2026, 12:00 p. m.'.
    Devuelve cadena vacía si el valor es nulo o no se puede parsear.
    """
    dt = _parse_valor(valor)
    if dt is None:
        return ""
    if isinstance(dt, time):
        return formato_hora(dt)
    fecha = f"{dt.day} de {_MESES[dt.month - 1]} de {dt.year}"
    hora = formato_hora(dt)
    return f"{fecha}, {hora}"
