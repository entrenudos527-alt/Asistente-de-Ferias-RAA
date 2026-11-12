"""
Regla RB-02: Fecha fija de demostración.

Implementa:
- Fecha y hora de referencia: 4 de noviembre de 2026 a las 12:00 m., zona America/Costa_Rica.
- Mostrar esa referencia en el modo de demostración.
- Las marcas de verificación y actualización del Excel del 04/11/2026 18:00 se
  interpretan como UTC, equivalentes a las 12:00 m. de Costa Rica.
- Las fechas de eventos se interpretan como fechas locales y las horas de atención
  como horas locales.
- No usar la fecha real del equipo mientras esté activada la fecha fija de demostración.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Fecha y hora de referencia fija para demostración
FECHA_DEMOSTRACION = "2026-11-04T12:00:00"
ZONA_HORARIA_COSTA_RICA = "America/Costa_Rica"

# Las marcas del Excel 04/11/2026 18:00 se interpretan como UTC
MARCA_UTC = "2026-11-04T18:00:00"


def obtener_fecha_referencia() -> str:
    """
    Devuelve la fecha y hora de referencia fija de demostración.
    No usa la fecha real del equipo.
    """
    return FECHA_DEMOSTRACION


def obtener_zona_horaria() -> str:
    """Devuelve la zona horaria de referencia."""
    return ZONA_HORARIA_COSTA_RICA


def interpretar_marca_utc_como_costa_rica(marca_utc: str) -> str:
    """
    Convierte una marca de tiempo UTC (ej. 04/11/2026 18:00) a su equivalente
    en zona America/Costa_Rica (ej. 12:00 p. m.).
    """
    dt_utc = datetime.fromisoformat(marca_utc).replace(tzinfo=timezone.utc)
    dt_cr = dt_utc.astimezone(ZoneInfo(ZONA_HORARIA_COSTA_RICA))
    return dt_cr.strftime("%Y-%m-%d %H:%M %p %Z")


def es_fecha_demo_activada() -> bool:
    """
    Indica si la fecha fija de demostración está activada.
    En esta versión siempre está activada; no se usa datetime.now().
    """
    return True


def obtener_referencia_modo_demo() -> dict:
    """
    Devuelve un diccionario con la referencia de demostración completa para
    mostrar en pantalla.
    """
    return {
        "fecha_referencia": FECHA_DEMOSTRACION,
        "zona_horaria": ZONA_HORARIA_COSTA_RICA,
        "marca_utc_equivalente": MARCA_UTC,
        "marca_utc_interpretada": interpretar_marca_utc_como_costa_rica(MARCA_UTC),
        "usa_fecha_real_equipo": False,
    }
