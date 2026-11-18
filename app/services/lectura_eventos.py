"""
Módulo de lectura de datos de eventos.

Implementa la lectura de Actividades_Artesanos_Festival_2026.xlsx
(ahora Plantilla_Eventos_RAA.xlsx), hoja "Eventos", encabezados fila 1.
Cada fila representa un evento. Las filas sin nombre de evento se omiten.
Los datos se buscan por encabezado y nombre de columna, no por posición.
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime, date, time

import openpyxl

RUTA_EXCEL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "Insumos",
    "Plantilla_Eventos_RAA (1).xlsx",
)

HOJA_EVENTOS = "Eventos"


def _parse_fecha_o_hora(valor: Any) -> Any:
    """
    Convierte un valor de Excel a datetime, date, time o string.
    Si ya es datetime/date/time, lo devuelve tal cual.
    Si es string, intenta convertirlo.
    """
    if valor is None:
        return None
    if isinstance(valor, (datetime, date, time)):
        return valor
    if isinstance(valor, str) and str(valor).strip() != "":
        texto = str(valor).strip()
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
        # Intentar como hora sola (formatos comunes en el Excel)
        texto_upper = texto.upper().replace(".", "").strip()
        for fmt in ("%I:%M%p", "%I:%M %p", "%H:%M", "%I%p", "%I %p"):
            try:
                return datetime.strptime(texto_upper, fmt).time()
            except ValueError:
                continue
        # Si no se pudo convertir, devolver como string
        return texto
    return valor


def leer_eventos(
    ruta_excel: Optional[str] = None,
) -> Dict[str, object]:
    """
    Lee los eventos del Excel de insumos.

    Returns:
        dict con:
            - "encabezados": lista de nombres de columnas
            - "registros": lista de dict {encabezado: valor} por cada fila con nombre de evento
            - "total_registros": número de registros leídos
            - "total_columnas": número de columnas leídas
            - "tipos_evento": lista de tipos únicos
    """
    if ruta_excel is None:
        ruta_excel = RUTA_EXCEL

    wb = openpyxl.load_workbook(ruta_excel, data_only=True)
    ws = wb[HOJA_EVENTOS]

    # Leer encabezados de la fila 1
    encabezados: List[str] = []
    for col in range(1, ws.max_column + 1):
        val = ws.cell(row=1, column=col).value
        encabezados.append(str(val) if val is not None else f"Col{col}")

    # Leer registros desde fila 2, omitir filas sin nombre de evento
    registros: List[Dict[str, Any]] = []
    for fila in range(2, ws.max_row + 1):
        nombre_evento = ws.cell(row=fila, column=1).value
        if nombre_evento is None or str(nombre_evento).strip() == "":
            continue

        registro: Dict[str, Any] = {}
        for idx, encabezado in enumerate(encabezados, start=1):
            valor_raw = ws.cell(row=fila, column=idx).value
            registro[encabezado] = _parse_fecha_o_hora(valor_raw)

        registros.append(registro)

    wb.close()

    # Obtener tipos de evento únicos
    tipos_evento: List[str] = []
    for reg in registros:
        tipo = reg.get("Tipo de evento")
        if tipo and str(tipo).strip() not in tipos_evento:
            tipos_evento.append(str(tipo).strip())

    return {
        "encabezados": encabezados,
        "registros": registros,
        "total_registros": len(registros),
        "total_columnas": len(encabezados),
        "tipos_evento": tipos_evento,
    }


def obtener_evento_por_nombre(
    nombre: str, ruta_excel: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Busca un evento por su nombre (búsqueda flexible, no distinguir mayúsculas)."""
    datos = leer_eventos(ruta_excel)
    nombre_lower = str(nombre).strip().lower()
    for registro in datos["registros"]:
        nombre_reg = str(registro.get("Nombre del evento", "")).strip().lower()
        if nombre_reg == nombre_lower:
            return registro
    return None


def obtener_eventos_por_tipo(
    tipo: str, ruta_excel: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Busca eventos por tipo de evento."""
    datos = leer_eventos(ruta_excel)
    tipo_lower = str(tipo).strip().lower()
    return [
        r for r in datos["registros"]
        if str(r.get("Tipo de evento", "")).strip().lower() == tipo_lower
    ]


def obtener_todos_los_eventos(
    ruta_excel: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Devuelve todos los eventos registrados."""
    datos = leer_eventos(ruta_excel)
    return datos["registros"]


def es_valor_desconocido(valor: Any) -> bool:
    """
    Determina si un valor representa información faltante.
    Campos vacíos, None, strings vacíos son desconocidos.
    Valores como "Sí", "No", "No aplica", "Por confirmar", 0, "0" son conocidos.
    """
    if valor is None:
        return True
    if isinstance(valor, str) and valor.strip() == "":
        return True
    if isinstance(valor, (int, float)):
        return False  # 0 es un valor válido, no desconocido
    return False
