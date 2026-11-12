# PLAN.md — Asistente de Ferias RAA

## 1. RESUMEN

Construimos una aplicación web de demostración para la Red Alajuelita Artesanal (RAA) que permite consultar información oficial y actualizada de ferias artesanales mediante una lista de ferias y un chat informativo. Entra como datos el Excel `Actividades_Artesanos_Festival_2026.xlsx` con 11 registros y 58 columnas, más los archivos de preguntas y casos de prueba. El agente de IA interpreta la pregunta, identifica la actividad, recupera los datos del registro vigente y redacta una respuesta breve respaldada, sin inventar información ni confirmar inscripciones. Salen como resultado un listado de ferias, fichas de detalle por registro, un chat con respuestas basadas en registros y pantallas de administración para crear, editar e importar fichas.

---

## 2. LO QUE ENCONTRÉ

### En la carpeta `Contexto`
- `Contexto_Mi_App.md` (extraído de los 3 documentos): define el problema, la solución, usuarios, agentes, reglas de negocio, fecha fija de demostración (04/11/2026 12:00 p. m. Costa Rica), insumos necesarios, prueba inicial y criterios de evaluación.

### En la carpeta `Insumos`
| Archivo | Hoja / Tipo | Filas de datos | Contenido clave |
|---------|-------------|----------------|-----------------|
| `Actividades_Artesanos_Festival_2026.xlsx` | Hoja `Exposición de artesanos` | 11 registros (filas 6-16) | 58 columnas A-BF; códigos RAA-DEMO-2026-001 a 011; A-J cronograma original, K-BF campos de práctica simulados |
| `Preguntas_y_Respuestas_Prueba_RAA.xlsx` | Hoja `Preguntas y respuestas` | 20 pruebas (P01-P20) | Preguntas y respuestas esperadas, campos utilizados, criterios de aprobación |
| `Casos_de_Prueba_y_Resultados_Esperados_RAA.xlsx` | Hoja `Casos de prueba` | 20 casos (CP01-CP20) | Escenarios de carga inicial, consulta directa, ambigua, actividad inexistente, dato desconocido, cupos agotados, inscripción cerrada, plazo vencido, cancelada, verificación ausente, actualizar horario, prioridad simulada, fallos, cambio desde chat, reserva fuera de alcance, reimportación, dato inválido, restablecer conversación |
| `Ficha_de_Feria_RAA.docx` | Word, 0 tablas | Plantilla de ficha | 8 secciones que definen los campos de cada feria |

### Coincidencia con `AGENTS.md`
- **Coincide completamente:** los 11 registros, los códigos RAA-DEMO-2026-001 a 011, las 58 columnas (A-J originales, K-BF simuladas), la fecha fija de demostración, las cifras de control (11 registros, 20 pruebas P, 20 casos CP), los 20 casos límite y todas las reglas RB-01 a RB-13 están reflejadas en `AGENTS.md`.
- **No hay faltantes ni contradicciones:** todo lo que menciona el contexto tiene su insumo correspondiente, y todo lo que está en los insumos está contemplado en `AGENTS.md`.

---

## 3. ENTREGAS POR SUBAGENTE

Orden de ejecución: backend → frontend → tester → revisor.

### Bloque 1: Estructura base y lectura de datos (@backend)

| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 1 | @backend | Proyecto Flask con `uv`, estructura MVC vacía, `app/__init__.py` con `create_app()`, `wsgi.py`, `.env.example`, `iniciar_app.bat` | `app/__init__.py`, `wsgi.py`, `.env.example`, `iniciar_app.bat`, `pyproject.toml` (uv) | Ninguno (primera entrega) | Ejecutar `iniciar_app.bat`, el navegador se abre y muestra una página en blanco o un mensaje de "app en marcha" sin errores de servidor |
| 2 | @backend | Lectura del Excel de actividades: función que lee hoja `Exposición de artesanos`, encabezados fila 5, 11 registros filas 6-16, columnas A-J y K-BF | `app/services/lectura_datos.py` (nueva) | Entrega 1 (proyecto Flask funcionando) | Ejecutar un script o endpoint que imprima en consola: "11 registros leídos, códigos RAA-DEMO-2026-001 a 011, 58 columnas" |

### Bloque 2: Reglas de negocio una por una (@backend)

| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 3 | @backend | Regla RB-01: búsqueda por encabezado y código, prioridad K-BF sobre A-J cuando existe valor específico | `app/services/regla_rb01.py` (nueva) | Entrega 2 (datos leídos) | Consultar un código (ej. RAA-DEMO-2026-003) y ver que devuelve el identificador correcto de la columna K |
| 4 | @backend | Regla RB-02: fecha fija de demostración 04/11/2026 12:00 p. m. Costa Rica, marcas UTC interpretadas como 12:00 p. m. CR | `app/services/regla_rb02.py` (nueva) | Entrega 3 | Mostrar en pantalla "Fecha de demostración: 04/11/2026 12:00 p. m. America/Costa_Rica" |
| 5 | @backend | Reglas RB-03 y RB-04: próxima actividad (fecha ≥ referencia, excluir canceladas/finalizadas) e identificar actividad por código/nombre/fecha/lugar, pedir aclaración si hay varias | `app/services/regla_rb03_rb04.py` (nueva) | Entrega 4 | Buscar "próxima actividad" y ver que aparece el Concurso de gastronomía del 14/11/2026; buscar sin contexto y ver que pide aclaración |
| 6 | @backend | Reglas RB-05 y RB-06: redactar respuesta con respaldo, indicar código + última actualización, manejar campos vacíos/"Por confirmar"/"No indicado" como desconocidos, distinguir 0 de vacío | `app/services/regla_rb05_rb06.py` (nueva) | Entrega 5 | Ver respuesta sobre un registro con aviso "Demostración con datos simulados", código visible y última actualización |
| 7 | @backend | Reglas RB-07 y RB-08: inscripción y disponibilidad (cancelada, finalizada, cerrada, 0 cupos, plazo vencido, abierto con cupos); actualizaciones solo por administración | `app/services/regla_rb07_rb08.py` (nueva) | Entrega 6 | Consultar un registro con estado "Cerrada" y ver que se informa la inscripción cerrada aunque haya cupos positivos |
| 8 | @backend | Reglas RB-09, RB-10, RB-11, RB-12, RB-13: consulta mediante herramientas, enlaces .example ficticios, validación de datos (no negativos, no convertir vacío en cero), importación con decisión explícita por código existente, cobertura de pantallas | `app/services/regla_rb09_rb13.py` (nueva) | Entrega 7 | Probar importación con código duplicado y ver que se solicita decisión explícita antes de reemplazar |

### Bloque 3: Agente de IA y herramientas JSON (@backend)

| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 9 | @backend | Contrato JSON de herramientas: `buscar_ferias`, `obtener_ficha`, `listar_proximas_ferias` (solo lectura); `guardar_ficha`, `importar_ferias`, `registrar_consulta_no_resuelta` (solo administración) | `app/services/herramientas_ia.py` (nueva) | Entrega 8 (todas las reglas RB implementadas) | Llamar a `buscar_ferias` con filtro por nombre y ver que devuelve JSON con resultados y sin error |
| 10 | @backend | Integración del agente de IA con llave leída de `.env` (nunca hardcodeada); flujo consulta → búsqueda → respuesta; no continuar si falla la búsqueda | `app/services/agente_ia.py`, `.env` (local, no se sube) | Entrega 9 | Enviar una pregunta en el chat y ver una respuesta basada en el registro, con referencia visible al código de la actividad |

### Bloque 4: Pantallas (@frontend)

| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 11 | @frontend | `base.html` con CSS embebido, fondo oscuro, aviso permanente "Demostración con datos simulados", estructura común | `app/templates/base.html` (nueva) | Entrega 10 (backend con agente de IA) | Abrir cualquier pantalla y ver fondo oscuro + aviso de simulación permanente |
| 12 | @frontend | Pantalla de inicio y listado: 11 tarjetas con nombre, fecha, lugar, horario de atención, estado de actividad, estado de inscripción; filtros por nombre/código, fecha, lugar; botones Ver detalles y Consultar al asistente | `app/templates/inicio.html` (nueva) | Entrega 11 | Ver 11 tarjetas, ordenadas por fecha; filtrar por "Open" y ver solo el Open Centroamericano de Taekwondo |
| 13 | @frontend | Pantalla de detalle por registro: bloques de información general, fechas y horarios (atención, montaje, desmontaje separados), ubicación, costos con moneda y unidad, requisitos, equipo, inscripción y cupos con fecha de verificación, contacto y actualización; botón Consultar sobre esta feria | `app/templates/detalle.html` (nueva) | Entrega 12 | Abrir el detalle de RAA-DEMO-2026-003 y ver costo ₡4.000 por puesto y jornada, montaje 7:30 a. m., atención 8:30 a. m. a 4:00 p. m. |
| 14 | @frontend | Pantalla de resultados/chat: historial de sesión, campo de pregunta, botón Enviar, botón Nueva conversación, preguntas sugeridas, referencia visible al registro (código + última actualización), fecha de verificación de cupos cuando corresponda | `app/templates/resultados.html` (nueva) | Entrega 13 | Enviar "¿Cuánto cuesta participar en el Open?" y ver respuesta con costo, código RAA-DEMO-2026-003 y última actualización |

### Bloque 5: Pruebas (@tester)

| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 15 | @tester | Pruebas pytest en `tests/` contra cifras de control (11 registros, códigos RAA-DEMO-2026-001 a 011, 20 pruebas P, 20 casos CP) y casos límite CP01-CP20 | `tests/test_cifras_control.py`, `tests/test_casos_limite.py` (nuevas), configuración `pythonpath` | Entrega 14 (app completa con frontend y backend) | Ejecutar `pytest` y ver que todas las pruebas pasan o reportar diferencias con causa probable |
| 16 | @tester | Archivo `VALIDACION.md` con esperado vs obtenido por cada cifra de control y cada caso límite | `VALIDACION.md` (nuevo) | Entrega 15 | Leer `VALIDACION.md` y confirmar que cada fila tiene columna "Esperado", "Obtenido" y "Causa probable" si hay diferencia |

