"""
Contrato JSON de herramientas para el agente de IA.

Estas herramientas consultan el almacenamiento de la app cargado inicialmente
desde el Excel de insumos. Son de solo lectura para el chat público.

Contrato definido en AGENTS.md, sección "Contrato JSON de herramientas".
"""

from typing import Any, Dict, List, Optional

from app.services.lectura_eventos import leer_eventos, obtener_evento_por_nombre


def _evento_a_resumen(registro: dict) -> dict:
    """Convierte un registro de evento en un resumen para resultados de búsqueda."""
    return {
        "nombre": str(registro.get("Nombre del evento", "")),
        "tipo": str(registro.get("Tipo de evento", "")),
        "lugar": str(registro.get("Lugar del evento", "")),
        "fecha_inicio": str(registro.get("Fecha de inicio", "")),
    }


# ============================================================================
# buscar_eventos (solo lectura)
# ============================================================================

def buscar_eventos(
    nombre: Optional[str] = None,
    tipo: Optional[str] = None,
    lugar: Optional[str] = None,
    fecha: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Busca eventos por filtros: nombre, tipo, lugar o fecha.
    Es de solo lectura.

    Contrato JSON:
    {
      "nombre": "buscar_eventos",
      "argumentos": {
        "nombre": "string | null",
        "tipo": "string | null",
        "lugar": "string | null",
        "fecha": "string | null"
      },
      "salida": {
        "resultados": [ { "nombre": "string", "tipo": "string", "lugar": "string", "fecha_inicio": "string" } ],
        "error": "string | null"
      }
    }
    """
    try:
        datos = leer_eventos()
        registros = datos["registros"]

        filtrados: List[dict] = []
        for registro in registros:
            coincide = True

            if nombre is not None:
                nom = str(registro.get("Nombre del evento", "")).strip()
                if nombre.strip().lower() not in nom.lower():
                    coincide = False

            if coincide and tipo is not None:
                t = str(registro.get("Tipo de evento", "")).strip()
                if tipo.strip().lower() not in t.lower():
                    coincide = False

            if coincide and lugar is not None:
                lug = str(registro.get("Lugar del evento", "")).strip()
                if lugar.strip().lower() not in lug.lower():
                    coincide = False

            if coincide and fecha is not None:
                fec = str(registro.get("Fecha de inicio", "")).strip()
                if fecha.strip().lower() not in fec.lower():
                    coincide = False

            if coincide:
                filtrados.append(_evento_a_resumen(registro))

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
# obtener_evento (solo lectura)
# ============================================================================

def obtener_evento(nombre_evento: str) -> Dict[str, Any]:
    """
    Recupera la ficha vigente de un evento por su nombre.
    Es de solo lectura.

    Contrato JSON:
    {
      "nombre": "obtener_evento",
      "argumentos": {
        "nombre": "string"
      },
      "salida": {
        "evento": { "campo": "valor" },
        "error": "string | null"
      }
    }
    """
    try:
        registro = obtener_evento_por_nombre(nombre_evento)
        if registro is None:
            return {
                "evento": {},
                "error": f"No se encontró el evento '{nombre_evento}'.",
            }

        return {
            "evento": registro,
            "error": None,
        }

    except Exception as e:
        return {
            "evento": {},
            "error": str(e),
        }
