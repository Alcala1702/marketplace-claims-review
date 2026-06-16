# Narrativa de hallazgos — Revisión de reclamos de un marketplace

> Datos **sintéticos**. El valor del análisis está en el método (generación de datos, modelado y narrativa), no en los datos en sí.

## El panorama

La operación procesa **204.656 casos** de reclamo entre enero y agosto de 2025, repartidos entre **32 representantes** y **9 países de Latinoamérica**, con un valor reclamado acumulado de **~117 M USD**. La base está limpia: sin nulos ni IDs duplicados, lista para analizar.

A primera vista la operación es sana: **88,7% de las gestiones se consideran buenas**, por encima del objetivo del 85%. Pero ese promedio esconde tres historias que vale la pena contar.

## 1. La calidad se deterioró… y se recuperó

El porcentaje de malas gestiones no es estable: **escala desde 7,7% en enero hasta un pico de 19,2% en abril**, el mes crítico, y luego **baja de forma sostenida hasta 6,5% en agosto**. Esa curva en forma de montaña es el corazón de la narrativa: hubo un problema creciente durante el primer cuatrimestre y una recuperación clara en el segundo. En una operación real, este patrón es justo lo que permitiría medir el impacto de una intervención (capacitación, cambio de proceso, refuerzo de personal).

## 2. No todos gestionan igual

La dispersión entre representantes es enorme: del **~4% de error en el mejor caso (`llopez`) al ~30% en el peor (`ttorres`)** — una diferencia de más de 7x. El promedio del equipo (~11%) oculta tanto a quienes sostienen la calidad como a quienes la arrastran. Es una señal directa de **dónde focalizar coaching** en lugar de aplicar medidas generales a todo el equipo.

## 3. El SLA es el termómetro de la calidad

El hallazgo más accionable: la calidad de la gestión está **perfectamente alineada con el tiempo de gestión (SLA)**. Una gestión es mala **si y solo si** el SLA cae en un extremo:

- **≤3 minutos** → gestión apresurada (no se revisó bien el caso).
- **≥18 minutos** → gestión demasiado lenta (atascada o mal manejada).

Los 23.027 casos con `eficiencia=0` coinciden **exactamente** con los 23.027 casos de SLA extremo: correspondencia uno a uno. El SLA medio de una gestión sana ronda los **9,3 minutos**. La implicación operativa es potente: **vigilar los extremos del SLA en tiempo real permitiría anticipar errores antes de la revisión de calidad**.

## 4. Restricciones: aplicar con criterio

En **~27% de los casos** se aplica una restricción a la cuenta (54.713 restricciones). De ellas, **el 8,2% se termina revirtiendo (rollback)** — es decir, se aplicaron y luego se quitaron. Por representante el rollback va de **5,3% a 13,8%**. Un rollback alto sugiere restricciones aplicadas con poco criterio: fricción innecesaria para el usuario y retrabajo para el equipo.

## 5. Riesgo y mix de reclamos

Alrededor del **34% de los casos se marca de alto riesgo (HIGH)**, una proporción estable que conviene monitorear por su carga operativa. El mix de reclamos está desbalanceado y dominado por **"producto no recibido" (~34%)**, seguido de producto diferente/defectuoso (~27%), devolución (~23%) y caja vacía (~16%). Los cruces país×producto y el SLA por canal (mayor en teléfono y en "producto no recibido") reflejan patrones operativos coherentes.

## Qué haría a continuación

1. **Alertas de SLA extremo** como señal temprana de mala gestión.
2. **Plan de coaching focalizado** en el cuartil de representantes con más error y más rollback.
3. **Revisar el criterio de restricciones** donde el rollback supera el 12%.
4. **Post-mortem de abril** para entender el deterioro y consolidar lo que funcionó en la recuperación.

---

*Recordatorio: dataset sintético, no apto para conclusiones del mundo real.*
