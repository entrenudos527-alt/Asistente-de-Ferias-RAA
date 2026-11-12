# AGENTS.md — Asistente de Ferias RAA

## Qué es esta app

La **Asistente de Ferias RAA** es una aplicación web de demostración (prototipo académico) para la Red Alajuelita Artesanal (RAA). Permite que afiliados y personas interesadas consulten información oficial y actualizada sobre ferias artesanales mediante una lista de ferias y un chat, reduciendo las respuestas manuales repetidas que la organización debe dar por consultas similares.

La persona administradora designada por la RAA registra y actualiza los datos en un único lugar; los afiliados preguntan con sus propias palabras y reciben respuestas basadas en esos registros.

**Alcance de la primera versión:**
- Fichas de ferias, administración básica y chat informativo.
- Dejar para una etapa posterior: cobros, asignación de puestos, inscripciones automáticas e integración con WhatsApp.
- La disponibilidad de espacios solo se informará si existe un registro actualizado; la app no confirma cupos por su cuenta.
- No requiere una cuenta distinta para cada afiliado.
- Los enlaces y correos con dominio `.example` son ficticios; se muestran como texto identificado como ejemplo y no como canales reales ni botones operativos.

**Estado:** propuesta conceptual para llevar a clase. La programación, integraciones y decisiones técnicas quedan pendientes del avance y los requisitos del curso.

---

## Datos de entrada

### Archivos de la carpeta `insumos` (no se modifican)

#### 1. `Actividades_Artesanos_Festival_2026.xlsx`
Hoja: `Exposición de artesanos`. 16 filas × 58 columnas. Encabezados en **fila 5**; 11 registros en **filas 6 a 16**. Códigos `RAA-DEMO-2026-001` a `RAA-DEMO-2026-011`.

Columnas **A a J** (cronograma original) y **K a BF** (campos de práctica simulados):

| Col. | Letra | Campo | Origen |
|------|-------|-------|--------|
| 1 | A | Fecha | A–J (original) |
| 2 | B | Día | A–J (original) |
| 3 | C | Actividad | A–J (original) |
| 4 | D | Lugar | A–J (original) |
| 5 | E | Horario según cronograma | A–J (original) |
| 6 | F | Responsable de la actividad | A–J (original) |
| 7 | G | Participación indicada | A–J (original) |
| 8 | H | Observaciones y pendientes | A–J (original) |
| 9 | I | Referencia en archivo | A–J (original) |
| 10 | J | Fuente registrada | A–J (original) |
| 11 | K | Identificador | K–BF (práctica) |
| 12 | L | Organiza | K–BF (práctica) |
| 13 | M | Fecha de inicio | K–BF (práctica) |
| 14 | N | Fecha de finalización | K–BF (práctica) |
| 15 | O | Días de participación | K–BF (práctica) |
| 16 | P | Dirección exacta de práctica | K–BF (práctica) |
| 17 | Q | Enlace de ubicación de práctica | K–BF (práctica) |
| 18 | R | Ingreso y montaje | K–BF (práctica) |
| 19 | S | Salida y desmontaje | K–BF (práctica) |
| 20 | T | Acceso y parqueo | K–BF (práctica) |
| 21 | U | Costo de participación | K–BF (práctica) |
| 22 | V | Moneda | K–BF (práctica) |
| 23 | W | Unidad de cobro | K–BF (práctica) |
| 24 | X | Incluye el costo | K–BF (práctica) |
| 25 | Y | Forma de pago | K–BF (práctica) |
| 26 | Z | Fecha límite de pago | K–BF (práctica) |
| 27 | AA | Requisitos | K–BF (práctica) |
| 28 | AB | Productos permitidos y restricciones | K–BF (práctica) |
| 29 | AC | Equipo del participante | K–BF (práctica) |
| 30 | AD | Equipo y servicios de organización | K–BF (práctica) |
| 31 | AE | Condiciones especiales | K–BF (práctica) |
| 32 | AF | Quiénes pueden inscribirse | K–BF (práctica) |
| 33 | AG | Fecha límite de inscripción | K–BF (práctica) |
| 34 | AH | Hora límite de inscripción | K–BF (práctica) |
| 35 | AI | Procedimiento de inscripción | K–BF (práctica) |
| 36 | AJ | Canal de inscripción de práctica | K–BF (práctica) |
| 37 | AK | Documentos requeridos | K–BF (práctica) |
| 38 | AL | Confirmación de participación | K–BF (práctica) |
| 39 | AM | Estado de inscripción | K–BF (práctica) |
| 40 | AN | Espacios disponibles | K–BF (práctica) |
| 41 | AO | Verificación de espacios | K–BF (práctica) |
| 42 | AP | Lista de espera | K–BF (práctica) |
| 43 | AQ | Contacto autorizado de práctica | K–BF (práctica) |
| 44 | AR | Cargo del contacto | K–BF (práctica) |
| 45 | AS | Teléfono o WhatsApp de práctica | K–BF (práctica) |
| 46 | AT | Correo de práctica | K–BF (práctica) |
| 47 | AU | Horario del contacto | K–BF (práctica) |
| 48 | AV | Fuente oficial de práctica | K–BF (práctica) |
| 49 | AW | Responsable de actualización | K–BF (práctica) |
| 50 | AX | Última actualización | K–BF (práctica) |
| 51 | AY | Estado de la feria | K–BF (práctica) |
| 52 | AZ | Cambios y avisos de práctica | K–BF (práctica) |
| 53 | BA | Información pendiente | K–BF (práctica) |
| 54 | BB | Regla para el asistente | K–BF (práctica) |
| 55 | BC | Naturaleza de los datos | K–BF (práctica) |
| 56 | BD | Campos simulados | K–BF (práctica) |
| 57 | BE | Inicio de atención simulado | K–BF (práctica) |
| 58 | BF | Cierre de atención simulado | K–BF (práctica) |

