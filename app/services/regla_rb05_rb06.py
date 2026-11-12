"""
Reglas RB-05 y RB-06.

RB-05: Redactar con respaldo en el registro
- Responder en español claro, cordial y breve.
- Priorizar el dato solicitado y añadir solo las condiciones necesarias para interpretarlo.
- No inventar información durante la conversación. Los datos ficticios preparados en el Excel
  sí pueden consultarse porque forman parte del escenario definido.
- No convertir el horario de atención en horario de montaje, el responsable de la actividad en
  contacto autorizado, ni los cupos disponibles en una reserva.
- Indicar el código de la actividad y la última actualización en una referencia visible junto a
  la respuesta. Ante cupos, mostrar además cuándo se verificaron.
- Mostrar permanentemente "Demostración con datos simulados". En respuestas sobre costos, cupos,
  contactos o inscripción, aclarar que corresponden al escenario de práctica.

RB-06: Información faltante y preguntas fuera del tema
- Campos vacíos, "Por confirmar", "Por definir" o "No indicado" = desconocidos.
- Distinguir "No aplica", "No habilitado" y el número cero: no representan el mismo estado.
  El valor 0 en cupos significa que no hay espacios.
- Si falta información, responder únicamente lo conocido y explicar qué dato no está disponible.
- Cuando exista un contacto autorizado, ofrecerlo como referencia de práctica.
- Si preguntan por compradores, ganancias, clima u otra información no registrada, no estimar
  valores ni buscar fuera del conjunto de datos en esta versión.
"""

from typing import Dict, List, Optional, Tuple

# Campos que se consideran "desconocidos" si están vacíos o tienen estos valores
VALORES_DESCONOCIDOS = {"", "por confirmar", "por definir", "no indicado", "no indicada"}

AVISO_SIMULACION = "Demostración con datos simulados"

# Temas que requieren aclaración de que son escenario de práctica
TEMAS_PRACTICA = {"costo", "cupo", "contacto", "inscripción"}

# Campos que NO deben confundirse entre sí
CAMPOS_NO_CONFUNDIR = {
    "horario de atención": "horario de montaje",
    "responsable de la actividad": "contacto autorizado",
    "cupos disponibles": "reserva",
}


def es_valor_desconocido(valor) -> bool:
    """Devuelve True si el campo se considera desconocido (vacío o valores especiales)."""
    if valor is None:
        return True
    if isinstance(valor, str) and valor.strip().lower() in VALORES_DESCONOCIDOS:
        return True
    return False


def necesita_aclaracion_practica(tema: str) -> bool:
    """Devuelve True si el tema requiere aclarar que es escenario de práctica."""
    return any(palabra in tema.lower() for palabra in TEMAS_PRACTICA)


def obtener_contacto_autorizado(registro: Dict) -> Optional[Dict[str, str]]:
    """
    Extrae los datos de contacto autorizado de un registro.
    Devuelve None si no hay contacto disponible.
    """
    nombre = registro.get("Contacto autorizado de práctica")
    cargo = registro.get("Cargo del contacto")
    telefono = registro.get("Teléfono o WhatsApp de práctica")
    correo = registro.get("Correo de práctica")
    horario = registro.get("Horario del contacto")

    if es_valor_desconocido(nombre) and es_valor_desconocido(correo) and es_valor_desconocido(telefono):
        return None

    return {
        "nombre": str(nombre) if not es_valor_desconocido(nombre) else "No indicado",
        "cargo": str(cargo) if not es_valor_desconocido(cargo) else "No indicado",
        "telefono": str(telefono) if not es_valor_desconocido(telefono) else "No habilitado en el ejercicio",
        "correo": str(correo) if not es_valor_desconocido(correo) else "No indicado",
        "horario": str(horario) if not es_valor_desconocido(horario) else "No indicado",
    }


def es_pregunta_fuera_de_tema(pregunta: str) -> Tuple[bool, Optional[str]]:
    """
    Detecta si la pregunta pide información no registrada (compradores, ganancias, clima, etc.).
    Devuelve (es_fuera_de_tema, campo_faltante).
    """
    palabras_fuera = ["comprador", "compradores", "venta", "ganancia", "ganancias", "ganar", "gana", "clima", "tiempo", "afluencia",
                      "visitante", "público asistente", "cuántas personas"]
    pregunta_lower = pregunta.lower()
    for palabra in palabras_fuera:
        if palabra in pregunta_lower:
            return True, palabra
    return False, None


def construir_referencia_registro(
    registro: Dict, incluir_verificacion_cupos: bool = False
) -> str:
    """
    Construye la referencia visible al registro: código + última actualización.
    Si incluir_verificacion_cupos es True, añade la fecha de verificación de cupos.
    """
    codigo = registro.get("Identificador", "No disponible")
    ultima_actualizacion = registro.get("Última actualización", "No disponible")
    referencia = f"Código: {codigo} | Última actualización: {ultima_actualizacion}"
    if incluir_verificacion_cupos:
        verificacion = registro.get("Verificación de espacios", "No disponible")
        referencia += f" | Verificación de cupos: {verificacion}"
    return referencia


def formatear_respuesta_con_respaldo(
    respuesta_texto: str,
    registro: Dict,
    es_practica: bool = False,
    incluir_verificacion_cupos: bool = False,
) -> str:
    """
    Formatea una respuesta aplicando RB-05: añade aviso de simulación si es necesario,
    referencia visible al registro, y aclaración de escenario de práctica.
    """
    partes = [respuesta_texto.strip()]

    # Referencia visible al registro
    referencia = construir_referencia_registro(registro, incluir_verificacion_cupos)
    partes.append(f"\n{referencia}")

    # Aviso de simulación permanente
    partes.append(f"\n{AVISO_SIMULACION}")

    # Si es tema de práctica, aclarar que es escenario simulado
    if es_practica:
        partes.append("Esta información corresponde al escenario de práctica.")

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

    # Contacto autorizado
    if contacto:
        partes.append(
            f"Para más información, puede contactar a {contacto['nombre']} "
            f"({contacto['cargo']}). Teléfono: {contacto['telefono']}. "
            f"Correo: {contacto['correo']}."
        )

    if not partes:
        partes.append("No hay información disponible en el registro para esta consulta.")

    return " ".join(partes)


def validar_no_confundir_campos(campo_solicitado: str, campo_devuelto: str) -> bool:
    """
    Devuelve True si el campo devuelto NO es una confusión prohibida del campo solicitado.
    RB-05: no convertir horario de atención en montaje, responsable en contacto, cupos en reserva.
    """
    solicitado = campo_solicitado.lower().strip()
    devuelto = campo_devuelto.lower().strip()
    for prohibido, sustituto in CAMPOS_NO_CONFUNDIR.items():
        if prohibido in solicitado and sustituto in devuelto:
            return False
    return True
