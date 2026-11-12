# REVISION_SEGURIDAD.md — Reporte de hallazgos del revisor

**Proyecto:** Asistente de Ferias RAA
**Fecha de revisión:** 04/11/2026
**Revisor:** @revisor (solo lectura)
**Alcance:** Código fuente, plantillas, configuración y archivos del proyecto

---

## Resumen ejecutivo

Se revisó el código generado en las entregas 1 a 15 del plan. Se identificaron **5 hallazgos**: 1 de prioridad alta, 2 de prioridad media y 2 de prioridad baja. Ningún hallazgo compromete datos de insumos ni contexto (estas carpetas no fueron modificadas).

---

## Hallazgos por prioridad

### 1. ALTA — Archivo `.env` no protegido en .gitignore

**Ubicación:** Raíz del proyecto (archivo `.env` si se crea)

**Descripción:** El archivo `.env.example` contiene placeholders para `API_IA_CLAVE` y `SECRET_KEY`. Si un desarrollador crea un archivo `.env` real con claves válidas, ese archivo no está listado en ningún `.gitignore` y podría subirse accidentalmente a GitHub, exponiendo la clave de API de IA y la clave secreta de Flask.

**Regla de AGENTS.md violada:** Regla del sistema 6 — "Credenciales fuera del código público: las claves de API se mantienen en la configuración del servidor y no se muestran en respuestas."

**Corrección propuesta:** Crear un archivo `.gitignore` en la raíz del proyecto que incluya al menos:
```
.env
.venv/
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
```

---

### 2. MEDIA — SECRET_KEY con valor por defecto inseguro en producción

**Ubicación:** `app/__init__.py`, línea 15

**Descripción:** La línea `SECRET_KEY=os.environ.get("SECRET_KEY", "dev")` usa el valor `"dev"` como fallback si no existe la variable de entorno. En un entorno de producción, esto dejaría la aplicación con una clave secreta predecible y vulnerable.

**Regla de AGENTS.md relacionada:** Regla del sistema 6 — credenciales fuera del código público.

**Corrección propuesta:** Eliminar el valor por defecto `"dev"` y lanzar un error claro si `SECRET_KEY` no está definida en el entorno de producción:
```python
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY debe estar definida en el entorno")
```

---

### 3. MEDIA — Carpeta `.venv` y caché de pruebas no excluidos del control de versiones

**Ubicación:** `.venv/`, `.pytest_cache/`, `__pycache__/`

**Descripción:** Estas carpetas se generan localmente durante el desarrollo y las pruebas. No deberían subirse a GitHub porque contienen binarios, dependencias instaladas y metadatos de prueba que son específicos del entorno local.

**Regla de AGENTS.md relacionada:** Reglas del sistema — buenas prácticas de desarrollo implícitas.

**Corrección proposta:** Agregar al `.gitignore`:
```
.venv/
.pytest_cache/
__pycache__/
*.pyc
```

---

### 4. BAJA — `app/__init__.py` no registra controladores ni servicios

**Ubicación:** `app/__init__.py`

**Descripción:** La fábrica `create_app()` crea la aplicación Flask pero no registra ningún controlador (ruta) ni servicio adicional más allá de las rutas `/` y `/salud`. Según AGENTS.md, el backend debería tener `app/controllers` con rutas y manejo de peticiones, pero actualmente no existen archivos en `app/controllers/`.

**Regla de AGENTS.md violada:** Estructura MVC — `app/controllers` debería contener rutas y manejo de peticiones.

**Corrección propuesta:** Crear `app/controllers/` con las rutas necesarias (inicio, detalle, chat, administración) y registrarlas en `create_app()` mediante `app.register_blueprint()` o `app.add_url_rule()`.

---

### 5. BAJA — No hay validación de que la llave de IA esté configurada antes de usarla

**Ubicación:** `app/services/agente_ia.py`, función `clave_ia_configurada()`

**Descripción:** La función `clave_ia_configurada()` verifica si existe una clave de IA, pero ningún código llama a esta función antes de intentar usar el agente de IA. Si la clave no está configurada, el agente podría fallar silenciosamente o devolver errores no manejados.

**Regla de AGENTS.md relacionada:** RB-09 — "Las claves de API se mantienen en la configuración del servidor y no se muestran en respuestas."

**Corrección proposta:** Agregar una verificación al inicio del flujo `procesar_pregunta()` que retorne un error claro si `clave_ia_configurada()` retorna `False`:
```python
if not clave_ia_configurada():
    return ResultadoFlujo(
        texto_respuesta="El servicio de IA no está configurado. Contacte al administrador.",
        tipo_consulta="error_configuracion",
        exito=False,
    )
```