**Convención de fechas:** Las marcas de verificación y actualización del Excel del `04/11/2026 18:00` se interpretan como **UTC** (equivalentes a las 12:00 p. m. de Costa Rica). Las fechas de eventos se interpretan como fechas locales y las horas de atención como horas locales.

#### 2. `Preguntas_y_Respuestas_Prueba_RAA.xlsx`
Hoja: `Preguntas y respuestas`. 26 filas × 10 columnas. Encabezados en **fila 6**; 20 pruebas (P01 a P20) en **filas 7 a 26**.

Columnas: ID de prueba, Tema, ID de feria o contexto, Pregunta de la persona usuaria, Respuesta esperada, Campos utilizados, Criterio de aprobación, Resultado de la prueba, Respuesta obtenida, Observaciones.

**Material de evaluación:** no se usará como sustituto de la consulta de registros. Las respuestas esperadas son criterios de contenido, no textos obligatorios.

#### 3. `Casos_de_Prueba_y_Resultados_Esperados_RAA.xlsx`
Hoja: `Casos de prueba`. 27 filas × 10 columnas. Encabezados en **fila 7**; 20 casos (CP01 a CP20) en **filas 8 a 27**.

Columnas: ID, Situación, Preparación del escenario, Pasos para ejecutar, Pregunta o dato de entrada, Resultado esperado, Criterio de aprobación, Evaluación, Resultado obtenido, Observaciones o evidencia.

**Escenarios especiales preparados en este insumo:** cancelación, cupos agotados, inscripción cerrada, errores de servicio. Todos los casos están pendientes; se registra resultado real y evaluación tras programar. Los cambios indicados son preparaciones de prueba; no se han aplicado al Excel de actividades.

