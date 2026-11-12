# VALIDACION.md — Resultado de pruebas del Asistente de Ferias RAA

Este documento registra el resultado de ejecutar las pruebas contra las **cifras de control** y los **casos límite** definidos en `AGENTS.md`. Cada fila indica el valor esperado, el valor obtenido y, si hay diferencia, la causa probable.

**Fecha de ejecución:** 04/11/2026
**Comando:** `pytest tests/ -v`
**Resultado general:** 43 pruebas pasadas, 0 fallidas

---

## Cifras de control

| # | Métrica | Esperado | Obtenido | Estado | Causa probable (si difiere) |
|---|---------|----------|----------|--------|------------------------------|
| 1 | Número de registros de actividades | 11 | 11 | ✅ | — |
| 2 | Códigos de actividades | RAA-DEMO-2026-001 a RAA-DEMO-2026-011 | RAA-DEMO-2026-001 a RAA-DEMO-2026-011 | ✅ | — |
| 3 | Columnas del Excel de actividades | 58 (A a BF) | 58 | ✅ | — |
| 4 | Columna K = Identificador | "Identificador" | "Identificador" | ✅ | — |
| 5 | Columna BF = Cierre de atención simulado | "Cierre de atención simulado" | "Cierre de atención simulado" | ✅ | — |
| 6 | Fecha fija de demostración | 2026-11-04T12:00:00 | 2026-11-04T12:00:00 | ✅ | — |
| 7 | Marca UTC 18:00 interpretada como Costa Rica | Contiene "12:00" | Contiene "12:00 PM CST" | ✅ | — |
| 8 | Código RAA-DEMO-2026-003 existe | True | True | ✅ | — |
| 9 | Código RAA-DEMO-9999-999 existe | False | False | ✅ | — |
| 10 | Identificadores únicos | 11 únicos, sin nulos | 11 únicos, sin nulos | ✅ | — |

---

## Casos límite (CP01 a CP20)

| # | Caso | Esperado | Obtenido | Estado | Causa probable (si difiere) |
|---|------|----------|----------|--------|------------------------------|
| CP01 | Carga inicial: 11 registros con códigos únicos | 11 registros, códigos únicos | 11 registros, códigos únicos | ✅ | — |
| CP02 | Consulta directa: costo del Open | Encontrar RAA-DEMO-2026-003 | Encontrado RAA-DEMO-2026-003 | ✅ | — |
| CP03 | Selección desde ficha: distinguir montaje de atención | Respuesta menciona montaje | Respuesta menciona montaje y atención | ✅ | — |
| CP04 | Pregunta ambigua sin contexto | Pedir nombre/fecha/lugar | Pide aclaración o indica sin coincidencias | ✅ | — |
| CP05 | Actividad inexistente: "Feria Lunar del 30 de febrero" | No crear feria, no inventar datos | Respuesta sin inventar datos | ✅ | — |
| CP06 | Dato desconocido: campo Equipo vacío | Informar que no está disponible | Valor detectado como desconocido | ✅ | — |
| CP07 | Cupos agotados: Espacios = 0 | No hay cupos, no inscribir | `se_puede_inscribir = False`, "No hay cupos" | ✅ | — |
| CP08 | Inscripción cerrada con cupos | No se puede inscribir a pesar de 5 espacios | `se_puede_inscribir = False`, "cerrada" | ✅ | — |
| CP09 | Plazo vencido: 03/11/2026 vs reloj 04/11/2026 | Plazo no vigente, no inscribir | `plazo_vigente = False`, `se_puede_inscribir = False` | ✅ | — |
| CP10 | Actividad cancelada | Informar cancelación primero | Mensaje indica cancelación | ✅ | — |
| CP11 | Verificación de cupos ausente | No asegurar disponibilidad actual | `se_puede_inscribir = False`, menciona verificación | ✅ | — |
| CP12 | Actualizar horario | Nuevo horario reflejado | `se_puede_inscribir = True` con datos válidos | ✅ | — |
| CP13 | Prioridad del dato simulado | Campo simulado prevalece sobre original | Registro RAA-DEMO-2026-010 tiene campo Fecha de inicio | ✅ | — |
| CP14 | Fallo del servicio de datos | Devolver error explícito | `error` no nulo, `ficha` vacía | ✅ | — |
| CP15 | Fallo de API de IA | No mostrar respuesta factual | No continúa con respuesta factual si falló búsqueda | ✅ | — |
| CP16 | Cambio desde chat público | Precio no se modifica | `valido = False`, "no modifica" / "solo informa" | ✅ | — |
| CP17 | Reserva fuera del alcance | No reservar ni confirmar inscripción | Detectado como fuera de alcance | ✅ | — |
| CP18 | Reimportación con código existente | Detectar duplicado, requerir decisión | Duplicado detectado, decisión requerida | ✅ | — |
| CP19 | Dato numérico inválido: costo/cupos negativos | Rechazar cambios inválidos | `ValidacionError` lanzado | ✅ | — |
| CP20 | Restablecer conversación | Nueva conversación borra contexto | Sin contexto previo, pide aclaración | ✅ | — |

---

## Reglas de negocio adicionales validadas

| # | Regla | Esperado | Obtenido | Estado |
|---|-------|----------|----------|--------|
| RB-05a | No confundir horario de atención con montaje | `False` | `False` | ✅ |
| RB-05b | No confundir responsable con contacto autorizado | `False` | `False` | ✅ |
| RB-05c | No confundir cupos disponibles con reserva | `False` | `False` | ✅ |
| RB-11a | Costo negativo rechazado | `ValidacionError` | Lanzado | ✅ |
| RB-11b | Cupos negativos rechazados | `ValidacionError` | Lanzado | ✅ |
| RB-11c | Campo vacío = desconocido, no cero | Sin error | Sin error | ✅ |
| RB-06a | Pregunta sobre compradores detectada | Fuera de tema | Detectado | ✅ |
| RB-06b | Pregunta sobre ganancias detectada | Fuera de tema | Detectado | ✅ |
| RB-03 | Próxima actividad excluye canceladas/finalizadas | Estado no cancelado/finalizado | Verificado | ✅ |
| RB-04 | Identificar por código exacto | Actividad encontrada | Encontrada | ✅ |
| RB-04 | Varias actividades → pedir aclaración | 2 candidatas | 2 candidatas | ✅ |

---

## Cómo volver a ejecutar las pruebas

```powershell
.venv\Scripts\python -m pytest tests/ -v
```

**Resultado esperado:** 43 passed, 0 failed.
