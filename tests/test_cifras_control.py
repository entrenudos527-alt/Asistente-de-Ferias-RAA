"""
Pruebas contra las cifras de control definidas en AGENTS.md.

Cifras de control:
- Número de registros de actividades: 11
- Códigos de actividades: RAA-DEMO-2026-001 a RAA-DEMO-2026-011
- Columnas del Excel de actividades: 58 (A a BF)
- Fecha fija de demostración: 04/11/2026 12:00 p. m. America/Costa_Rica
- Marcas de verificación/actualización interpretadas como UTC: 04/11/2026 18:00 UTC
"""

import pytest
from app.services.lectura_datos import leer_actividades, obtener_actividad_por_codigo
from app.services.regla_rb01 import buscar_actividad_por_codigo, validar_codigo_existe
from app.services.regla_rb02 import (
    obtener_fecha_referencia,
    interpretar_marca_utc_como_costa_rica,
)


class TestCifrasControl:
    """Pruebas para verificar las cifras de control de AGENTS.md."""

    def test_numero_registros_actividades(self):
        """Deben existir exactamente 11 registros de actividades."""
        datos = leer_actividades()
        assert datos["total_registros"] == 11, (
            f"Esperado: 11 registros, Obtenido: {datos['total_registros']}"
        )

    def test_codigos_actividades_rango(self):
        """Los códigos deben ser RAA-DEMO-2026-001 a RAA-DEMO-2026-011."""
        datos = leer_actividades()
        codigos_esperados = [f"RAA-DEMO-2026-{i:03d}" for i in range(1, 12)]
        assert datos["codigos"] == codigos_esperados, (
            f"Esperado: {codigos_esperados}, Obtenido: {datos['codigos']}"
        )

    def test_numero_columnas_excel(self):
        """El Excel debe tener 58 columnas (A a BF)."""
        datos = leer_actividades()
        assert datos["total_columnas"] == 58, (
            f"Esperado: 58 columnas, Obtenido: {datos['total_columnas']}"
        )

    def test_encabezado_columna_k_es_identificador(self):
        """La columna K (índice 10) debe ser 'Identificador'."""
        datos = leer_actividades()
        assert datos["encabezados"][10] == "Identificador", (
            f"Esperado: 'Identificador', Obtenido: '{datos['encabezados'][10]}'"
        )

    def test_encabezado_columna_bf_es_cierre_atencion_simulado(self):
        """La columna BF (última, índice 57) debe ser 'Cierre de atención simulado'."""
        datos = leer_actividades()
        assert datos["encabezados"][-1] == "Cierre de atención simulado", (
            f"Esperado: 'Cierre de atención simulado', Obtenido: '{datos['encabezados'][-1]}'"
        )

    def test_obtener_actividad_por_codigo_valido(self):
        """Debe obtenerse la actividad RAA-DEMO-2026-003 correctamente."""
        registro = obtener_actividad_por_codigo("RAA-DEMO-2026-003")
        assert registro is not None, "No se encontró RAA-DEMO-2026-003"
        assert registro["Identificador"] == "RAA-DEMO-2026-003"
        assert registro["Actividad"] == "Open Centroamericano de Taekwondo"

    def test_obtener_actividad_codigo_inexistente(self):
        """Debe devolver None para un código que no existe."""
        registro = obtener_actividad_por_codigo("RAA-DEMO-9999-999")
        assert registro is None, (
            f"Esperado: None, Obtenido: {registro}"
        )

    def test_validar_codigo_existe(self):
        """validar_codigo_existe debe retornar True para códigos válidos y False para inválidos."""
        from app.services.regla_rb01 import validar_codigo_existe
        assert validar_codigo_existe("RAA-DEMO-2026-001") is True
        assert validar_codigo_existe("RAA-DEMO-2026-011") is True
        assert validar_codigo_existe("RAA-DEMO-9999-999") is False

    def test_fecha_referencia_demostracion(self):
        """La fecha fija de demostración debe ser 04/11/2026 12:00 p. m. Costa Rica."""
        fecha = obtener_fecha_referencia()
        assert fecha == "2026-11-04T12:00:00", (
            f"Esperado: '2026-11-04T12:00:00', Obtenido: '{fecha}'"
        )

    def test_marca_utc_interpretada_como_costa_rica(self):
        """La marca UTC 04/11/2026 18:00 debe interpretarse como 12:00 p. m. Costa Rica."""
        resultado = interpretar_marca_utc_como_costa_rica("2026-11-04T18:00:00")
        assert "12:00" in resultado, (
            f"Esperado que contenga '12:00', Obtenido: '{resultado}'"
        )

    def test_actividad_003_tiene_datos_esperados(self):
        """RAA-DEMO-2026-003 (Open Taekwondo) debe tener los datos de prueba esperados."""
        registro = obtener_actividad_por_codigo("RAA-DEMO-2026-003")
        assert registro is not None
        assert "Liceo de Alajuelita" in str(registro.get("Lugar", ""))
        assert "2026-11-15" in str(registro.get("Fecha de inicio", ""))

    def test_registros_tienen_identificador_unico(self):
        """Cada registro debe tener un identificador único en la columna K."""
        datos = leer_actividades()
        codigos = [r.get("Identificador") for r in datos["registros"]]
        assert len(codigos) == len(set(codigos)), "Hay códigos duplicados"
        assert all(c is not None for c in codigos), "Hay códigos nulos"