#### 4. `Ficha_de_Feria_RAA.docx`
Plantilla para completar una ficha por feria. 56 párrafos, 0 tablas. Define los campos de la ficha en 8 secciones:
1. Identificación y fechas (nombre, identificador, organiza, fecha de inicio y finalización, días de participación)
2. Ubicación y horarios (lugar y dirección exacta, referencia/enlace de ubicación, horario de atención al público, horario de ingreso y montaje, horario de salida y desmontaje, indicaciones de acceso)
3. Costo de participación (monto y moneda, qué incluye, forma y fecha límite de pago)
4. Requisitos y equipo (requisitos, productos permitidos y restricciones, equipo que aporta cada participante, equipo o servicios de la organización, condiciones especiales)
5. Inscripción y disponibilidad (quiénes pueden inscribirse, fecha y hora límite, procedimiento, enlace/canal, documentos, cómo se confirma, estado de inscripción, disponibilidad de espacios, fecha y hora de verificación, lista de espera)
6. Contacto autorizado (nombre y cargo, teléfono o WhatsApp, correo electrónico, horario de atención)
7. Fuente y actualización (fuente oficial, responsable de actualizar, última actualización, estado de la feria, cambios o avisos, información pendiente)
8. Regla para el asistente de IA (responder con datos vigentes, indicar si falta información, no deducir costos/horarios/disponibilidad, pedir aclaración si hay varias ferias posibles, no confirmar inscripciones ni reservar espacios)

---

## Reglas de negocio (código, sin IA)

### Regla RB-01: Fuente de datos y versión
- La fuente inicial es `Actividades_Artesanos_Festival_2026.xlsx`, hoja `Exposición de artesanos`, encabezados fila 5, registros filas 6 a 16.
- Cada actividad se identifica por su código `RAA-DEMO-2026-001` a `RAA-DEMO-2026-011`.
- La implementación debe buscar por encabezado y código, no depender únicamente de posiciones de columnas.
- Conservar A a J como referencia original. Para las respuestas del ejercicio, usar los campos de práctica de K a BF cuando exista un valor específico sobre el mismo tema.
- La hoja de preguntas y respuestas es material de evaluación: no se usará como sustituto de la consulta de registros.
- `Ficha_de_Feria_RAA.docx` define los campos. El Excel contiene los valores para responder.

### Regla RB-02: Fecha fija de demostración
- Fecha y hora de referencia: **4 de noviembre de 2026 a las 12:00 m., zona America/Costa_Rica**.
- Mostrar esa referencia en el modo de demostración.
- Las marcas de verificación y actualización del Excel del `04/11/2026 18:00` se interpretan como UTC, equivalentes a las 12:00 m. de Costa Rica.
- Las fechas de eventos se interpretan como fechas locales y las horas de atención como horas locales.
- No usar la fecha real del equipo mientras esté activada la fecha fija de demostración.

### Regla RB-03: Próxima actividad
- Buscar la fecha de inicio más cercana que sea igual o posterior a la fecha de referencia, excluyendo actividades canceladas y finalizadas.
- Si varias actividades comparten la primera fecha, mencionarlas o pedir cuál interesa.

### Regla RB-04: Identificar la actividad
- Buscar por código, nombre, fecha o lugar.
- Conservar como contexto la actividad que la persona seleccionó o aclaró dentro de la conversación.
- Si una pregunta permite identificar varias actividades, pedir aclaración antes de responder costos, horarios, cupos o requisitos. Ejemplo: "¿A cuál feria te referís? Podés indicarme el nombre, la fecha o el lugar".
- No elegir una actividad por defecto.
- El identificador de una prueba sirve para verificar el resultado; no cuenta como contexto del chat salvo que la persona haya seleccionado esa actividad.
- Si no hay coincidencias, decirlo y ofrecer consultar las actividades registradas.
- Si la persona cambia de feria, actualizar el contexto.

### Regla RB-05: Redactar con respaldo en el registro
- Responder en español claro, cordial y breve.
- Priorizar el dato solicitado y añadir solo las condiciones necesarias para interpretarlo.
- No inventar información durante la conversación. Los datos ficticios preparados en el Excel sí pueden consultarse porque forman parte del escenario definido.
- No convertir el horario de atención en horario de montaje, el responsable de la actividad en contacto autorizado, ni los cupos disponibles en una reserva.
- Indicar el código de la actividad y la última actualización en una referencia visible junto a la respuesta. Ante cupos, mostrar además cuándo se verificaron.
- Mostrar permanentemente "Demostración con datos simulados". En respuestas sobre costos, cupos, contactos o inscripción, aclarar que corresponden al escenario de práctica.

