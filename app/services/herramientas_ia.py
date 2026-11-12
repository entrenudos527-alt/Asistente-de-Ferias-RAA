"""
Contrato JSON de herramientas para el agente de IA (RB-09).

Estas herramientas consultan el almacenamiento de la app cargado inicialmente
desde el Excel de insumos. Son de solo lectura para el chat público.

Contrato definido en AGENTS.md, sección "Contrato JSON de herramientas".
"""

from typing import Any, Dict, List, Optional

from app.services.lectura_datos import leer_actividades, obtener_actividad_por_codigo
from app.services.regla_rb02 import obtener_fecha_referencia
from app.services.regla_rb03_rb04 import obtener_proxima_actividad

# Encabezados clave del Excel
ENC_IDENTIFICADOR = "Identificador"
ENC_ACTIVIDAD = "Actividad"
ENC_LUGAR = "Lugar"
ENC_FECHA_INICIO = "Fecha de inicio"
ENC_ESTADO = "Estado de la feria"
ENC_ULTIMA_ACTUALIZACION = "Última actualización"
ENC_VERIFICACION_ESPACIOS = "Verificación de espacios"


def _registro_a_dict_completo(registro: dict) -> dict:
    """Convierte un registro del Excel en un diccionario serializable."""
    resultado: dict = {}
    for clave, valor in registro.items():
        if hasattr(valor, "isoformat"):  # datetime
            resultado[clave] = valor.isoformat()
        else:
            resultado[clave] = valor
    return resultado


def _campos_desconocidos(registro: dict) -> List[str]:
    """Devuelve la lista de campos con valores desconocidos (vacíos o especiales)."""
    desconocidos: List[str] = []
    valores_especiales = {"", "por confirmar", "por definir", "no indicado", "no indicada"}
    for clave, valor in registro.items():
        if valor is None:
            desconocidos.append(clave)
        elif isinstance(valor, str) and valor.strip().lower() in valores_especiales:
            desconocidos.append(clave)
    return desconocidos


def _detectar_inconsistencias(registro: dict) -> List[str]:
    """Detecta inconsistencias básicas en el registro."""
    inconsistencias: List[str] = []
    # Ejemplo: si hay fecha de inicio y fecha de fin, validar orden
    fecha_inicio = registro.get("Fecha de inicio")
    fecha_fin = registro.get("Fecha de finalización")
    if fecha_inicio and fecha_fin:
        try:
            from datetime import datetime
            fi = datetime.fromisoformat(str(fecha_inicio)) if isinstance(fecha_inicio, str) else fecha_inicio
            ff = datetime.fromisoformat(str(fecha_fin)) if isinstance(fecha_fin, str) else fecha_fin
            if fi > ff:
                inconsistencias.append("Fecha de inicio posterior a fecha de finalización")
        except (ValueError, TypeError):
            pass
    return inconsistencias


# ============================================================================
# buscar_ferias (solo lectura)
# ============================================================================

