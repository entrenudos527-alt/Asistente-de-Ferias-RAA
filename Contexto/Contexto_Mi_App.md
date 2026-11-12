# Contexto_Mi_App

Contenido extraído de todos los documentos de la carpeta Contexto.


## Documento: Asistente_Ferias_RAA_Problema_e_Insumos (1).pdf


### PDF: Asistente_Ferias_RAA_Problema_e_Insumos (1).pdf — 3 páginas


--- Página 1 ---

RAA | Propuesta inicial para curso de inteligencia artificial
1
ASISTENTE DE
FERIAS RAA
Definición del problema e insumos del proyecto
Red Alajuelita Artesanal (RAA)
1. Contexto y necesidad
La Red Alajuelita Artesanal organiza y comunica información sobre ferias a sus afiliados. Según lo
expresado por su representante, las personas consultan repetidamente por las ferias, aunque ya se les
haya facilitado la información. Esto obliga a responder varias veces preguntas similares.
2. Definición del problema
La RAA necesita facilitar a sus afiliados el acceso a información oficial y actualizada sobre las
ferias, porque las consultas repetidas generan trabajo manual para la organización y muestran una
dificultad para localizar o recuperar la información previamente compartida.
Las consultas pueden referirse a fechas, lugares, horarios, costos, requisitos e inscripción. Estos temas
son ejemplos que deberán validarse con preguntas reales de los afiliados.
3. Causas por validar y consecuencias
Posibles causas: información repartida entre comunicaciones, dificultad para encontrar mensajes
anteriores y cambios en los datos de una feria. Son hipótesis iniciales; todavía no se ha confirmado el
canal utilizado ni la frecuencia de las consultas.
Consecuencias: tiempo dedicado a repetir respuestas, interrupciones en otras tareas de coordinación y
riesgo de confusión cuando circulan versiones distintas de la información.
4. Pregunta del proyecto
¿Cómo facilitar que los afiliados consulten información oficial y vigente de las ferias de la RAA, mediante
una app web con agentes de IA conectados por API, y reducir las respuestas manuales repetidas?


--- Página 2 ---

RAA | Propuesta inicial para curso de inteligencia artificial
2
Propuesta y alcance
5. Definición de la solución
Crear una aplicación web, accesible desde el celular mediante un enlace, con una lista de ferias y un chat.
La persona encargada registra y actualiza los datos en un único lugar; los afiliados preguntan con sus
propias palabras y reciben respuestas basadas en esos registros.
Objetivo general: facilitar el acceso autónomo a la información de las ferias y disminuir la carga de
consultas repetidas para la organización.
Objetivos específicos: centralizar los datos oficiales; responder preguntas frecuentes con respaldo en la
fuente; detectar información faltante o ambigua; permitir que la organización mantenga los datos
actualizados.
6. Usuarios y funciones iniciales
Usuario
Funciones propuestas
Afiliado o persona interesada
Consultar próximas ferias, revisar su ficha y hacer preguntas en el chat.
Persona administradora
designada por la RAA
Crear y editar fichas, registrar cambios, indicar el estado de inscripción y revisar
consultas sin respuesta.
7. Agentes y API: diseño preliminar
Componente
Responsabilidad
Agente de consulta
Interpretar la pregunta e identificar la feria. Pedir aclaración si hay varias
posibilidades.
Agente de búsqueda
Consultar mediante una herramienta/API el registro oficial de la feria y recuperar
datos y fuentes.
Agente de respuesta
Redactar una respuesta breve respaldada por los datos recuperados e indicar lo
que no se conoce.
Los tres roles son una propuesta para discutir en clase; podrían implementarse con uno o varios agentes
según la consigna. El código deberá ofrecer herramientas concretas para consultar registros, más allá de
enviar instrucciones a un modelo.
Papel de las herramientas: OpenCode apoyaría la programación. La API de IA permitiría interpretar y
redactar; la API de datos permitiría consultar las fichas. El proveedor y la tecnología se elegirán durante el
curso.
8. Límites de la primera versión
Incluir: fichas de ferias, administración básica y chat informativo. Dejar para una etapa posterior: cobros,
asignación de puestos, inscripciones automáticas e integración con WhatsApp. La disponibilidad de
espacios solo se informará si existe un registro actualizado; la app no confirmará cupos por su cuenta.