### Regla RB-06: Información faltante y preguntas fuera del tema
- Campos vacíos, "Por confirmar", "Por definir" o "No indicado" = desconocidos.
- Distinguir "No aplica", "No habilitado" y el número cero: no representan el mismo estado. El valor 0 en cupos significa que no hay espacios.
- Si falta información, responder únicamente lo conocido y explicar qué dato no está disponible.
- Cuando exista un contacto autorizado, ofrecerlo como referencia de práctica.
- Si preguntan por compradores, ganancias, clima u otra información no registrada, no estimar valores ni buscar fuera del conjunto de datos en esta versión.

### Regla RB-07: Inscripción y disponibilidad
- Si la actividad está cancelada, indicar la cancelación antes de cualquier instrucción de participación.
- Si está finalizada, presentarla como actividad pasada.
- Si la inscripción está cerrada o venció el plazo respecto a la fecha de referencia, informarlo aunque todavía aparezcan espacios. No afirmar que se puede inscribir.
- Si hay 0 espacios, informar que no hay cupos y explicar la lista de espera solo si está registrada. No crear una inscripción en esa lista.
- Si la inscripción está abierta, el plazo está vigente y hay cupos, comunicar lo registrado con su fecha de verificación. No garantizar disponibilidad en tiempo real ni confirmar participación.
- Si falta el estado, el plazo o la verificación de cupos, no asegurar que puede inscribirse o que hay disponibilidad actual. Explicar qué dato falta.

### Regla RB-08: Actualizaciones y administración
- Solo la persona administradora podrá crear o modificar fichas mediante las funciones previstas para ello.
- El chat del visitante no modifica fechas, costos, cupos ni estados. Una solicitud como "cambiá el precio a mil" no altera el registro.
- Después de guardar un cambio válido, actualizar la marca de última actualización y consultar la versión vigente en las respuestas siguientes.
- Si un registro fue editado en la app, esa versión guardada será la fuente de trabajo; el Excel será la carga inicial.
- Una nueva importación no sobrescribirá cambios sin una acción explícita de la persona administradora.

### Regla RB-09: Consulta mediante herramientas y API
- La implementación deberá permitir buscar actividades y recuperar una ficha por identificador.
- El agente utilizará esas herramientas para obtener datos antes de responder preguntas específicas.
- Las instrucciones de un visitante no se tratarán como autorización para cambiar registros ni como fuente de información sobre una feria.
- Si la consulta falla, el servicio no está disponible o el registro no se encuentra, indicar que no fue posible recuperar los datos e invitar a reintentar. No responder como si la búsqueda hubiera tenido éxito.
- Las claves de API se mantienen en la configuración del servidor y no se muestran en respuestas.

### Regla RB-10: Enlaces, contactos y acciones del ejercicio
- Los enlaces y correos con dominio `.example` son ficticios. Mostrarlos como texto identificado como ejemplo y no ofrecerlos como canales reales ni botones operativos.
- Si Teléfono o WhatsApp de práctica indica "No habilitado en el ejercicio", comunicar ese estado sin inventar un número.
- No enviar mensajes, efectuar pagos, reservar puestos ni confirmar inscripciones. Si se solicita una de esas acciones, explicar el alcance informativo y describir el procedimiento registrado como parte de la simulación.

### Regla RB-11: Validación de datos (formulario de administración)
- Validar identificador único, nombre, fechas válidas y orden de fechas.
- Mantener costo y cupos como números no negativos; no convertir un campo vacío en cero.
- Conservar desconocidos como información no disponible.
- No exigir que todo dato opcional esté completo para guardar una ficha.
- Para el modelo de una jornada por registro, validar que montaje no sea posterior al inicio de atención y que desmontaje no sea anterior al cierre.
- Registrar el responsable de actualización y validar fecha y hora límite de inscripción.
- Al guardar correctamente, mostrar confirmación, actualizar la fecha de modificación y reflejar el cambio en la ficha y el chat. Cancelar no altera el registro.

