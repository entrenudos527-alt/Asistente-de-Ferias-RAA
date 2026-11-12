"""
Regla RB-01: Fuente de datos y versión.

Implementa:
- Búsqueda por encabezado y código (no depende únicamente de posiciones de columnas).
- Conservar A a J como referencia original.
- Para las respuestas del ejercicio, usar los campos de práctica de K a BF cuando
  exista un valor específico sobre el mismo tema.
"""

from typing import Dict, Optional

from app.services.lectura_datos import leer_actividades, obtener_actividad_por_codigo

# Nombres de encabezados clave (según fila 5 del Excel)
ENC_IDENTIFICADOR = "Identificador"


def obtener_valor_campo(
    registro: Dict[str, object], campo_practica: str, campo_original: str
) -> Optional[object]:
    """
    Devuelve el valor de un campo aplicando la prioridad de RB-01:
    - Si el campo de práctica (K-BF) tiene un valor específico, se usa ese.
    - Si no, se usa el campo original (A-J).
    - Si ninguno tiene valor, devuelve None.
    """
    valor_practica = registro.get(campo_practica)
    if valor_practica is not None and str(valor_practica).strip() != "":
        return valor_practica
    return registro.get(campo_original)


def buscar_actividad_por_codigo(codigo: str) -> Optional[Dict[str, object]]:
    """
    Busca una actividad por su código identificador, usando el encabezado
    'Identificador' (columna K) y no la posición de columna.

    Returns:
        dict con los datos de la actividad aplicando prioridad K-BF, o None
        si no se encuentra.
    """
    registro = obtener_actividad_por_codigo(codigo)
    if registro is None:
        return None

    # Aplicar prioridad K-BF sobre A-J para los campos que tienen par conocido
    mapeo_campos = {
        "Fecha de inicio": "Fecha",
        "Dirección exacta de práctica": "Lugar",
        "Ingreso y montaje": "Horario según cronograma",
        "Costo de participación": "Participación indicada",
        "Estado de inscripción": "Observaciones y pendientes",
    }

    resultado: Dict[str, object] = {}
    for clave, valor in registro.items():
        resultado[clave] = valor

    for campo_practica, campo_original in mapeo_campos.items():
        if campo_practica in registro and campo_original in registro:
            valor_prioritario = obtener_valor_campo(
                registro, campo_practica, campo_original
            )
            if valor_prioritario is not None:
                resultado[campo_practica] = valor_prioritario

    return resultado


def validar_codigo_existe(codigo: str) -> bool:
    """Devuelve True si el código existe entre los 11 registros."""
    return buscar_actividad_por_codigo(codigo) is not None