--- Página 3 ---

RAA | Propuesta inicial para curso de inteligencia artificial
3
Insumos para comenzar
Insumos significa la información, los materiales y los recursos necesarios para construir y
probar la propuesta. Los siguientes elementos están por recopilar o confirmar.
9. Información y materiales necesarios
Insumo
Contenido requerido
Fichas de ferias
Nombre, identificador, fechas, ubicación, horarios de atención y montaje, costo, requisitos,
equipo que debe llevar cada participante, fecha límite, procedimiento de inscripción y
contacto autorizado.
Estado y actualización
Inscripción abierta/cerrada/por confirmar; cupos solo si se controlan; fecha de última
actualización y responsable del dato.
Fuentes oficiales
Comunicados, afiches, reglamentos o mensajes aprobados por la RAA. Cada dato deberá
relacionarse con su fuente vigente.
Preguntas reales
Entre 10 y 20 consultas habituales, sin datos personales innecesarios, junto con la
respuesta oficial esperada.
Reglas de atención
Quién actualiza; qué hacer si falta información; cómo identificar la versión vigente y a
quién remitir una consulta no resuelta.
Recursos técnicos y del
curso
Consigna, fecha de entrega, cantidad de agentes requerida, equipo con OpenCode,
acceso a una API de IA, almacenamiento de datos y entorno para ejecutar la app. Las
claves se guardarán fuera del código público.
10. Prueba inicial propuesta
Utilizar tres ferias de ejemplo y un conjunto de preguntas revisadas por la RAA. Si se emplean datos
ficticios, identificarlos claramente. Probar: una consulta directa, una feria ambigua, un dato faltante y un
cambio de horario.
Ejemplo: ante “¿A qué hora llegamos?”, la app identifica o pregunta por la feria y distingue el horario de
montaje del horario de atención. Si el montaje no está registrado, lo indica y ofrece el contacto autorizado.
11. Criterios para evaluar el resultado
Comprobar que las respuestas coincidan con las fichas; que no se inventen costos, cupos ni requisitos;
que se solicite aclaración cuando corresponda; y que una actualización se refleje en las consultas
siguientes. Para medir el beneficio real, registrar antes y después el número de consultas manuales y el
tiempo de atención, sin asumir una reducción todavía.
Estado del proyecto: propuesta conceptual para llevar a clase. La programación, las integraciones y las
decisiones técnicas quedan pendientes del avance y los requisitos del curso.


## Documento: Pantallas_Funciones_y_Agentes_RAA.docx