### Regla RB-12: Importación de Excel
- Leer los encabezados y códigos del Excel, presentar una vista previa y errores por fila.
- La carga inicial incorpora los 11 registros.
- Si un código ya existe, solicitar una decisión explícita antes de reemplazarlo.
- No modificar la hoja de preguntas y respuestas ni usarla como fuente de fichas.

### Regla RB-13: Cobertura de pantallas (desde `Pantallas_Funciones_y_Agentes_RAA.docx`)
- Pantalla de inicio y listado: mostrar nombre "Asistente de Ferias RAA", aviso "Demostración con datos simulados", fecha fija de demostración (04/11/2026 12:00 m.), actividades ordenadas por fecha y hora de atención. Cada tarjeta muestra nombre, fecha, lugar, horario de atención, estado de la actividad y estado de inscripción. Botones: Ver detalles y Consultar al asistente. Filtros: búsqueda por nombre o código, fecha y lugar. Las actividades canceladas o finalizadas deben identificarse claramente. Si no hay resultados, mostrar "No encontramos actividades con esos filtros" y un botón para limpiarlos. Si falla la carga, ofrecer Reintentar sin mostrar datos inventados.
- Pantalla de detalle: abrir actividad por identificador único. Bloques: información general; fechas y horarios; ubicación y acceso; costos; requisitos y equipo; inscripción y cupos; contacto y actualización. Separar atención, ingreso y montaje, salida y desmontaje. Mostrar costo con moneda y unidad de cobro. Indicar fecha y hora límite de inscripción. Mostrar última verificación junto a los cupos. Los contactos y enlaces `.example` aparecen como ejemplos no operativos. Si falta un dato, mostrar "Información no disponible". Botones: Consultar sobre esta feria y Volver al listado. Al abrir el chat desde aquí, enviar el identificador como contexto visible y permitir cambiar de actividad.
- Pantalla de chat: mostrar historial de la sesión, campo de pregunta, botón Enviar y botón Nueva conversación. Indicar la actividad seleccionada, si existe, y mantener el aviso de simulación. Preguntas sugeridas como "¿Cuánto cuesta participar?" y "¿Qué debo llevar?". Al enviar: mostrar que se está consultando y evitar envíos duplicados. Al recibir: mostrar respuesta, identificador de la feria y última actualización; si se habla de cupos, añadir su fecha de verificación. Si hay ambigüedad, ofrecer opciones con nombre, fecha y lugar. No seleccionar una feria sin aclaración. Nueva conversación borra el contexto anterior. Si no se puede responder, explicar el motivo y, cuando corresponda, ofrecer el contacto de práctica. Si falla el servicio, conservar la pregunta y permitir reintentar.
- Pantallas de administración: acceso con formulario de ingreso y salida de sesión; error general ante credenciales incorrectas. No publicar credenciales de demostración dentro de los archivos de insumos. Panel: lista de actividades con código, nombre, fecha, estado y última actualización. Acciones: Crear ficha, Editar e Importar Excel. Sección para revisar preguntas sin respuesta registradas en el prototipo, con fecha y motivo. No requiere un tablero de estadísticas.

---

## Lo que hace el agente de IA (con el contrato JSON)

Tres roles académicos propuestos (pueden implementarse como uno o varios agentes según la consigna del curso). En cualquier caso debe existir una consulta real a herramientas mediante código; describir roles en un prompt no sustituye esa consulta.

### Agente de consulta
**Propósito:** comprender la pregunta e identificar qué actividad y dato se necesitan.
**Entrada:** pregunta, contexto visible de la conversación, fecha de demostración.
**Herramienta:** `buscar_ferias` con filtros por código, nombre, fecha o lugar.
**Salida:** una de:
1. Consulta identificada con código y campos solicitados.
2. Lista de candidatas para aclaración.
3. Sin coincidencias.
4. Pregunta fuera del alcance.
**Restricción:** no inventa una coincidencia ni modifica registros.

### Agente de búsqueda
**Propósito:** recuperar los valores de la fuente de trabajo vigente.
**Entrada:** identificador y campos necesarios.
**Herramientas:** `obtener_ficha` y, para consultas generales, `listar_proximas_ferias`. Estas herramientas consultan el almacenamiento de la app cargado inicialmente desde el Excel.
**Salida:** datos recuperados, campos desconocidos, inconsistencias, código, versión o última actualización y fecha de verificación de cupos.
**Restricción:** si una herramienta falla, devuelve un error explícito. Aplica la prioridad de datos simulados y no combina valores contradictorios.

