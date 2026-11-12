"""
Reglas RB-09 a RB-13.

RB-09: Consulta mediante herramientas y API
- La implementación deberá permitir buscar actividades y recuperar una ficha por identificador.
- El agente utilizará esas herramientas para obtener datos antes de responder preguntas específicas.
- Las instrucciones de un visitante no se tratarán como autorización para cambiar registros ni como
  fuente de información sobre una feria.
- Si la consulta falla, el servicio no está disponible o el registro no se encuentra, indicar que
  no fue posible recuperar los datos e invitar a reintentar. No responder como si la búsqueda
  hubiera tenido éxito.
- Las claves de API se mantienen en la configuración del servidor y no se muestran en respuestas.

RB-10: Enlaces, contactos y acciones del ejercicio
- Los enlaces y correos con dominio .example son ficticios. Mostrarlos como texto identificado
  como ejemplo y no ofrecerlos como canales reales ni botones operativos.
- Si Teléfono o WhatsApp de práctica indica "No habilitado en el ejercicio", comunicar ese estado
  sin inventar un número.
- No enviar mensajes, efectuar pagos, reservar puestos ni confirmar inscripciones. Si se solicita
  una de esas acciones, explicar el alcance informativo y describir el procedimiento registrado
  como parte de la simulación.

RB-11: Validación de datos (formulario de administración)
- Validar identificador único, nombre, fechas válidas y orden de fechas.
- Mantener costo y cupos como números no negativos; no convertir un campo vacío en cero.
- Conservar desconocidos como información no disponible.
- No exigir que todo dato opcional esté completo para guardar una ficha.
- Para el modelo de una jornada por registro, validar que montaje no sea posterior al inicio de
  atención y que desmontaje no sea anterior al cierre.
- Registrar el responsable de actualización y validar fecha y hora límite de inscripción.
- Al guardar correctamente, mostrar confirmación, actualizar la fecha de modificación y reflejar
  el cambio en la ficha y el chat. Cancelar no altera el registro.

RB-12: Importación de Excel
- Leer los encabezados y códigos del Excel, presentar una vista previa y errores por fila.
- La carga inicial incorpora los 11 registros.
- Si un código ya existe, solicitar una decisión explícita antes de reemplazarlo.
- No modificar la hoja de preguntas y respuestas ni usarla como fuente de fichas.

RB-13: Cobertura de pantallas (desde Pantallas_Funciones_y_Agentes_RAA.docx)
- Definición de qué debe mostrar cada pantalla (listado, detalle, chat, administración).
"""

import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.services.lectura_datos import leer_actividades, obtener_actividad_por_codigo
from app.services.regla_rb02 import obtener_fecha_referencia

# Encabezados clave
ENC_IDENTIFICADOR = "Identificador"
ENC_COSTO_PARTICIPACION = "Costo de participación"
ENC_ESPACIOS_DISPONIBLES = "Espacios disponibles"
ENC_MONEDA = "Moneda"
ENC_UNIDAD_COBRO = "Unidad de cobro"
ENC_INGRESO_MONTAJE = "Ingreso y montaje"
ENC_INICIO_ATENCION_SIMULADO = "Inicio de atención simulado"
ENC_SALIDA_DESMONTAJE = "Salida y desmontaje"
ENC_CIERRE_ATENCION_SIMULADO = "Cierre de atención simulado"
ENC_FECHA_LIMITE_INSCRIPCION = "Fecha límite de inscripción"
ENC_HORA_LIMITE_INSCRIPCION = "Hora límite de inscripción"
ENC_RESPONSABLE_ACTUALIZACION = "Responsable de actualización"
ENC_TEL_WHATSAPP = "Teléfono o WhatsApp de práctica"

AVISO_SIMULACION = "Demostración con datos simulados"
DOMINIO_EJEMPLO = ".example"


# ============================================================================
# RB-09: Consulta mediante herramientas y API
# ============================================================================

class ConsultaFallidaError(Exception):
    """Excepción lanzada cuando una consulta de datos falla."""
    pass


def buscar_actividad_por_identificador(
    identificador: str,
) -> Dict[str, Any]:
    """
    Busca una actividad por su identificador único (RB-09).
    Lanza ConsultaFallidaError si no se encuentra.
    """
    registro = obtener_actividad_por_codigo(identificador)
    if registro is None:
        raise ConsultaFallidaError(
            f"No se encontró la actividad con identificador '{identificador}'."
        )
    return registro


