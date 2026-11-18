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


def _parse_hora_string(texto: str) -> time | None:
    """
    Intenta convertir un string de hora a objeto time.
    Soporta formatos como: '8:00pm', '7:00 p. m.', '5:00pm', '9:00am',
    '7am', '13:00', '13:00:00', etc.
    """
    texto_limpio = texto.strip().upper().replace(".", "").replace(" ", "")
    # Formatos comunes en el Excel de eventos
    for fmt in ("%I:%M%p", "%I%p", "%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(texto_limpio, fmt).time()
        except ValueError:
            continue
    return None


def _parse_valor(valor):
    """
    Convierte un valor a objeto datetime o time.
    Soporta datetime, time, strings ISO, strings de fecha, strings de hora.
    """
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, time):
        return valor
    if isinstance(valor, str) and valor.strip() != "":
        texto = valor.strip()
        # Intentar como datetime ISO
        try:
            return datetime.fromisoformat(texto)
        except ValueError:
            pass
        # Intentar como fecha sola
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(texto, fmt)
            except ValueError:
                continue
        # Intentar como hora sola
        resultado = _parse_hora_string(texto)
        if resultado is not None:
            return resultado
    return None


def formatear_fecha(valor) -> str:
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


def formatear_hora(valor) -> str:
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


def formatear_fecha_hora(valor) -> str:
    """
    Formatea fecha y hora como '4 de noviembre de 2026, 12:00 p. m.'.
    Devuelve cadena vacía si el valor es nulo o no se puede parsear.
    """
    dt = _parse_valor(valor)
    if dt is None:
        return ""
    if isinstance(dt, time):
        return formatear_hora(dt)
    fecha = f"{dt.day} de {_MESES[dt.month - 1]} de {dt.year}"
    hora = formatear_hora(dt)
    return f"{fecha}, {hora}"


def formatear_rango_fechas(fecha_inicio, fecha_fin) -> str:
    """
    Formatea un rango de fechas.
    Si es un solo día, muestra la fecha una sola vez.
    Si son varios días, muestra el intervalo.
    """
    fi = _parse_valor(fecha_inicio)
    ff = _parse_valor(fecha_fin)

    if fi is None:
        return ""
    if isinstance(fi, time):
        return ""

    if ff is None:
        return f"{fi.day} de {_MESES[fi.month - 1]} de {fi.year}"

    if isinstance(ff, time):
        return f"{fi.day} de {_MESES[fi.month - 1]} de {fi.year}"

    # Mismo día
    if fi.date() == ff.date():
        return f"{fi.day} de {_MESES[fi.month - 1]} de {fi.year}"

    # Diferentes días - intervalo
    return f"{fi.day} de {_MESES[fi.month - 1]} al {ff.day} de {_MESES[ff.month - 1]} de {ff.year}"


def formatear_monto(valor) -> str:
    """
    Formatea un monto en colones costarricenses.
    Diferencia 0 de vacío. Si es 0, muestra "₡0". Si está vacío, devuelve "".
    Si es string como "c1000", lo interpreta como 1000.
    """
    if valor is None:
        return ""
    if isinstance(valor, str):
        texto = valor.strip()
        if texto == "" or texto.lower() in ("no aplica", "por confirmar", "no indicado"):
            return ""
        # Intentar extraer número de strings como "c1000"
        import re
        match = re.search(r'[\d,]+', texto)
        if match:
            try:
                numero = int(match.group().replace(",", ""))
                if numero == 0:
                    return "₡0"
                return f"₡{numero:,}"
            except ValueError:
                return texto
        return texto
    if isinstance(valor, (int, float)):
        if valor == 0:
            return "₡0"
        return f"₡{valor:,}"
    return str(valor)