### Agente de respuesta
**Propósito:** redactar una respuesta breve y respaldada.
**Entrada:** pregunta, datos recuperados y estados de aclaración o error.
**Reglas:** aplica las reglas del insumo 2 (RB-02 a RB-10) para inscripción, plazos, cupos y actividades canceladas.
**Salida:** texto para el visitante y una referencia visible al registro.
**Restricción:** si falta información, lo explica; si la consulta es ambigua, pide aclaración. No afirma reservas, pagos ni inscripciones y no rellena valores con conocimiento general.

### Coordinación y herramientas propuestas
**Flujo normal:** el visitante pregunta; el agente de consulta identifica o aclara; el agente de búsqueda recupera la ficha; el agente de respuesta redacta; la interfaz muestra texto y referencia. Un controlador en código conserva el contexto y deriva errores. No debe continuar con una respuesta factual si falló la búsqueda.

#### Contrato JSON de herramientas

**`buscar_ferias`** (solo lectura)
```json
{
  "nombre": "buscar_ferias",
  "argumentos": {
    "codigo": "string | null",
    "nombre": "string | null",
    "fecha": "string | null",
    "lugar": "string | null"
  },
  "salida": {
    "resultados": [
      {
        "codigo": "string",
        "nombre": "string",
        "fecha": "string",
        "lugar": "string"
      }
    ],
    "error": "string | null"
  }
}
```

**`obtener_ficha`** (solo lectura)
```json
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
```

**`listar_proximas_ferias`** (solo lectura)
```json
{
  "nombre": "listar_proximas_ferias",
  "argumentos": {
    "fecha_referencia": "string",
    "filtros": { "nombre": "string | null", "lugar": "string | null" }
  },
  "salida": {
    "actividades": [
      {
        "codigo": "string",
        "nombre": "string",
        "fecha_inicio": "string",
        "lugar": "string",
        "estado": "string"
      }
    ],
    "error": "string | null"
  }
}
```

**Funciones exclusivas de administración (no disponibles para los agentes del chat público):**

**`guardar_ficha`**
```json
{
  "nombre": "guardar_ficha",
  "argumentos": {
    "ficha": { "campo": "valor" },
    "permiso_administrador": true
  },
  "salida": {
    "exito": true,
    "fecha_modificacion": "string",
    "error": "string | null"
  }
}
```

**`importar_ferias`**
```json
{
  "nombre": "importar_ferias",
  "argumentos": {
    "archivo_excel": "string",
    "decision_codigo_existente": "reemplazar | cancelar | null"
  },
  "salida": {
    "registros_cargados": number,
    "errores_por_fila": ["string"],
    "vista_previa": ["string"],
    "error": "string | null"
  }
}
```

**`registrar_consulta_no_resuelta`**
```json
{
  "nombre": "registrar_consulta_no_resuelta",
  "argumentos": {
    "pregunta": "string",
    "motivo": "string",
    "actividad_identificada": "string | null"
  },
  "salida": {
    "registrada": true,
    "error": "string | null"
  }
}
```

---

## Qué produce la app

1. **Listado de ferias** con 11 registros, cada tarjeta muestra nombre, fecha, lugar, horario de atención, estado de la actividad y estado de inscripción.
2. **Ficha de detalle por actividad** (abierta por identificador único), organizada en bloques: información general; fechas y horarios; ubicación y acceso; costos; requisitos y equipo; inscripción y cupos; contacto y actualización.
3. **Chat informativo** con historial de sesión, respuestas basadas en registros, referencia visible al registro (código + última actualización), y fecha de verificación de cupos cuando corresponda.
4. **Pantallas de administración** para crear, editar e importar fichas, y revisar preguntas sin respuesta.
5. **Aviso permanente:** "Demostración con datos simulados".
6. **Registro de consultas no resueltas** guardado aparte para revisión administrativa (fecha y motivo).
7. **No produce:** cobros, asignación de puestos, inscripciones automáticas, integración con WhatsApp, confirmación de cupos en tiempo real, cuentas individuales por afiliado, tablero de estadísticas.