def obtener_clave_api() -> Optional[str]:
    """
    Lee la clave de API de IA desde el entorno (.env).
    Nunca se hardcodea ni se muestra en respuestas (RB-09).
    """
    clave = os.environ.get("API_IA_CLAVE")
    if clave and clave != "tu_clave_aqui":
        return clave
    return None


def clave_api_configurada() -> bool:
    """Devuelve True si existe una clave de API configurada (no es el valor por defecto)."""
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


def formatear_contacto_ejemplo(telefono_whatsapp: Optional[str]) -> str:
    """
    Formatea el teléfono/WhatsApp de práctica.
    Si indica "No habilitado en el ejercicio", comunican ese estado sin inventar un número.
    Si es un enlace .example, se identifica como ejemplo.
    """
    if telefono_whatsapp is None or str(telefono_whatsapp).strip() == "":
        return "No indicado"
    texto = str(telefono_whatsapp).strip()
    if "no habilitado en el ejercicio" in texto.lower():
        return "No habilitado en el ejercicio"
    if es_enlace_ejemplo(texto):
        return f"{texto} (enlace de ejemplo, no operativo)"
    return texto


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


def validar_identificador_unico(
    identificador: str, codigos_existentes: List[str], excluir_codigo: Optional[str] = None
) -> None:
    """Valida que el identificador sea único."""
    if not identificador or str(identificador).strip() == "":
        raise ValidacionError("Identificador", "El identificador es obligatorio.")
    ident = str(identificador).strip()
    if excluir_codigo and ident == excluir_codigo:
        return
    if ident in codigos_existentes:
        raise ValidacionError(
            "Identificador", f"El código '{ident}' ya existe. Use otro código."
        )


def validar_nombre(nombre: str) -> None:
    """Valida que el nombre esté presente."""
    if not nombre or str(nombre).strip() == "":
        raise ValidacionError("Nombre", "El nombre de la actividad es obligatorio.")


def validar_fechas(
    fecha_inicio, fecha_fin, dias_participacion: Optional[str] = None
) -> None:
    """Valida fechas válidas y orden de fechas (inicio <= fin)."""
    fi = _parse_fecha(fecha_inicio)
    ff = _parse_fecha(fecha_fin)
    if fi is None:
        raise ValidacionError("Fecha de inicio", "Fecha de inicio inválida.")
    if ff is not None and fi > ff:
        raise ValidacionError(
            "Fechas", "La fecha de inicio no puede ser posterior a la fecha de finalización."
        )


def validar_costo(costo) -> None:
    """Valida que el costo sea un número no negativo."""
    if costo is None or str(costo).strip() == "":
        return  # Campo opcional vacío = desconocido, no cero
    try:
        valor = float(costo)
    except (ValueError, TypeError):
        raise ValidacionError("Costo de participación", "El costo debe ser un número.")
    if valor < 0:
        raise ValidacionError("Costo de participación", "El costo no puede ser negativo.")


def validar_cupos(cupos) -> None:
    """Valida que los cupos sean un número no negativo."""
    if cupos is None or str(cupos).strip() == "":
        return  # Campo opcional vacío = desconocido, no cero
    try:
        valor = int(cupos)
    except (ValueError, TypeError):
        raise ValidacionError("Espacios disponibles", "Los cupos deben ser un número entero.")
    if valor < 0:
        raise ValidacionError("Espacios disponibles", "Los cupos no pueden ser negativos.")


def validar_orden_horario_jornada(
    ingreso_montaje, inicio_atencion, salida_desmontaje, cierre_atencion
) -> None:
    """
    Para el modelo de una jornada por registro:
    - Montaje no sea posterior al inicio de atención.
    - Desmontaje no sea anterior al cierre.
    """
    im = _parse_hora(ingreso_montaje)
    ia = _parse_hora(inicio_atencion)
    sd = _parse_hora(salida_desmontaje)
    ca = _parse_hora(cierre_atencion)

    if im is not None and ia is not None and im > ia:
        raise ValidacionError(
            "Horario", "El ingreso y montaje no puede ser posterior al inicio de atención."
        )
    if sd is not None and ca is not None and sd < ca:
        raise ValidacionError(
            "Horario", "La salida y desmontaje no puede ser anterior al cierre de atención."
        )


