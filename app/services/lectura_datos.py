"""
Módulo de lectura de datos de insumos.

Implementa la regla RB-01: la fuente inicial es
Actividades_Artesanos_Festival_2026.xlsx, hoja "Exposición de artesanos",
encabezados fila 5, registros filas 6 a 16. Cada actividad se identifica
por su código (columna K). La implementación busca por encabezado y código,
no depende únicamente de posiciones de columnas.

Conserva A a J como referencia original. Para las respuestas del ejercicio,
usa los campos de práctica de K a BF cuando exista un valor específico.
"""

import os
from typing import Dict, List, Optional

import openpyxl

RUTA_EXCEL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "Insumos",
    "Actividades_Artesanos_Festival_2026.xlsx",
)

HOJA_EXPOSICION = "Exposición de artesanos"
FILA_ENCABEZADOS = 5
FILA_PRIMER_REGISTRO = 6
FILA_ULTIMO_REGISTRO = 16


def leer_actividades(
    ruta_excel: Optional[str] = None,
) -> Dict[str, object]:
    """
    Lee las 11 actividades del Excel de insumos.

    Returns:
        dict con:
            - "encabezados": lista de (columna_letra, nombre_encabezado) para A-BF
            - "registros": lista de dict {encabezado: valor} por cada fila 6-16
            - "codigos": lista de identificadores (columna K)
            - "total_registros": número de registros leídos
            - "total_columnas": número de columnas leídas
    """
    if ruta_excel is None:
        ruta_excel = RUTA_EXCEL

    wb = openpyxl.load_workbook(ruta_excel, data_only=True)
    ws = wb[HOJA_EXPOSICION]

    # Leer encabezados de la fila 5, columnas A (1) a BF (58)
    encabezados: List[str] = []
    for col in range(1, 59):
        valor = ws.cell(row=FILA_ENCABEZADOS, column=col).value
        encabezados.append(str(valor) if valor is not None else f"Col{col}")

    # Leer registros filas 6 a 16
    registros: List[Dict[str, object]] = []
    codigos: List[str] = []

    for fila in range(FILA_PRIMER_REGISTRO, FILA_ULTIMO_REGISTRO + 1):
        registro: Dict[str, object] = {}
        for idx, encabezado in enumerate(encabezados, start=1):
            valor = ws.cell(row=fila, column=idx).value
            registro[encabezado] = valor
        registros.append(registro)

        # El identificador está en la columna K (índice 11, position 11 en la lista)
        codigo = registro.get(encabezados[10]) if len(encabezados) > 10 else None
        if codigo:
            codigos.append(str(codigo))

    wb.close()

    return {
        "encabezados": encabezados,
        "registros": registros,
        "codigos": codigos,
        "total_registros": len(registros),
        "total_columnas": len(encabezados),
    }


def obtener_actividad_por_codigo(
    codigo: str, ruta_excel: Optional[str] = None
) -> Optional[Dict[str, object]]:
    """Busca una actividad por su código identificador (columna K)."""
    datos = leer_actividades(ruta_excel)
    for registro in datos["registros"]:
        if str(registro.get(datos["encabezados"][10], "")) == codigo:
            return registro
    return None
