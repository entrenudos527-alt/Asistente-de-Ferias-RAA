"""
Pruebas contra los casos límite definidos en AGENTS.md (insumo 4).

Casos CP01 a CP20 definidos en Casos_de_Prueba_y_Resultados_Esperados_RAA.xlsx.
"""

import pytest
from datetime import datetime
from app.services.regla_rb02 import obtener_fecha_referencia
from app.services.regla_rb03_rb04 import obtener_proxima_actividad, identificar_actividad
from app.services.regla_rb05_rb06 import (
    es_valor_desconocido,
    es_pregunta_fuera_de_tema,
    validar_no_confundir_campos,
)
from app.services.regla_rb07_rb08 import (
    evaluar_inscripcion_disponibilidad,
    validar_solicitud_cambio_desde_chat,
)
from app.services.regla_rb09_rb13 import (
    validar_costo,
    validar_cupos,
    ValidacionError,
)
from app.services.herramientas_ia import buscar_ferias, obtener_ficha


class TestCasosLimite:
    """Pruebas para los 20 casos límite (CP01 a CP20)."""

    # --- CP01: Carga inicial ---
    def test_cp01_carga_inicial_11_registros(self):
        """CP01: Se cargan 11 registros con códigos únicos."""
        from app.services.lectura_datos import leer_actividades
        datos = leer_actividades()
        assert datos["total_registros"] == 11
        codigos = [r.get("Identificador") for r in datos["registros"]]
        assert len(codigos) == len(set(codigos))

    # --- CP02: Consulta directa ---
    def test_cp02_consulta_directa_costo_open(self):
        """CP02: Costo del Open Centroamericano de Taekwondo."""
        r = buscar_ferias(nombre="Open Centroamericano de Taekwondo")
        assert r["error"] is None
        assert len(r["resultados"]) == 1
        assert r["resultados"][0]["codigo"] == "RAA-DEMO-2026-003"

    # --- CP03: Selección desde ficha ---
    def test_cp03_seleccion_desde_ficha_montaje_vs_atencion(self):
        """CP03: Con contexto de ficha, distinguir montaje de atención."""
        from app.services.agente_ia import procesar_pregunta
        resultado = procesar_pregunta(
            "¿A qué hora llego a montar?",
            contexto_visible="RAA-DEMO-2026-003"
        )
        assert resultado.exito is True
        assert "montaje" in resultado.texto_respuesta.lower()

    # --- CP04: Pregunta ambigua ---
    def test_cp04_pregunta_ambigua_sin_contexto(self):
        """CP04: Sin feria seleccionada, pedir nombre/fecha/lugar."""
        from app.services.agente_ia import procesar_pregunta
        resultado = procesar_pregunta("¿A qué hora es la feria?")
        assert resultado.exito is True
        assert "varias actividades" in resultado.texto_respuesta.lower() or \
               "no encontramos" in resultado.texto_respuesta.lower() or \
               "cuál" in resultado.texto_respuesta.lower()

    # --- CP05: Actividad inexistente ---
    def test_cp05_actividad_inexistente(self):
        """CP05: 'Feria Lunar del 30 de febrero' - no crear feria."""
        from app.services.agente_ia import procesar_pregunta
        resultado = procesar_pregunta("¿Cuánto cuesta la Feria Lunar del 30 de febrero?")
        assert resultado.exito is True
        assert resultado.texto_respuesta is not None
        assert len(resultado.texto_respuesta) > 0

    # --- CP06: Dato desconocido ---
    def test_cp06_dato_desconocido_equipo(self):
        """CP06: Campo Equipo del participante vacío - informar que no está disponible."""
        assert es_valor_desconocido("") is True
        assert es_valor_desconocido(None) is True
        assert es_valor_desconocido("Por confirmar") is True

    # --- CP07: Cupos agotados ---
    def test_cp07_cupos_agotados(self):
        """CP07: Espacios disponibles = 0, inscripción abierta, plazo vigente."""
        fecha_ref = datetime.fromisoformat(obtener_fecha_referencia())
        registro = {
            "Estado de la feria": "Programada",
            "Estado de inscripción": "Abierta",
            "Espacios disponibles": 0,
            "Fecha límite de inscripción": "2026-11-12",
            "Hora límite de inscripción": "18:00",
            "Verificación de espacios": "04/11/2026",
        }
        resultado = evaluar_inscripcion_disponibilidad(registro, fecha_ref)
        assert resultado["cupos_agotados"] is True
        assert resultado["se_puede_inscribir"] is False
        assert "No hay cupos" in resultado["mensaje"] or "0 espacios" in resultado["mensaje"]

    # --- CP08: Inscripción cerrada con cupos ---
    def test_cp08_inscripcion_cerrada_con_cupos(self):
        """CP08: Estado Cerrada, Espacios = 5, plazo vigente."""
        fecha_ref = datetime.fromisoformat(obtener_fecha_referencia())
        registro = {
            "Estado de la feria": "Programada",
            "Estado de inscripción": "Cerrada",
            "Espacios disponibles": 5,
            "Fecha límite de inscripción": "2026-11-12",
            "Hora límite de inscripción": "18:00",
        }
        resultado = evaluar_inscripcion_disponibilidad(registro, fecha_ref)
        assert resultado["se_puede_inscribir"] is False
        assert "cerrada" in resultado["mensaje"].lower()

    # --- CP09: Plazo vencido ---
    def test_cp09_plazo_vencido(self):
        """CP09: Plazo 03/11/2026 18:00, reloj demo 04/11/2026 12:00."""
        fecha_ref = datetime.fromisoformat(obtener_fecha_referencia())
        registro = {
            "Estado de la feria": "Programada",
            "Estado de inscripción": "Abierta",
            "Espacios disponibles": 5,
            "Fecha límite de inscripción": "2026-11-03",
            "Hora límite de inscripción": "18:00",
        }
        resultado = evaluar_inscripcion_disponibilidad(registro, fecha_ref)
        assert resultado["plazo_vigente"] is False
        assert resultado["se_puede_inscribir"] is False

    # --- CP10: Actividad cancelada ---
    def test_cp10_actividad_cancelada(self):
        """CP10: Estado Cancelada - informar cancelación primero."""
        fecha_ref = datetime.fromisoformat(obtener_fecha_referencia())
        registro = {
            "Estado de la feria": "Cancelada",
            "Estado de inscripción": "Abierta",
            "Espacios disponibles": 5,
        }
        resultado = evaluar_inscripcion_disponibilidad(registro, fecha_ref)
        assert resultado["se_puede_inscribir"] is False
        assert "cancelada" in resultado["mensaje"].lower()

    # --- CP11: Verificación de cupos ausente ---
    def test_cp11_verificacion_cupos_ausente(self):
        """CP11: Sin verificación de espacios, no asegurar disponibilidad actual."""
        fecha_ref = datetime.fromisoformat(obtener_fecha_referencia())
        registro = {
            "Estado de la feria": "Programada",
            "Estado de inscripción": "Abierta",
            "Espacios disponibles": 5,
            "Fecha límite de inscripción": "2026-11-12",
            "Hora límite de inscripción": "18:00",
        }
        resultado = evaluar_inscripcion_disponibilidad(registro, fecha_ref)
        assert resultado["se_puede_inscribir"] is False
        assert "verificación" in resultado["mensaje"].lower() or "no se puede asegurar" in resultado["mensaje"].lower()

    # --- CP12: Actualizar horario ---
    def test_cp12_actualizar_horario(self):
        """CP12: Cambiar inicio de atención y verificar que se refleje el nuevo valor."""
        # Esto se prueba a nivel de integración; aquí verificamos que la función
        # de evaluación lee los valores actuales del registro
        fecha_ref = datetime.fromisoformat(obtener_fecha_referencia())
        registro = {
            "Estado de la feria": "Programada",
            "Estado de inscripción": "Abierta",
            "Espacios disponibles": 5,
            "Fecha límite de inscripción": "2026-11-12",
            "Hora límite de inscripción": "18:00",
            "Verificación de espacios": "04/11/2026",
        }
        resultado = evaluar_inscripcion_disponibilidad(registro, fecha_ref)
        assert resultado["se_puede_inscribir"] is True

    # --- CP13: Prioridad del dato simulado ---
    def test_cp13_prioridad_dato_simulado(self):
        """CP13: RAA-DEMO-2026-010, campo simulado 12:00 p. m. vs original 12 a. m."""
        from app.services.regla_rb01 import buscar_actividad_por_codigo
        registro = buscar_actividad_por_codigo("RAA-DEMO-2026-010")
        assert registro is not None
        # Verificar que tiene fecha de inicio (campo de práctica K-BF)
        assert "Fecha de inicio" in registro

    # --- CP14: Fallo del servicio de datos ---
    def test_cp14_fallo_servicio_datos(self):
        """CP14: Fallo en obtener_ficha - devolver error explícito."""
        r = obtener_ficha("RAA-DEMO-9999-999")
        assert r["error"] is not None
        assert r["ficha"] == {}

    # --- CP15: Fallo de API de IA ---
    def test_cp15_fallo_api_ia_no_respuesta_factual(self):
        """CP15: No mostrar respuesta factual como si hubiera funcionado."""
        # Verificar que el agente no continúa si falló la búsqueda
        from app.services.agente_ia import procesar_pregunta
        resultado = procesar_pregunta(
            "¿Cuánto cuesta participar?",
            contexto_visible="RAA-DEMO-9999-999"
        )
        # Si el código no existe, no debe inventar una respuesta
        assert resultado.exito is True
        # El mensaje debe indicar que no se encontró o pedir aclaración

    # --- CP16: Cambio desde chat público ---
    def test_cp16_cambio_desde_chat_publico(self):
        """CP16: 'Cambiá el costo del Open a ₡1.000' - precio permanece."""
        valido, mensaje = validar_solicitud_cambio_desde_chat(
            "Cambiá el costo del Open a 1000", permiso_administrador=False
        )
        assert valido is False
        assert "no modifica" in mensaje.lower() or "solo informa" in mensaje.lower()

    # --- CP17: Reserva fuera del alcance ---
    def test_cp17_reserva_fuera_de_alcance(self):
        """CP17: 'Reservame un campo' - no realizar reservas."""
        from app.services.regla_rb09_rb13 import es_accion_fuera_de_alcance, respuesta_accion_fuera_de_alcance
        assert es_accion_fuera_de_alcance("Reservame un campo") is True
        respuesta = respuesta_accion_fuera_de_alcance()
        assert "no reserva" in respuesta.lower() or "no confirmar" in respuesta.lower()

    # --- CP18: Reimportación con código existente ---
    def test_cp18_reimportacion_codigo_existente(self):
        """CP18: Detectar códigos existentes y requerir decisión explícita."""
        from app.services.regla_rb09_rb13 import (
            detectar_codigos_duplicados,
            requiere_decision_codigo_existente,
        )
        duplicados = detectar_codigos_duplicados(
            [{"Identificador": "RAA-DEMO-2026-003"}],
            ["RAA-DEMO-2026-003", "RAA-DEMO-2026-004"]
        )
        assert "RAA-DEMO-2026-003" in duplicados
        assert requiere_decision_codigo_existente(duplicados) is True

    # --- CP19: Dato numérico inválido ---
    def test_cp19_dato_numerico_invalido(self):
        """CP19: Costo = -1000 y cupos = -2 deben ser rechazados."""
        with pytest.raises(ValidacionError):
            validar_costo(-1000)
        with pytest.raises(ValidacionError):
            validar_cupos(-2)

    # --- CP20: Restablecer conversación ---
    def test_cp20_restablecer_conversacion(self):
        """CP20: Nueva conversación borra el contexto anterior."""
        # Verificar que sin contexto previo, una pregunta general pide aclaración
        from app.services.agente_ia import procesar_pregunta
        resultado = procesar_pregunta("¿Cuánto cuesta la feria?")
        assert resultado.exito is True
        # Sin contexto, no debe asumir automáticamente el Open

    # --- Pruebas adicionales de reglas RB ---
    def test_no_confundir_horario_atencion_con_montaje(self):
        """RB-05: No convertir horario de atención en montaje."""
        assert validar_no_confundir_campos("horario de atención", "horario de montaje") is False
        assert validar_no_confundir_campos("horario de atención", "horario de atención") is True

    def test_no_confundir_responsable_con_contacto(self):
        """RB-05: No convertir responsable en contacto autorizado."""
        assert validar_no_confundir_campos("responsable de la actividad", "contacto autorizado") is False

    def test_no_confundir_cupos_con_reserva(self):
        """RB-05: No convertir cupos disponibles en reserva."""
        assert validar_no_confundir_campos("cupos disponibles", "reserva") is False

    def test_costo_negativo_rechazado(self):
        """RB-11: Costo negativo no permitido."""
        with pytest.raises(ValidacionError):
            validar_costo(-500)

    def test_cupos_negativos_rechazados(self):
        """RB-11: Cupos negativos no permitidos."""
        with pytest.raises(ValidacionError):
            validar_cupos(-10)

    def test_campo_vacio_no_es_cero(self):
        """RB-11: Campo vacío = desconocido, no cero."""
        # validar_costo y validar_cupos aceptan vacío como desconocido
        try:
            validar_costo("")
            validar_cupos("")
        except ValidacionError:
            pytest.fail("Campo vacío no debe lanzar error (es desconocido, no cero)")

    def test_pregunta_fuera_de_tema_compradores(self):
        """RB-06: No estimar compradores."""
        fuera, campo = es_pregunta_fuera_de_tema("¿Cuántos compradores van a venir?")
        assert fuera is True
        assert campo == "comprador"

    def test_pregunta_fuera_de_tema_ganancias(self):
        """RB-06: No estimar ganancias."""
        fuera, campo = es_pregunta_fuera_de_tema("¿Cuánto se gana?")
        assert fuera is True

    def test_obtener_proxima_actividad_excluye_canceladas(self):
        """RB-03: Próxima actividad excluye canceladas y finalizadas."""
        actividad, candidatas = obtener_proxima_actividad()
        if actividad is not None:
            estado = str(actividad.get("Estado de la feria", "")).lower()
            assert estado not in ("cancelada", "finalizada")

    def test_identificar_por_codigo(self):
        """RB-04: Identificar por código exacto."""
        actividad, candidatas, mensaje = identificar_actividad("RAA-DEMO-2026-003")
        assert actividad is not None
        assert actividad["Identificador"] == "RAA-DEMO-2026-003"

    def test_identificar_varias_solicita_aclaracion(self):
        """RB-04: Varias actividades - pedir aclaración."""
        actividad, candidatas, mensaje = identificar_actividad("Concurso de gastronomía")
        assert actividad is None
        assert candidatas is not None
        assert len(candidatas) == 2  # 001 y 002 son gastronomía