def validar_responsable_actualizacion(responsable: str) -> None:
    """Valida que se registre el responsable de actualización."""
    if not responsable or str(responsable).strip() == "":
        raise ValidacionError(
            "Responsable de actualización",
            "Debe indicar quién es el responsable de actualizar la ficha.",
        )


def validar_fecha_hora_limite_inscripcion(
    fecha_limite, hora_limite, fecha_ref: datetime
) -> None:
    """Valida fecha y hora límite de inscripción."""
    fl = _parse_fecha(fecha_limite)
    if fl is None:
        raise ValidacionError(
            "Fecha límite de inscripción", "La fecha límite de inscripción es obligatoria."
        )
    # Validar que no sea anterior a la fecha de referencia (opcional, según contexto)


def validar_fecha_hora_limite_pago(
    fecha_limite_pago,
) -> None:
    """Valida fecha límite de pago si se proporciona."""
    if fecha_limite_pago is not None and str(fecha_limite_pago).strip() != "":
        _parse_fecha(fecha_limite_pago)


def validar_datos_ficha(datos: Dict[str, Any], codigos_existentes: List[str]) -> List[Dict[str, str]]:
    """
    Valida todos los datos de una ficha antes de guardar.
    Devuelve lista de errores (vacía si todo es válido).
    """
    errores: List[Dict[str, str]] = []

    try:
        validar_identificador_unico(
            datos.get("Identificador", ""), codigos_existentes
        )
    except ValidacionError as e:
        errores.append({"campo": e.campo, "mensaje": e.mensaje})

    try:
        validar_nombre(datos.get("Actividad", ""))
    except ValidacionError as e:
        errores.append({"campo": e.campo, "mensaje": e.mensaje})

    try:
        validar_fechas(
            datos.get("Fecha de inicio"),
            datos.get("Fecha de finalización"),
            datos.get("Días de participación"),
        )
    except ValidacionError as e:
        errores.append({"campo": e.campo, "mensaje": e.mensaje})

    try:
        validar_costo(datos.get("Costo de participación"))
    except ValidacionError as e:
        errores.append({"campo": e.campo, "mensaje": e.mensaje})

    try:
        validar_cupos(datos.get("Espacios disponibles"))
    except ValidacionError as e:
        errores.append({"campo": e.campo, "mensaje": e.mensaje})

    try:
        validar_orden_horario_jornada(
            datos.get("Ingreso y montaje"),
            datos.get("Inicio de atención simulado"),
            datos.get("Salida y desmontaje"),
            datos.get("Cierre de atención simulado"),
        )
    except ValidacionError as e:
        errores.append({"campo": e.campo, "mensaje": e.mensaje})

    try:
        validar_responsable_actualizacion(datos.get("Responsable de actualización", ""))
    except ValidacionError as e:
        errores.append({"campo": e.campo, "mensaje": e.mensaje})

    try:
        validar_fecha_hora_limite_inscripcion(
            datos.get("Fecha límite de inscripción"),
            datos.get("Hora límite de inscripción"),
            datetime.fromisoformat(obtener_fecha_referencia()),
        )
    except ValidacionError as e:
        errores.append({"campo": e.campo, "mensaje": e.mensaje})

    return errores


# ============================================================================
# RB-12: Importación de Excel
# ============================================================================

def detectar_codigos_duplicados(
    registros_importados: List[Dict[str, Any]], codigos_existentes: List[str]
) -> List[str]:
    """Detecta códigos que ya existen en el sistema."""
    duplicados: List[str] = []
    for registro in registros_importados:
        codigo = str(registro.get(ENC_IDENTIFICADOR, "")).strip()
        if codigo and codigo in codigos_existentes:
            duplicados.append(codigo)
    return duplicados