Pantallas funciones y agentes del Asistente de Ferias RAA
Insumo 3 para programar la aplicación web | Caso de estudio
Esta especificación describe la primera versión del prototipo: consultar las ferias, abrir sus fichas, conversar con un asistente y administrar los datos. Las pantallas y herramientas son propuestas para implementar durante el curso. Se utilizarán los 11 registros del Excel y las reglas del insumo 2.
1 Usuarios y permisos
Visitante o afiliado: consultar lista y fichas, filtrar actividades, hacer preguntas y comenzar una conversación nueva. No requiere registro en esta versión y no puede modificar información.
Persona administradora: ingresar con una cuenta de demostración configurada fuera de los documentos públicos; crear y editar fichas, revisar consultas no resueltas e importar los datos iniciales. El servidor debe verificar sus permisos antes de aceptar cambios.
Alcance inicial: información y administración básica. Las reservas, cobros, envío de mensajes, inscripción automática y asignación de puestos quedan para otra etapa. No se necesita una cuenta distinta para cada afiliado.
2 Pantalla de inicio y listado de ferias
Mostrar el nombre Asistente de Ferias RAA, el aviso “Demostración con datos simulados” y la fecha fija de demostración definida en el insumo 2. Presentar las actividades ordenadas por fecha y hora de atención. Usar un diseño cómodo en celular, con texto legible y botones visibles.
Cada tarjeta muestra nombre, fecha, lugar, horario de atención, estado de la actividad y estado de inscripción. Botones: Ver detalles y Consultar al asistente.
Filtros: búsqueda por nombre o código, fecha y lugar. Las actividades canceladas o finalizadas deben identificarse claramente; el filtro Próximas aplica las reglas del insumo 2.
Si no hay resultados, mostrar “No encontramos actividades con esos filtros” y un botón para limpiarlos. Si falla la carga, ofrecer Reintentar sin mostrar datos inventados.
3 Pantalla de detalle de la feria
Abrir la actividad por su identificador único. Organizar la ficha en bloques: información general; fechas y horarios; ubicación y acceso; costos; requisitos y equipo; inscripción y cupos; contacto y actualización.
Separar atención, ingreso y montaje, salida y desmontaje. Mostrar costo con moneda y unidad de cobro. Indicar fecha y hora límite de inscripción.
Mostrar la última verificación junto a los cupos. Los contactos y enlaces .example aparecen como ejemplos no operativos. Si falta un dato, mostrar “Información no disponible”.
Incluir Consultar sobre esta feria y Volver al listado. Al abrir el chat desde aquí, enviar el identificador como contexto visible y permitir cambiar de actividad.
4 Pantalla de chat
Mostrar historial de la sesión, campo de pregunta, botón Enviar y botón Nueva conversación. Indicar la actividad seleccionada, si existe, y mantener el aviso de simulación. Ofrecer preguntas sugeridas como “¿Cuánto cuesta participar?” y “¿Qué debo llevar?”.
Al enviar: mostrar que se está consultando y evitar envíos duplicados. Al recibir: mostrar respuesta, identificador de la feria y última actualización; si se habla de cupos, añadir su fecha de verificación.
Si hay ambigüedad, ofrecer opciones con nombre, fecha y lugar. No seleccionar una feria sin aclaración. Nueva conversación borra el contexto anterior.
Si no se puede responder, explicar el motivo y, cuando corresponda, ofrecer el contacto de práctica. Si falla el servicio, conservar la pregunta y permitir reintentar.
5 Pantallas de administración
Acceso: formulario de ingreso y salida de sesión. Mostrar un error general ante credenciales incorrectas. No publicar credenciales de demostración dentro de los archivos de insumos.
Panel: lista de actividades con código, nombre, fecha, estado y última actualización. Acciones: Crear ficha, Editar e Importar Excel. Una sección permite revisar las preguntas sin respuesta registradas en el prototipo, con fecha y motivo. No requiere un tablero de estadísticas.
Formulario: agrupar los campos según la ficha de Word. Usar Guardar y Cancelar. Al guardar correctamente, mostrar confirmación, actualizar la fecha de modificación y reflejar el cambio en la ficha y el chat. Cancelar no altera el registro.
Validar identificador único, nombre, fechas válidas y orden de fechas. Mantener costo y cupos como números no negativos; no convertir un campo vacío en cero. Conservar desconocidos como información no disponible.
Para el modelo de una jornada por registro, validar que montaje no sea posterior al inicio de atención y que desmontaje no sea anterior al cierre. Si se necesitan actividades nocturnas, ampliar después a fechas y horas completas.
Registrar el responsable de actualización y validar fecha y hora límite de inscripción. No exigir que todo dato opcional esté completo para guardar una ficha.
Importación: leer los encabezados y códigos del Excel, presentar una vista previa y errores por fila. La carga inicial incorpora los 11 registros. Si un código ya existe, solicitar una decisión explícita antes de reemplazarlo. No modificar la hoja de preguntas y respuestas ni usarla como fuente de fichas.
6 Agente de consulta
Propósito: comprender la pregunta e identificar qué actividad y dato se necesitan. Recibe pregunta, contexto visible de la conversación y fecha de demostración. Puede utilizar la herramienta buscar_ferias con filtros por código, nombre, fecha o lugar.
Entrega una de estas salidas: consulta identificada con código y campos solicitados; lista de candidatas para aclaración; sin coincidencias; o pregunta fuera del alcance. No inventa una coincidencia ni modifica registros.
7 Agente de búsqueda
Propósito: recuperar los valores de la fuente de trabajo vigente. Recibe el identificador y los campos necesarios. Utiliza obtener_ficha y, para consultas generales, listar_proximas_ferias. Estas herramientas consultan el almacenamiento de la app cargado inicialmente desde el Excel.
Entrega datos recuperados, campos desconocidos, inconsistencias, código, versión o última actualización y fecha de verificación de cupos. Si una herramienta falla, devuelve un error explícito. Aplica la prioridad de datos simulados y no combina valores contradictorios.
8 Agente de respuesta
Propósito: redactar una respuesta breve y respaldada. Recibe la pregunta, los datos recuperados y los estados de aclaración o error. Aplica las reglas del insumo 2 para inscripción, plazos, cupos y actividades canceladas.
Entrega texto para el visitante y una referencia visible al registro. Si falta información, lo explica; si la consulta es ambigua, pide aclaración. No afirma reservas, pagos ni inscripciones y no rellena valores con conocimiento general.
Los tres roles constituyen el diseño académico propuesto. La consigna del curso determinará si se implementan como tres agentes separados o como roles coordinados. En cualquier caso debe existir una consulta real a herramientas mediante código; describir roles en un prompt no sustituye esa consulta.
9 Coordinación y herramientas propuestas
Flujo normal: el visitante pregunta; el agente de consulta identifica o aclara; el agente de búsqueda recupera la ficha; el agente de respuesta redacta; la interfaz muestra texto y referencia. Un controlador en código conserva el contexto y deriva errores. No debe continuar con una respuesta factual si falló la búsqueda.
buscar_ferias: recibe filtros; devuelve códigos, nombres, fechas y lugares. Es de solo lectura.
obtener_ficha: recibe un identificador; devuelve la ficha vigente y sus marcas de actualización. Es de solo lectura.
listar_proximas_ferias: recibe fecha de referencia y filtros; devuelve actividades elegibles ordenadas, según el insumo 2. Es de solo lectura.
guardar_ficha e importar_ferias: funciones exclusivas de administración; validan permisos y datos. No están disponibles para los agentes del chat público.
registrar_consulta_no_resuelta: guarda la pregunta, el motivo y la actividad si fue identificada. Para la práctica se usan preguntas ficticias, sin datos personales innecesarios.
La API de IA procesa el lenguaje y las llamadas a herramientas; la API de datos expone las consultas al almacenamiento del prototipo. OpenCode se utilizará para programar. El proveedor, modelo, framework y formato final de las rutas se elegirán con la consigna del curso; este documento no los fija.
10 Datos presentación y conservación
Importar el Excel a un modelo de trabajo con un registro por código. Para la demostración usar los campos simulados como establece el insumo 2 y conservar la referencia original sin mezclarla en respuestas. Tras una edición administrativa, consultar la versión guardada vigente. Mantener fechas y números como valores estructurados, no solo texto de presentación.
La fecha fija de demostración es 04/11/2026 a las 12:00 m., zona America/Costa_Rica. Las marcas 04/11/2026 18:00 del Excel se interpretan como UTC según el insumo 2. La app debe respetar esa convención para no cambiar días u horas al mostrar los datos.
El historial del chat se conserva durante la sesión y se limpia al iniciar una conversación nueva. Las consultas no resueltas se guardan aparte para revisión administrativa. El registro de evaluación de las pruebas permanece en el Excel del insumo 1.
11 Comprobación del alcance
Desde el listado se pueden abrir las 11 fichas y consultar una actividad con su código como contexto.
El chat consulta herramientas, distingue una pregunta ambigua, explica un dato faltante y responde con datos del registro correspondiente.
Una edición válida guardada por administración aparece en la siguiente consulta. Una petición de cambio desde el chat público no altera los datos.
Las pruebas del insumo 1 se ejecutan con el resultado registrado. Los escenarios especiales de cancelación, cupos agotados, inscripción cerrada y errores de servicio se prepararán en el insumo 4.
Este documento deja definidas las pantallas, funciones y responsabilidades del prototipo. Su implementación y las pruebas de funcionamiento se realizarán durante la programación.