### Bloque 6: Revisión (@revisor)

| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 17 | @revisor | Lista de hallazgos de seguridad (llaves expuestas, `.env` en código, datos sensibles, archivos que no deben subirse a GitHub) y de reglas no contempladas en `AGENTS.md` | Ninguno (solo lee) | Entrega 16 (VALIDACION.md y app completa) | Leer el reporte del revisor y verificar cada hallazgo en pantalla según ubicación indicada |

---

## 4. PUNTOS DE CONTROL

| Después de la entrega | Quién interviene | Qué debe verse en pantalla exactamente |
|----------------------|------------------|----------------------------------------|
| 1 | @tester (opcional, humo) | `iniciar_app.bat` abre el navegador y la app responde sin error 500 |
| 2 | @tester | Mensaje en consola o pantalla: "11 registros leídos, códigos RAA-DEMO-2026-001 a 011, 58 columnas" |
| 9 | @tester | JSON válido de `buscar_ferias` con campo `resultados` y `error: null` |
| 10 | @tester | Respuesta del chat con referencia visible al código de la actividad y aviso "Demostración con datos simulados" |
| 12 | @tester | 11 tarjetas en el listado; al filtrar por "Open" aparece exactamente 1 tarjeta: Open Centroamericano de Taekwondo |
| 13 | @tester | Detalle de RAA-DEMO-2026-003 muestra: costo ₡4.000 por puesto y jornada, montaje 7:30 a. m., atención 8:30 a. m. a 4:00 p. m. |
| 14 | @tester | Respuesta al chat incluye código RAA-DEMO-2026-003 y última actualización visible |
| 15 | @tester | `pytest` ejecuta pruebas de cifras de control y casos límite; cada prueba muestra PASSED o FAILED con causa probable |
| 16 | @revisor | `VALIDACION.md` tiene filas con columnas: Esperado | Obtenido | Causa probable (si aplica) |
| 17 | @revisor | Reporte de hallazgos ordenado por prioridad (alta/media/baja), cada uno con ubicación, descripción y corrección propuesta |

---

## 5. RIESGOS

| Riesgo | Qué hará cada subagente |
|--------|------------------------|
| **Datos incompletos en el Excel** (campos vacíos, "Por confirmar") | @backend implementa RB-06: responde solo lo conocido y explica qué dato falta. @tester verifica que no se inventen valores. @revisor revisa que no se rellene vacío con cero. |
| **Archivos escaneados (PDF sin texto)** | No aplica a este proyecto: todos los PDFs del contexto tienen texto extraíble. Si en el futuro apareciera uno escaneado, @backend preguntaría antes de asumir contenido. |
| **Respuestas del agente que no son JSON válido** | @backend implementa control de errores en las herramientas JSON; si falla, devuelve `error` explícito y no continúa con respuesta factual (regla del sistema 2). @tester valida que la salida sea JSON válido. |
| **Límites de la llave gratis de la API de IA** | @backend lee la llave de `.env` y nunca la hardcodea. @revisor verifica que no haya claves en el código. Si se agota la llave, el agente informa el fallo y permite reintentar (regla RB-09). |
| **Código existente en reimportación** | @backend implementa RB-12: detecta códigos duplicados y solicita decisión explícita antes de reemplazar. @tester prueba CP18. |
| **Confusión entre horario de atención y montaje** | @backend aplica RB-05: no convierte uno en el otro. @tester verifica CP03 (montaje 7:30 vs atención 8:30). |
| **Uso de fecha real del equipo en lugar de la fija de demostración** | @backend aplica RB-02: usa 04/11/2026 12:00 p. m. como referencia, no `datetime.now()`. @tester verifica CP09 (plazo vencido el 03/11/2026 respecto al reloj de demostración). |

---

## 6. PREGUNTAS PARA MÍ

Antes de que @backend comience a construir, necesito confirmar:

1. **Proveedor y modelo de IA:** ¿qué proveedor y modelo se usará para el agente de IA (la consigna del curso lo definirá, pero necesito saber si ya hay una preferencia para configurar `.env`)?
2. **¿Ya existe un archivo `.env` o debo crearlo solo como `.env.example`?** La llave de API se lee de `.env`, pero no sé si ya hay una llave proporcionada por el curso.
3. **¿Los tres roles del agente de IA (consulta, búsqueda, respuesta) se implementan como tres agentes separados o como roles coordinados en uno solo?** `AGENTS.md` dice que la consigna del curso lo decidirá.
4. **¿Hay alguna credencial de demostración ya definida para el panel de administración?** `AGENTS.md` dice que no se publique dentro de los insumos, pero necesito saber si hay alguna ya acordada.
5. **¿El tablero con contadores grandes que pide el frontend debe mostrarse en la pantalla de inicio o en una pantalla separada de administración?**

Quedo a la espera de su aprobación de la tabla de entregas antes de que cada subagente comience a trabajar.