def preparar_vista_previa_importacion(
    registros_importados: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Prepara una vista previa de la importación: total de registros,
    códigos y errores por fila.
    """
    errores_por_fila: List[str] = []
    for idx, registro in enumerate(registros_importados, start=1):
        codigo = registro.get(ENC_IDENTIFICADOR, "Sin código")
        if not codigo or str(codigo).strip() == "":
            errores_por_fila.append(f"Fila {idx}: código faltante")

    return {
        "total_registros": len(registros_importados),
        "codigos": [str(r.get(ENC_IDENTIFICADOR, "")) for r in registros_importados],
        "errores_por_fila": errores_por_fila,
        "puede_importar": len(errores_por_fila) == 0,
    }


def requiere_decision_codigo_existente(codigos_duplicados: List[str]) -> bool:
    """Devuelve True si hay códigos duplicados que requieren decisión explícita."""
    return len(codigos_duplicados) > 0


# ============================================================================
# RB-13: Cobertura de pantallas
# ============================================================================

def obtener_configuracion_pantalla_inicio() -> Dict[str, Any]:
    """Devuelve la configuración esperada para la pantalla de inicio y listado."""
    return {
        "nombre_app": "Asistente de Ferias RAA",
        "aviso_simulacion": AVISO_SIMULACION,
        "fecha_demo": obtener_fecha_referencia(),
        "orden_por": "fecha y hora de atención",
        "campos_tarjeta": [
            "nombre", "fecha", "lugar", "horario de atención",
            "estado de la actividad", "estado de inscripción",
        ],
        "botones": ["Ver detalles", "Consultar al asistente"],
        "filtros": ["nombre o código", "fecha", "lugar"],
        "mensaje_sin_resultados": "No encontramos actividades con esos filtros",
        "accion_error": "Reintentar",
    }


def obtener_configuracion_pantalla_detalle() -> Dict[str, Any]:
    """Devuelve la configuración esperada para la pantalla de detalle de la feria."""
    return {
        "bloques": [
            "información general",
            "fechas y horarios",
            "ubicación y acceso",
            "costos",
            "requisitos y equipo",
            "inscripción y cupos",
            "contacto y actualización",
        ],
        "separar": [
            "atención, ingreso y montaje",
            "salida y desmontaje",
        ],
        "mostrar_costo_con": ["moneda", "unidad de cobro"],
        "mostrar_fecha_limite_inscripcion": True,
        "mostrar_ultima_verificacion_cupos": True,
        "contactos_ejemplo_no_operativos": True,
        "dato_faltante": "Información no disponible",
        "botones": ["Consultar sobre esta feria", "Volver al listado"],
    }


def obtener_configuracion_pantalla_chat() -> Dict[str, Any]:
    """Devuelve la configuración esperada para la pantalla de chat."""
    return {
        "elementos": ["historial de sesión", "campo de pregunta", "botón Enviar", "botón Nueva conversación"],
        "aviso_simulacion": AVISO_SIMULACION,
        "preguntas_sugeridas": [
            "¿Cuánto cuesta participar?",
            "¿Qué debo llevar?",
        ],
        "mostrar_al_recibir": [
            "respuesta", "identificador de la feria", "última actualización",
        ],
        "mostrar_cupos_con": "fecha de verificación",
        "ambigüedad": "ofrecer opciones con nombre, fecha y lugar",
        "nueva_conversacion": "borra el contexto anterior",
    }


def obtener_configuracion_paneles_admin() -> Dict[str, Any]:
    """Devuelve la configuración esperada para las pantallas de administración."""
    return {
        "acceso": ["formulario de ingreso", "salida de sesión"],
        "error_credenciales": "error general ante credenciales incorrectas",
        "no_publicar_credenciales": True,
        "panel_columnas": ["código", "nombre", "fecha", "estado", "última actualización"],
        "acciones": ["Crear ficha", "Editar", "Importar Excel"],
        "seccion_preguntas_sin_respuesta": ["fecha", "motivo"],
        "tablero_estadisticas": False,
    }


# ============================================================================
# Utilidades internas
# ============================================================================

def _parse_fecha(valor) -> Optional[datetime]:
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
            try:
                return datetime.strptime(valor.strip(), fmt)
            except ValueError:
                continue
    return None


def _parse_hora(valor) -> Optional[datetime]:
    """Convierte un string de hora (ej. '7:30 a. m.') a datetime para comparación."""
    if valor is None or str(valor).strip() == "":
        return None
    texto = str(valor).strip().lower()
    # Manejar formatos como "7:30 a. m.", "8:30 a. m.", "5:00 p. m."
    texto = texto.replace("a. m.", "am").replace("p. m.", "pm").replace(".", "").strip()
    for fmt in ("%I:%M%p", "%I:%M %p", "%H:%M"):
        try:
            return datetime.strptime(texto, fmt)
        except ValueError:
            continue
    return None
