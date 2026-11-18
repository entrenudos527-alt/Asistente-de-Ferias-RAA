"""
Reglas RB-05 y RB-06.

RB-05: Redactar con respaldo en el registro
- Responder en español claro, cordial y breve.
- Priorizar el dato solicitado y añadir solo las condiciones necesarias para interpretarlo.
- No inventar información durante la conversación. Los datos del Excel sí pueden consultarse.
- No confundir campos vacíos con "No", "No aplica", cero ni gratuito.
- Mostrar permanentemente la referencia al evento consultado.

RB-06: Información faltante y preguntas fuera del tema
- Campos vacíos = desconocidos (información pendiente).
- Distinguir "Sí", "No", "No aplica", "Por confirmar" y cero: son estados distintos.
- Si falta información, responder únicamente lo conocido y explicar qué dato no está disponible.
- Cuando exista un contacto autorizado, ofrecerlo como referencia.
- Si preguntan por información no registrada, no estimar valores ni buscar fuera del conjunto de datos.
"""

from typing import Dict, List, Optional, Tuple

# Campos que se consideran "desconocidos" si están vacíos
VALORES_DESCONOCIDOS = {"", "por confirmar", "por definir", "no indicado", "no indicada"}

# Valores que SÍ son conocidos (no se tratan como desconocidos aunque sean negativos o nulos)
VALORES_CONOCIDOS = {"sí", "si", "no", "no aplica", "por confirmar", "0", "cero"}

AVISO_DATOS = "Información basada en datos de la Red Alajuelita Artesanal"


def es_valor_desconocido(valor) -> bool:
    """Devuelve True si el campo se considera desconocido (vacío o valores especiales)."""
    if valor is None:
        return True
    if isinstance(valor, str) and valor.strip().lower() in VALORES_DESCONOCIDOS:
        return True
    if isinstance(valor, str) and valor.strip() == "":
        return True
    return False


def necesita_aclaracion_practica(tema: str) -> bool:
    """Siempre False para este proyecto: no hay escenario de práctica simulada."""
    return False


def obtener_contacto_autorizado(registro: Dict) -> Optional[Dict[str, str]]:
    """
    Extrae los datos de contacto autorizado de un registro de evento.
    Devuelve None si no hay contacto disponible.
    """
    nombre = registro.get("Coordinador del evento")
    whatsapp = registro.get("WhatsApp de coordinación")

    if es_valor_desconocido(nombre) and es_valor_desconocido(whatsapp):
        return None

    return {
        "nombre": str(nombre) if not es_valor_desconocido(nombre) else "No indicado",
        "whatsapp": str(whatsapp) if not es_valor_desconocido(whatsapp) else "No indicado",
    }


def es_pregunta_fuera_de_tema(pregunta: str) -> Tuple[bool, Optional[str]]:
    """
    Detecta si la pregunta pide información no registrada.
    Devuelve (es_fuera_de_tema, campo_faltante).
    """
    palabras_fuera = ["comprador", "compradores", "venta", "ganancia", "ganancias", "ganar", "gana",
                      "clima", "tiempo", "afluencia", "visitante", "público asistente", "cuántas personas",
                      "beneficio", "utilidad"]
    pregunta_lower = pregunta.lower()
    for palabra in palabras_fuera:
        if palabra in pregunta_lower:
            return True, palabra
    return False, None


def construir_referencia_evento(evento: Dict) -> str:
    """Construye la referencia visible al evento: nombre del evento."""
    nombre = evento.get("Nombre del evento", "No disponible")
    return f"Evento: {nombre}"


def formatear_respuesta_con_respaldo(
    respuesta_texto: str,
    evento: Dict,
) -> str:
    """
    Formatea una respuesta aplicando RB-05: añade referencia visible al evento.
    """
    partes = [respuesta_texto.strip()]

    # Referencia visible al evento
    referencia = construir_referencia_evento(evento)
    partes.append(f"\n{referencia}")

    # Aviso permanente de datos
    partes.append(f"\n{AVISO_DATOS}")

    return "\n".join(partes)


def manejar_informacion_faltante(
    campos_conocidos: Dict[str, object],
    campos_faltantes: List[str],
    contacto: Optional[Dict[str, str]] = None,
) -> str:
    """
    Construye una respuesta aplicando RB-06: responde solo lo conocido,
    explica qué falta y ofrece contacto autorizado si existe.
    """
    partes = []

    # Lo conocido
    if campos_conocidos:
        conocido_txt = "; ".join(f"{k}: {v}" for k, v in campos_conocidos.items())
        partes.append(f"Lo que sí consta en el registro: {conocido_txt}.")

    # Lo que falta
    if campos_faltantes:
        faltante_txt = ", ".join(campos_faltantes)
        partes.append(f"No consta en el registro: {faltante_txt}.")
        partes.append("Te sugerimos consultar con la coordinación del evento para obtener esa información.")

    # Contacto autorizado
    if contacto:
        partes.append(
            f"Coordinador: {contacto['nombre']}. WhatsApp: {contacto['whatsapp']}."
        )

    if not partes:
        partes.append("No hay información disponible en el registro para esta consulta.")

    return " ".join(partes)


def validar_no_confundir_campos(campo_solicitado: str, campo_devuelto: str) -> bool:
    """
    Devuelve True si el campo devuelto NO es una confusión prohibida.
    """
    solicitado = campo_solicitado.lower().strip()
    devuelto = campo_devuelto.lower().strip()
    pares_no_confundir = [
        ("costo", "donación"),
        ("donación", "costo"),
        ("cupos disponibles", "cupos totales"),
        ("montaje", "desmontaje"),
        ("inicio", "finalización"),
    ]
    for prohibido, sustituto in pares_no_confundir:
        if prohibido in solicitado and sustituto in devuelto:
            return False
    return True
