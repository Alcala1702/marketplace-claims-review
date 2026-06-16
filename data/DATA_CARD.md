# Dataset Card — Marketplace Claims Review (synthetic)

## Resumen

Base **sintética** que simula la operación de revisión de reclamos de un marketplace / e-commerce en Latinoamérica. Cada registro es **un caso de reclamo** gestionado por un representante de soporte, con metadatos de riesgo, SLA, restricciones a la cuenta, producto, geografía, canal y una bandera de calidad de la gestión.

- **Filas:** 204.656
- **Columnas:** 23
- **Periodo:** enero–agosto 2025
- **Granularidad:** 1 fila = 1 caso de reclamo
- **Formato:** `casos.csv` (UTF-8 con BOM) + `gestion_operativa.xlsx` (7 dimensiones)
- **Licencia:** MIT (código) · dataset educativo
- **Idioma:** español

> ⚠️ **Datos 100% sintéticos.** Generados con Python/pandas/numpy. No representan a ninguna empresa ni persona real. **No usar para conclusiones del mundo real.**

---

## Contexto

El dataset fue creado como pieza de portafolio para demostrar generación de datos sintéticos realistas, modelado dimensional, análisis exploratorio y narrativa de datos sobre una operación típica de **revisión de reclamos / fraude / calidad** en e-commerce. Permite practicar análisis sobre una operación verosímil sin exponer información sensible.

---

## Columnas

| Columna | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `id_caso` | string | ID único de 10 caracteres | `30VXZW5CBU` |
| `fecha_de_creacion_caso` | datetime | Creación del caso (24h, con acumulación nocturna) | `2025-01-01 00:07:01` |
| `fecha_asignacion` | datetime | `fecha_cierre` − `sla_minutos` | `2025-01-01 11:48:23` |
| `fecha_cierre` | datetime | Cierre dentro de horario laboral (8:00–20:00) | `2025-01-01 11:55:05` |
| `id_representante` | string | Inicial + apellido | `zzamora` |
| `flag_riesgo` | int (0/1) | Caso de alto riesgo | `1` |
| `decision` | cat | `HIGH`/`LOW` (espejo de `flag_riesgo`) | `HIGH` |
| `fuente` | cat | `CX` / `Sin mediacion` | `CX` |
| `regla` | cat | `forward`/`return` × categoría | `return_Producto_no_recibido` |
| `tipo_reclamo` | cat | 4 categorías de reclamo | `Producto_no_recibido` |
| `restriccion` | int (0/1) | Restricción aplicada a la cuenta | `0` |
| `tipo_restriccion` | cat | 4 niveles (incl. `Sin restriccion`) | `15 dias sancion leve` |
| `rollback_restriccion` | int (0/1) | La restricción se revirtió | `0` |
| `producto_reclamado` | cat | 26 productos | `Laptop Lenovo` |
| `valor_producto_usd` | float | Valor del producto en USD | `685.5` |
| `dias_recepcion_a_reclamo` | int | Días entre recepción y reclamo | `3` |
| `sla_minutos` | float | Tiempo de gestión activa (min) | `6.7` |
| `tiempo_gestion_horas` | float | Tiempo total (reloj de pared); bimodal | `11.8` |
| `mes` | string | `YYYY-MM` | `2025-01` |
| `semana` | string | Semana ISO `YYYY-Sxx` | `2025-S01` |
| `pais_region` | cat | 9 países LATAM | `Chile` |
| `canal_contacto` | cat | 5 canales | `Web` |
| `eficiencia` | int (0/1) | **Calidad de la gestión: 1 = buena, 0 = mala** | `1` |

**Países:** Argentina, Brasil, Chile, Colombia, México, Panamá, Perú, Uruguay, Venezuela.
**Canales:** App móvil, Web, Teléfono, Email, Chat.

---

## Dimensiones (modelo estrella) — `gestion_operativa.xlsx`

`dim_representante`, `dim_calendario`, `dim_pais` (país→región), `dim_producto` (producto→categoría, rango de precio), `dim_tipo_reclamo` (+ código PNR/PDD/EB/DEVO), `dim_tipo_restriccion` (+ código y severidad), `dim_canal` (+ tipo digital/asistido).

---

## Cómo se generó

Datos generados programáticamente con Python (`pandas`, `numpy`) — ver `src/generar_datos.py`. Reglas de diseño incorporadas para dar realismo:

- **Productividad:** ≈ 8 casos cada 5 horas por representante → ~800 casos/rep/mes, operación casi continua.
- **Calidad objetivo:** ~88,7% de buena gestión (`eficiencia=1`).
- **Relación SLA–calidad:** las malas gestiones (`eficiencia=0`) corresponden **exactamente** a SLA extremo (≤3 min apresurado o ≥18 min lento).
- **Estacionalidad:** los errores escalan hasta abril y luego decrecen hasta agosto.
- **Cruces realistas:** distribución país×producto (más aires acondicionados en México/Brasil, electrónica premium en Chile/Argentina), estacionalidad climática, canal por país, SLA mayor en Teléfono y en "producto no recibido".
- **`tiempo_gestion_horas` bimodal:** grupo normal ~3,5 h en horario laboral (8:00–20:00) + acumulación nocturna ~15–16 h.
- **Reclamos desbalanceados:** PNR ~34% › PDD ~27% › Devolución ~23% › Caja vacía ~16%.

---

## Posibles preguntas de análisis

1. ¿Cómo evoluciona la calidad de gestión mes a mes y qué explica el pico de abril?
2. ¿Qué representantes necesitan coaching (alto % de error o rollback)?
3. ¿Sirve el SLA como señal temprana de mala gestión?
4. ¿Hay sesgos por país, producto o canal en el riesgo o en las restricciones?
5. ¿Las restricciones más severas tienen mayor o menor rollback?
6. Modelado: ¿se puede predecir `eficiencia` a partir de `sla_minutos`, canal, tipo de reclamo, etc.? (Nota: por diseño `eficiencia` está determinada por SLA extremo — útil como ejercicio didáctico de fuga de información / target leakage.)

---

## Limitaciones

- **Es sintético:** los patrones fueron impuestos por reglas de generación; **no reflejan comportamiento real** de clientes, representantes ni mercados.
- **Relaciones deterministas por diseño** (p. ej. SLA extremo ⟺ `eficiencia=0`): excelentes para enseñar EDA y storytelling, pero **no** para inferencia causal del mundo real.
- **No usar** para decisiones de negocio, benchmarking real ni entrenamiento de modelos productivos.