---

## Quién decide

| Rol | Decide |
|-----|--------|
| Persona administradora designada por la RAA | Crear y editar fichas, registrar cambios, indicar el estado de inscripción, revisar consultas sin respuesta, importar datos iniciales, decidir explícitamente si reemplazar códigos existentes en reimportación. |
| Visitante / afiliado | Consultar lista y fichas, filtrar actividades, hacer preguntas, comenzar una conversación nueva. No puede modificar información. No requiere registro en esta versión. |
| Agente de IA (chat público) | Interpretar preguntas, identificar actividades, recuperar datos, redactar respuestas. **No** puede modificar registros ni confirmar inscripciones/reservas/pagos. |
| Curso / consigna | Elegir proveedor, modelo, framework, formato de rutas, y si se implementan como tres agentes separados o roles coordinados. |

**Quién decide qué dato es vigente:** tras una edición administrativa guardada, la versión guardada en la app es la fuente de trabajo; el Excel es la carga inicial.

---

## Cifras de control

| Métrica | Valor | Fuente |
|---------|-------|--------|
| Número de registros de actividades | 11 | `Actividades_Artesanos_Festival_2026.xlsx`, filas 6 a 16 |
| Códigos de actividades | `RAA-DEMO-2026-001` a `RAA-DEMO-2026-011` | Columna K del Excel |
| Número de pruebas (P) | 20 (P01 a P20) | `Preguntas_y_Respuestas_Prueba_RAA.xlsx`, filas 7 a 26 |
| Número de casos de prueba (CP) | 20 (CP01 a CP20) | `Casos_de_Prueba_y_Resultados_Esperados_RAA.xlsx`, filas 8 a 27 |
| Columnas del Excel de actividades | 58 (A a BF) | `Actividades_Artesanos_Festival_2026.xlsx` |
| Fecha fija de demostración | 04/11/2026 12:00 p. m. America/Costa_Rica | Contexto, reglas de negocio |
| Marcas de verificación/actualización del Excel interpretadas como UTC | 04/11/2026 18:00 UTC | Contexto, reglas de negocio |
| Costo de ejemplo (Open Taekwondo) | ₡4.000 por puesto y jornada | Contexto, regla RB-11 ejemplo |
| Espacios disponibles de ejemplo (Open Taekwondo) | 5 espacios, verificados 04/11/2026 | Contexto, regla RB-11 ejemplo |
| Fecha límite de inscripción ejemplo (Open Taekwondo) | 12 de noviembre de 2026 a las 6:00 p. m. | `Preguntas_y_Respuestas_Prueba_RAA.xlsx`, P13 |
| Fecha límite de pago ejemplo (Open Taekwondo) | 13 de noviembre de 2026 | `Preguntas_y_Respuestas_Prueba_RAA.xlsx`, P15 |

---

## Casos límite

Estos casos están definidos en `Casos_de_Prueba_y_Resultados_Esperados_RAA.xlsx` (insumo 4) y requieren escenarios adicionales o una copia de prueba; no se afirma que ya existan en los 11 registros base:

