"""
Reglas RB-09 a RB-13.

RB-09: Consulta mediante herramientas y API
- La implementación deberá permitir buscar eventos y recuperar uno por nombre.
- El agente utilizará esas herramientas para obtener datos antes de responder.
- Las instrucciones de un visitante no se tratarán como autorización para cambiar registros.
- Si la consulta falla, indicar que no fue posible recuperar los datos e invitar a reintentar.
- Las claves de API se mantienen en la configuración del servidor y no se muestran en respuestas.

RB-10: Enlaces, contactos y acciones del ejercicio
- Los enlaces con dominio .example son ficticios.
- No enviar mensajes, efectuar pagos, reservar puestos ni confirmar inscripciones.
- Si se solicita una de esas acciones, explicar el alcance informativo.

RB-11: Validación de datos (formulario de administración)
- Validar identificador único, nombre, fechas válidas y orden de fechas.
- Mantener costo y cupos como números no negativos; no convertir un campo vacío en cero.
- Conservar desconocidos como información no disponible.

RB-12: Importación de Excel
- Leer los encabezados y códigos del Excel, presentar una vista previa y errores por fila.
- Si un código ya existe, solicitar una decisión explícita antes de reemplazarlo.

RB-13: Cobertura de pantallas
- Definición de qué debe mostrar cada pantalla.
"""

import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.services.lectura_eventos import leer_eventos, obtener_evento_por_codigo as obtener_evento_por_nombre

AVISO_DATOS = "Información basada en datos de la Red Alajuelita Artesanal"
DOMINIO_EJEMPLO = ".example"


# ============================================================================
# RB-09: Consulta mediante herramientas y API
# ============================================================================

class ConsultaFallidaError(Exception):
    """Excepción lanzada cuando una consulta de datos falla."""
    pass


def obtener_clave_api() -> Optional[str]:
    """Lee la clave de API de IA desde el entorno (.env)."""
    clave = os.environ.get("API_IA_CLAVE")
    if clave and clave != "tu_clave_aqui":
        return clave
    return None


def clave_api_configurada() -> bool:
    """Devuelve True si existe una clave de API configurada."""
    return obtener_clave_api() is not None


# ============================================================================
# RB-10: Enlaces, contactos y acciones del ejercicio
# ============================================================================

def es_enlace_ejemplo(valor) -> bool:
    """Devuelve True si el valor es un enlace o correo con dominio .example."""
    if valor is None:
        return False
    texto = str(valor).lower()
    return DOMINIO_EJEMPLO in texto


def es_accion_fuera_de_alcance(solicitud: str) -> bool:
    """
    Detecta si la solicitud pide una acción fuera del alcance: enviar mensajes,
    efectuar pagos, reservar puestos, confirmar inscripciones.
    """
    palabras = [
        "enviar mensaje", "enviar whatsapp", "efectuar pago", "pagar",
        "reservar puesto", "reservar campo", "confirmar inscripción",
        "inscribirme", "inscribir", "reservame", "reservar",
    ]
    solicitud_lower = solicitud.lower()
    return any(palabra in solicitud_lower for palabra in palabras)


def respuesta_accion_fuera_de_alcance() -> str:
    """Devuelve el mensaje estándar para solicitudes fuera de alcance (RB-10)."""
    return (
        "Esta aplicación solo informa; no envía mensajes, no efectúa pagos, "
        "no reserva puestos ni confirma inscripciones. Puede consultar el "
        "procedimiento registrado como parte de la simulación."
    )


# ============================================================================
# RB-11: Validación de datos (formulario de administración)
# ============================================================================

class ValidacionError(Exception):
    """Excepción lanzada cuando un dato no pasa la validación."""
    def __init__(self, campo: str, mensaje: str):
        self.campo = campo
        self.mensaje = mensaje
        super().__init__(f"{campo}: {mensaje}")


def validar_nombre(nombre: str) -> None:
    """Valida que el nombre esté presente."""
    if not nombre or str(nombre).strip() == "":
        raise ValidacionError("Nombre", "El nombre del evento es obligatorio.")


def validar_costo(costo) -> None:
    """Valida que el costo sea un número no negativo o un valor conocido."""
    if costo is None or str(costo).strip() == "":
        return  # Campo opcional vacío = desconocido, no cero
    texto = str(costo).strip().lower()
    if texto in ("no aplica", "no indicado", "por confirmar", "gratuito", "gratis"):
        return  # Valores conocidos, no son cero numérico
    try:
        # Extraer número de strings como "c1000" o "₡1000"
        import re
        match = re.search(r'[\d,]+', texto)
        if match:
            valor = int(match.group().replace(",", ""))
            if valor < 0:
                raise ValidacionError("Costo de participación", "El costo no puede ser negativo.")
    except (ValueError, TypeError):
        pass


def validar_cupos(cupos) -> None:
    """Valida que los cupos sean un número no negativo."""
    if cupos is None or str(cupos).strip() == "":
        return  # Campo opcional vacío = desconocido, no cero
    texto = str(cupos).strip()
    try:
        valor = int(texto)
        if valor < 0:
            raise ValidacionError("Espacios disponibles", "Los cupos no pueden ser negativos.")
    except (ValueError, TypeError):
        pass