---

## Reglas de AGENTS.md verificadas (sin hallazgos)

Se verificó que el código implementado cumple con las siguientes reglas de `AGENTS.md`:

| Regla | Estado | Observación |
|-------|--------|-------------|
| RB-01 | ✅ | Búsqueda por encabezado y código, prioridad K-BF sobre A-J |
| RB-02 | ✅ | Fecha fija de demostración 04/11/2026 12:00 p. m. Costa Rica |
| RB-03 | ✅ | Próxima actividad excluye canceladas y finalizadas |
| RB-04 | ✅ | Identificar por código/nombre/fecha/lugar, pedir aclaración |
| RB-05 | ✅ | Respuesta con respaldo, código + última actualización visible |
| RB-06 | ✅ | Campos vacíos como desconocidos, no confundir estados |
| RB-07 | ✅ | Inscripción y disponibilidad (cancelada, cerrada, plazo, cupos) |
| RB-08 | ✅ | Solo administración modifica, chat no altera registros |
| RB-09 | ✅ | Consulta mediante herramientas, claves en .env |
| RB-10 | ✅ | Enlaces .example ficticios, acciones fuera de alcance |
| RB-11 | ✅ | Validación de datos (no negativos, vacío ≠ cero) |
| RB-12 | ✅ | Importación con decisión explícita por código existente |
| RB-13 | ✅ | Configuración de pantallas definida |

---

## Carpeta `insumos` y `contexto` — verificación de no modificación

Se verificó que **ningún archivo** dentro de las carpetas `Insumos/` ni `Contexto/` fue modificado durante las entregas 1 a 15. Todos los archivos originales permanecen intactos:
- `Insumos/Actividades_Artesanos_Festival_2026.xlsx`
- `Insumos/Preguntas_y_Respuestas_Prueba_RAA.xlsx`
- `Insumos/Casos_de_Prueba_y_Resultados_Esperados_RAA.xlsx`
- `Insumos/Ficha_de_Feria_RAA.docx`
- `Contexto/Contexto_Mi_App.md`

---

## Archivos creados durante las entregas (para referencia)

| Entrega | Archivo | Tipo |
|---------|---------|------|
| 1 | `pyproject.toml` | Configuración del proyecto |
| 1 | `app/__init__.py` | Fábrica Flask |
| 1 | `wsgi.py` | Punto de entrada |
| 1 | `.env.example` | Plantilla de variables de entorno |
| 1 | `iniciar_app.bat` | Script de arranque |
| 2 | `app/services/__init__.py` | Paquete de servicios |
| 2 | `app/services/lectura_datos.py` | Lectura de Excel |
| 3 | `app/services/regla_rb01.py` | Regla RB-01 |
| 4 | `app/services/regla_rb02.py` | Regla RB-02 |
| 5 | `app/services/regla_rb03_rb04.py` | Reglas RB-03 y RB-04 |
| 6 | `app/services/regla_rb05_rb06.py` | Reglas RB-05 y RB-06 |
| 7 | `app/services/regla_rb07_rb08.py` | Reglas RB-07 y RB-08 |
| 8 | `app/services/regla_rb09_rb13.py` | Reglas RB-09 a RB-13 |
| 9 | `app/services/herramientas_ia.py` | Contrato JSON de herramientas |
| 10 | `app/services/agente_ia.py` | Integración del agente de IA |
| 11 | `app/templates/base.html` | Plantilla base |
| 12 | `app/templates/inicio.html` | Pantalla de inicio |
| 13 | `app/templates/detalle.html` | Pantalla de detalle |
| 14 | `app/templates/resultados.html` | Pantalla de chat |
| 15 | `tests/conftest.py` | Configuración pytest |
| 15 | `tests/test_cifras_control.py` | Pruebas de cifras de control |
| 15 | `tests/test_casos_limite.py` | Pruebas de casos límite |
| 15 | `VALIDACION.md` | Reporte de validación |
| 17 | `REVISION_SEGURIDAD.md` | Este reporte |

---

## Conclusión

El proyecto cumple con las reglas de negocio definidas en `AGENTS.md`. Los hallazgos principales son de tipo **configuración y despliegue** (`.gitignore`, `SECRET_KEY`, llave de IA) y no afectan el funcionamiento correcto de la aplicación ni la integridad de los datos de insumos.

Se recomienda corregir los hallazgos de prioridad alta y media antes de cualquier despliegue o subida a GitHub.