1. **Carga inicial (CP01):** entorno vacío, importar Excel, revisar vista previa y confirmar carga de 11 códigos únicos.
2. **Consulta directa (CP02):** pregunta sobre costo del Open sin modificar datos.
3. **Selección desde ficha (CP03):** contexto de ficha seleccionada, distinguir montaje de atención.
4. **Pregunta ambigua (CP04):** chat nuevo sin feria seleccionada, pedir nombre/fecha/lugar.
5. **Actividad inexistente (CP05):** "Feria Lunar del 30 de febrero", no crear feria ni atribuir datos de otro registro.
6. **Dato desconocido (CP06):** campo Equipo del participante vacío, informar que no está disponible.
7. **Cupos agotados (CP07):** Espacios disponibles = 0, Estado de inscripción = Abierta, plazo vigente, verificación 04/11/2026 18:00 UTC.
8. **Inscripción cerrada con cupos (CP08):** Estado de inscripción = Cerrada, Espacios disponibles = 5, plazo vigente.
9. **Plazo vencido (CP09):** Estado de inscripción = Abierta, plazo 03/11/2026 18:00 hora Costa Rica, reloj de demostración 04/11/2026 12:00.
10. **Actividad cancelada (CP10):** Estado de la feria = Cancelada, informar cancelación antes de cualquier instrucción de participación.
11. **Verificación de cupos ausente (CP11):** borrar Verificación de espacios, conservar 5 cupos e inscripción abierta; no asegurar disponibilidad actual.
12. **Actualizar horario (CP12):** cambiar inicio de atención a 09:00, guardar, consultar de nuevo; la segunda respuesta indica el nuevo valor y muestra la nueva actualización.
13. **Prioridad del dato simulado (CP13):** RAA-DEMO-2026-010, mantener nota original de 12 a. m. y campo simulado de 12:00 p. m.; responder 12:00 p. m. para la simulación.
14. **Fallo del servicio de datos (CP14):** fallo controlado en `obtener_ficha` para el Open; durante el fallo explicar que no se pudo recuperar, al reintentar responder desde el registro.
15. **Fallo de API de IA (CP15):** interfaz informa el fallo, conserva la pregunta, permite reintentar. No mostrar respuesta factual como si hubiera funcionado.
16. **Cambio desde chat público (CP16):** "Cambiá el costo del Open a ₡1.000", el chat explica su alcance informativo, el precio permanece en ₡4.000.
17. **Reserva fuera del alcance (CP17):** "Reservame un campo y confirmame que ya quedé inscrita", explicar que no realiza reservas ni confirma inscripciones; cupos siguen en 5.
18. **Reimportación con código existente (CP18):** importar Excel original con los mismos 11 identificadores, detectar códigos existentes y requerir decisión explícita; cancelar preserva el cambio administrativo.
19. **Dato numérico inválido (CP19):** intentar guardar costo = -1000 y cupos = -2; señalar campos inválidos y rechazar esos cambios; permitir guardar al corregirlos.
20. **Restablecer conversación (CP20):** Nueva conversación borra el contexto anterior; ya no usar automáticamente el Open como contexto.

**Escenarios adicionales que requieren preparación:** cancelación, inscripción cerrada, cero cupos, actualización y fallos de consulta (según insumo 4, sección 12 del contexto).

---

## Reglas del sistema

1. **Solo lectura para el chat público:** `buscar_ferias`, `obtener_ficha` y `listar_proximas_ferias` son de solo lectura. `guardar_ficha` e `importar_ferias` son exclusivos de administración y requieren verificación de permisos.
2. **No continuar si falla la búsqueda:** un controlador en código conserva el contexto y deriva errores. No debe continuar con una respuesta factual si falló la búsqueda.
3. **Prioridad de datos simulados:** aplicar la prioridad de campos del insumo 2 (RB-02) y no combinar valores contradictorios.
4. **No inventar información:** no afirmar reservas, pagos ni inscripciones; no rellenar valores con conocimiento general; no estimar compradores, ganancias, clima u otra información no registrada.
5. **Siempre mostrar aviso de simulación:** "Demostración con datos simulados" de forma permanente.
6. **Credenciales fuera del código público:** no publicar credenciales de demostración dentro de los archivos de insumos; las claves de API se mantienen en la configuración del servidor.
7. **Historial de chat:** se conserva durante la sesión y se limpia al iniciar una conversación nueva.
8. **Consultas no resueltas:** se guardan aparte para revisión administrativa, con fecha y motivo. Para la práctica se usan preguntas ficticias, sin datos personales innecesarios.
9. **Registro de evaluación:** permanece en el Excel del insumo 1 (`Preguntas_y_Respuestas_Prueba_RAA.xlsx`).
10. **Procedimiento de inscripción (simulado):** el enlace del archivo es ficticio y no permite inscribirse realmente; describir el procedimiento registrado como parte de la simulación sin confirmar participación.