## Documento: Reglas_del_Asistente_y_Consulta_de_Datos_RAA.docx

Reglas del Asistente de Ferias RAA
Insumo 2 para programar la aplicación web | Caso de estudio
Este documento define qué puede responder el asistente, qué datos debe consultar y cómo actuar ante dudas o inconsistencias. Se aplicará al prototipo académico con información simulada. Son reglas propuestas para implementar y probar; no describen una aplicación ya programada.
1 Propósito y alcance
Ayudar a consultar fechas, ubicación, horarios, costos, requisitos, equipo, inscripción, disponibilidad y contactos de las actividades artesanales registradas. La aplicación informa; las inscripciones, reservas, pagos y comunicaciones externas quedan fuera de esta versión.
2 Fuente de consulta y versión de los datos
La fuente inicial es Actividades_Artesanos_Festival_2026(1).xlsx, hoja Exposición de artesanos. Los encabezados están en la fila 5 y los 11 registros en las filas 6 a 16. Cada actividad se identifica mediante su código RAA-DEMO-2026-001 a RAA-DEMO-2026-011. La implementación debe buscar por encabezado y código, no depender únicamente de posiciones de columnas.
El PDF del proyecto define el alcance. La ficha de Word define los campos. El Excel contiene los valores para responder. La hoja de preguntas y respuestas es material de evaluación: no se usará como sustituto de la consulta de registros.
Conservar A a J como referencia original. Para las respuestas del ejercicio, usar los campos de práctica de K a BF cuando exista un valor específico sobre el mismo tema.
Nombre: Actividad. Ubicación general: Lugar. Detalles del acceso: Dirección exacta de práctica y Acceso y parqueo.
Fechas: Fecha de inicio y Fecha de finalización. Atención: Inicio de atención simulado y Cierre de atención simulado. Montaje: Ingreso y montaje. Desmontaje: Salida y desmontaje.
Costo: Costo de participación, Moneda y Unidad de cobro. Inscripción: Estado de inscripción, Fecha límite de inscripción y Hora límite de inscripción. Cupos: Espacios disponibles y Verificación de espacios.
Si falta un valor de práctica, no completarlo con una suposición ni mezclarlo automáticamente con notas originales. Informar que no está disponible. Si los propios campos de práctica se contradicen, explicar la inconsistencia y solicitar revisión.
3 Fecha fija de demostración
Usar como fecha y hora de referencia el 4 de noviembre de 2026 a las 12:00 m., zona America/Costa_Rica. Mostrar esa referencia en el modo de demostración. Las marcas de verificación y actualización del Excel del 04/11/2026 a las 18:00 se interpretan como UTC, equivalentes a las 12:00 m. de Costa Rica. Las fechas de eventos se interpretan como fechas locales y las horas de atención como horas locales.
Para “próxima actividad”, buscar la fecha de inicio más cercana que sea igual o posterior a la fecha de referencia, excluyendo actividades canceladas y finalizadas. Si varias actividades comparten la primera fecha, mencionarlas o pedir cuál interesa. No usar la fecha real del equipo mientras esté activada la fecha fija de demostración.
Reglas de conversación y respuesta
4 Identificar la actividad
Buscar por código, nombre, fecha o lugar. Conservar como contexto la actividad que la persona seleccionó o aclaró dentro de la conversación.
Si una pregunta permite identificar varias actividades, pedir aclaración antes de responder costos, horarios, cupos o requisitos. Ejemplo: “¿A cuál feria te referís? Podés indicarme el nombre, la fecha o el lugar”.
No elegir una actividad por defecto. El identificador de una prueba sirve para verificar el resultado; no cuenta como contexto del chat salvo que la persona haya seleccionado esa actividad.
Si no hay coincidencias, decirlo y ofrecer consultar las actividades registradas. Si la persona cambia de feria, actualizar el contexto.
5 Redactar con respaldo en el registro
Responder en español claro, cordial y breve. Priorizar el dato solicitado y añadir solo las condiciones necesarias para interpretarlo.
No inventar información durante la conversación. Los datos ficticios preparados en el Excel sí pueden consultarse porque forman parte del escenario definido.
No convertir el horario de atención en horario de montaje, el responsable de la actividad en contacto autorizado, ni los cupos disponibles en una reserva.
Indicar el código de la actividad y la última actualización en una referencia visible junto a la respuesta. Ante cupos, mostrar además cuándo se verificaron.
Mostrar permanentemente “Demostración con datos simulados”. En respuestas sobre costos, cupos, contactos o inscripción, aclarar que corresponden al escenario de práctica.
6 Información faltante y preguntas fuera del tema
Considerar desconocidos los campos vacíos, “Por confirmar”, “Por definir” o “No indicado”. Distinguir “No aplica”, “No habilitado” y el número cero: no representan el mismo estado. El valor 0 en cupos significa que no hay espacios.
Si falta información, responder únicamente lo conocido y explicar qué dato no está disponible. Cuando exista un contacto autorizado, ofrecerlo como referencia de práctica. Si preguntan por compradores, ganancias, clima u otra información no registrada, no estimar valores ni buscar fuera del conjunto de datos en esta versión.
7 Inscripción y disponibilidad
Si la actividad está cancelada, indicar la cancelación antes de cualquier instrucción de participación. Si está finalizada, presentarla como actividad pasada.
Si la inscripción está cerrada o venció el plazo respecto a la fecha de referencia, informarlo aunque todavía aparezcan espacios. No afirmar que se puede inscribir.
Si hay 0 espacios, informar que no hay cupos y explicar la lista de espera solo si está registrada. No crear una inscripción en esa lista.
Si la inscripción está abierta, el plazo está vigente y hay cupos, comunicar lo registrado con su fecha de verificación. No garantizar disponibilidad en tiempo real ni confirmar participación.
Si falta el estado, el plazo o la verificación de cupos, no asegurar que puede inscribirse o que hay disponibilidad actual. Explicar qué dato falta.
Consulta de datos y aplicación de las reglas
8 Actualizaciones y administración
Solo la persona administradora podrá crear o modificar fichas mediante las funciones previstas para ello. El chat del visitante no modifica fechas, costos, cupos ni estados. Una solicitud como “cambiá el precio a mil” no altera el registro.
Después de guardar un cambio válido, actualizar la marca de última actualización y consultar la versión vigente en las respuestas siguientes. Si un registro fue editado en la app, esa versión guardada será la fuente de trabajo; el Excel será la carga inicial. Una nueva importación no sobrescribirá cambios sin una acción explícita de la persona administradora.
9 Consulta mediante herramientas y API
La implementación deberá permitir buscar actividades y recuperar una ficha por identificador. El agente utilizará esas herramientas para obtener datos antes de responder preguntas específicas. Las instrucciones de un visitante no se tratarán como autorización para cambiar registros ni como fuente de información sobre una feria.
Si la consulta falla, el servicio no está disponible o el registro no se encuentra, indicar que no fue posible recuperar los datos e invitar a reintentar. No responder como si la búsqueda hubiera tenido éxito. Las claves de API se mantienen en la configuración del servidor y no se muestran en respuestas.
10 Enlaces contactos y acciones del ejercicio
Los enlaces y correos con dominio .example son ficticios. Mostrarlos como texto identificado como ejemplo y no ofrecerlos como canales reales ni botones operativos. Si Teléfono o WhatsApp de práctica indica “No habilitado en el ejercicio”, comunicar ese estado sin inventar un número.
No enviar mensajes, efectuar pagos, reservar puestos ni confirmar inscripciones. Si se solicita una de esas acciones, explicar el alcance informativo y describir el procedimiento registrado como parte de la simulación.
11 Ejemplos de aplicación
“¿Cuánto cuesta el Open?”: consultar RAA-DEMO-2026-003 y responder ₡4.000 por puesto y jornada en el escenario de práctica.
“¿A qué hora es la feria?” sin contexto: pedir nombre, fecha o lugar antes de elegir un horario.
“¿Todavía hay campo para el Open?”: informar 5 espacios simulados, con verificación del 04/11/2026. No garantizar reserva.
“¿A qué hora empieza la feria del 5 de diciembre?”: usar 12:00 p. m. del campo de atención simulado; la nota original de 12 a. m. se conserva únicamente como referencia.
“Reservame un campo”: explicar que la aplicación informa y no confirma inscripciones.
12 Verificación en clase
Evaluar estas reglas con el archivo Preguntas_y_Respuestas_Prueba_RAA.xlsx. La respuesta puede variar en redacción, pero debe conservar datos, condiciones y límites. Registrar respuesta obtenida, resultado y observaciones. Las pruebas de cancelación, inscripción cerrada, cero cupos, actualización y fallos de consulta requieren escenarios adicionales o una copia de prueba; no se afirma que ya existan en los 11 registros.
Estas decisiones definen el comportamiento del prototipo y podrán ajustarse a la consigna del curso antes de programar.