def buscar_ferias(
    codigo: Optional[str] = None,
    nombre: Optional[str] = None,
    fecha: Optional[str] = None,
    lugar: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Busca actividades por filtros: código, nombre, fecha o lugar.
    Es de solo lectura.

    Contrato JSON:
    {
      "nombre": "buscar_ferias",
      "argumentos": {
        "codigo": "string | null",
        "nombre": "string | null",
        "fecha": "string | null",
        "lugar": "string | null"
      },
      "salida": {
        "resultados": [ { "codigo": "string", "nombre": "string", "fecha": "string", "lugar": "string" } ],
        "error": "string | null"
      }
    }
    """
    try:
        datos = leer_actividades()
        registros = datos["registros"]

        # Aplicar filtros
        filtrados: List[dict] = []
        for registro in registros:
            coincide = True

            if codigo is not None:
                cod_registro = str(registro.get(ENC_IDENTIFICADOR, "")).strip()
                if cod_registro.lower() != codigo.strip().lower():
                    coincide = False

            if coincide and nombre is not None:
                nom_registro = str(registro.get(ENC_ACTIVIDAD, "")).strip()
                if nombre.strip().lower() not in nom_registro.lower():
                    coincide = False

            if coincide and fecha is not None:
                fec_registro = str(registro.get(ENC_FECHA_INICIO, "")).strip()
                if fecha.strip().lower() not in fec_registro.lower():
                    coincide = False

            if coincide and lugar is not None:
                lug_registro = str(registro.get(ENC_LUGAR, "")).strip()
                if lugar.strip().lower() not in lug_registro.lower():
                    coincide = False

            if coincide:
                filtrados.append({
                    "codigo": str(registro.get(ENC_IDENTIFICADOR, "")),
                    "nombre": str(registro.get(ENC_ACTIVIDAD, "")),
                    "fecha": str(registro.get(ENC_FECHA_INICIO, "")),
                    "lugar": str(registro.get(ENC_LUGAR, "")),
                })

        return {
            "resultados": filtrados,
            "error": None,
        }

    except Exception as e:
        return {
            "resultados": [],
            "error": str(e),
        }


# ============================================================================
# obtener_ficha (solo lectura)
# ============================================================================

def obtener_ficha(identificador: str) -> Dict[str, Any]:
    """
    Recupera la ficha vigente de una actividad por su identificador.
    Es de solo lectura.

    Contrato JSON:
    {
      "nombre": "obtener_ficha",
      "argumentos": {
        "identificador": "string"
      },
      "salida": {
        "ficha": { "campo": "valor" },
        "ultima_actualizacion": "string | null",
        "version": "string | null",
        "fecha_verificacion_cupos": "string | null",
        "campos_desconocidos": ["string"],
        "inconsistencias": ["string"],
        "error": "string | null"
      }
    }
    """
    try:
        registro = obtener_actividad_por_codigo(identificador)
        if registro is None:
            return {
                "ficha": {},
                "ultima_actualizacion": None,
                "version": None,
                "fecha_verificacion_cupos": None,
                "campos_desconocidos": [],
                "inconsistencias": [],
                "error": f"No se encontró la actividad con identificador '{identificador}'.",
            }

        ficha_completa = _registro_a_dict_completo(registro)

        return {
            "ficha": ficha_completa,
            "ultima_actualizacion": str(registro.get(ENC_ULTIMA_ACTUALIZACION, "")) or None,
            "version": str(registro.get(ENC_ULTIMA_ACTUALIZACION, "")) or None,
            "fecha_verificacion_cupos": str(registro.get(ENC_VERIFICACION_ESPACIOS, "")) or None,
            "campos_desconocidos": _campos_desconocidos(registro),
            "inconsistencias": _detectar_inconsistencias(registro),
            "error": None,
        }

    except Exception as e:
        return {
            "ficha": {},
            "ultima_actualizacion": None,
            "version": None,
            "fecha_verificacion_cupos": None,
            "campos_desconocidos": [],
            "inconsistencias": [],
            "error": str(e),
        }


# ============================================================================
# listar_proximas_ferias (solo lectura)
# ============================================================================

def listar_proximas_ferias(
    fecha_referencia: Optional[str] = None,
    filtros: Optional[Dict[str, Optional[str]]] = None,
) -> Dict[str, Any]:
    """
    Devuelve actividades elegibles ordenadas, según la fecha de referencia y filtros.
    Es de solo lectura.

    Contrato JSON:
    {
      "nombre": "listar_proximas_ferias",
      "argumentos": {
        "fecha_referencia": "string",
        "filtros": { "nombre": "string | null", "lugar": "string | null" }
      },
      "salida": {
        "actividades": [ { "codigo": "string", "nombre": "string", "fecha_inicio": "string", "lugar": "string", "estado": "string" } ],
        "error": "string | null"
      }
    }
    """
    try:
        if fecha_referencia is None:
            fecha_referencia = obtener_fecha_referencia()

        # Usar la lógica de RB-03 para obtener la próxima actividad y candidatas
        from datetime import datetime

        fecha_ref_dt = datetime.fromisoformat(fecha_referencia)

        datos = leer_actividades()
        registros = datos["registros"]

        # Filtrar actividades no canceladas ni finalizadas, con fecha >= referencia
        elegibles: List[dict] = []
        for registro in registros:
            estado = str(registro.get(ENC_ESTADO, "")).strip().lower()
            if estado in {"cancelada", "finalizada"}:
                continue

            fecha_inicio_str = str(registro.get(ENC_FECHA_INICIO, ""))
            try:
                fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
            except ValueError:
                continue

            if fecha_inicio >= fecha_ref_dt:
                # Aplicar filtros adicionales si se proporcionan
                if filtros:
                    if filtros.get("nombre"):
                        nom = str(registro.get(ENC_ACTIVIDAD, "")).lower()
                        if filtros["nombre"].lower() not in nom:
                            continue
                    if filtros.get("lugar"):
                        lug = str(registro.get(ENC_LUGAR, "")).lower()
                        if filtros["lugar"].lower() not in lug:
                            continue

                elegibles.append({
                    "codigo": str(registro.get(ENC_IDENTIFICADOR, "")),
                    "nombre": str(registro.get(ENC_ACTIVIDAD, "")),
                    "fecha_inicio": str(registro.get(ENC_FECHA_INICIO, "")),
                    "lugar": str(registro.get(ENC_LUGAR, "")),
                    "estado": estado,
                })

        # Ordenar por fecha de inicio
        elegibles.sort(key=lambda a: a["fecha_inicio"])

        return {
            "actividades": elegibles,
            "error": None,
        }

    except Exception as e:
        return {
            "actividades": [],
            "error": str(e),
        }