def validar_fechas(fecha_inicio, fecha_fin) -> None:
    """Valida fechas válidas y orden de fechas (inicio <= fin)."""
    from app.utils.formato import _parse_valor
    fi = _parse_valor(fecha_inicio)
    ff = _parse_valor(fecha_fin)
    if fi is None:
        raise ValidacionError("Fecha de inicio", "Fecha de inicio inválida.")
    if ff is not None and fi > ff:
        raise ValidacionError(
            "Fechas", "La fecha de inicio no puede ser posterior a la fecha de finalización."
        )


def validar_datos_evento(datos: Dict[str, Any], nombres_existentes: List[str]) -> List[Dict[str, str]]:
    """
    Valida todos los datos de un evento antes de guardar.
    Devuelve lista de errores (vacía si todo es válido).
    """
    errores: List[Dict[str, str]] = []

    try:
        validar_nombre(datos.get("Nombre del evento", ""))
    except ValidacionError as e:
        errores.append({"campo": e.campo, "mensaje": e.mensaje})

    identificador = str(datos.get("Nombre del evento", "")).strip()
    if identificador in nombres_existentes:
        errores.append({
            "campo": "Nombre del evento",
            "mensaje": f"El evento '{identificador}' ya existe. Use otro nombre."
        })

    try:
        validar_fechas(datos.get("Fecha de inicio"), datos.get("Fecha de finalización"))
    except ValidacionError as e:
        errores.append({"campo": e.campo, "mensaje": e.mensaje})

    try:
        validar_costo(datos.get("Costo de participación"))
    except ValidacionError as e:
        errores.append({"campo": e.campo, "mensaje": e.mensaje})

    try:
        validar_cupos(datos.get("Cantidad total de cupos"))
    except ValidacionError as e:
        errores.append({"campo": e.campo, "mensaje": e.mensaje})

    return errores


# ============================================================================
# RB-12: Importación de Excel
# ============================================================================

def detectar_nombres_duplicados(
    eventos_importados: List[Dict[str, Any]], nombres_existentes: List[str]
) -> List[str]:
    """Detecta nombres que ya existen en el sistema."""
    duplicados: List[str] = []
    for evento in eventos_importados:
        nombre = str(evento.get("Nombre del evento", "")).strip()
        if nombre and nombre in nombres_existentes:
            duplicados.append(nombre)
    return duplicados


def preparar_vista_previa_importacion(
    eventos_importados: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Prepara una vista previa de la importación."""
    errores_por_fila: List[str] = []
    for idx, evento in enumerate(eventos_importados, start=1):
        nombre = evento.get("Nombre del evento", "Sin nombre")
        if not nombre or str(nombre).strip() == "":
            errores_por_fila.append(f"Fila {idx}: nombre del evento faltante")

    return {
        "total_eventos": len(eventos_importados),
        "nombres": [str(e.get("Nombre del evento", "")) for e in eventos_importados],
        "errores_por_fila": errores_por_fila,
        "puede_importar": len(errores_por_fila) == 0,
    }


def requiere_decision_nombre_existente(nombres_duplicados: List[str]) -> bool:
    """Devuelve True si hay nombres duplicados que requieren decisión explícita."""
    return len(nombres_duplicados) > 0


# ============================================================================
# RB-13: Cobertura de pantallas
# ============================================================================

def obtener_configuracion_pantalla_inicio() -> Dict[str, Any]:
    """Devuelve la configuración esperada para la pantalla de inicio y listado."""
    return {
        "nombre_app": "Asistente de Eventos RAA",
        "aviso_datos": "Información basada en datos de la Red Alajuelita Artesanal",
        "campos_tarjeta": ["nombre", "tipo", "lugar", "fecha", "horario"],
        "filtros": ["nombre", "tipo", "lugar", "fecha"],
        "mensaje_sin_resultados": "No encontramos eventos con esos filtros",
    }


def obtener_configuracion_pantalla_detalle() -> Dict[str, Any]:
    """Devuelve la configuración esperada para la pantalla de detalle del evento."""
    return {
        "bloques": [
            "Información general y ubicación",
            "Fechas y horarios",
            "Espacio, mesa y toldo",
            "Facilidades y condiciones de participación",
            "Manejo del stand y mercadería entre días",
            "Costos, donaciones y pagos",
            "Inscripciones y cupos",
            "Coordinación y comentarios adicionales",
        ],
        "dato_faltante": "Información pendiente",
    }


def obtener_configuracion_pantalla_chat() -> Dict[str, Any]:
    """Devuelve la configuración esperada para la pantalla de chat."""
    return {
        "elementos": ["historial de sesión", "campo de pregunta", "botón Enviar", "botón Nueva conversación"],
        "preguntas_sugeridas": [
            "¿Cuándo es el evento?",
            "¿Dónde se lleva a cabo?",
            "¿Cuál es el costo de participación?",
            "¿Hay cupos disponibles?",
            "¿Cuál es el coordinador?",
        ],
    }
