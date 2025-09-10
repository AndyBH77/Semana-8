# Backend Biblioteca Digital

Este proyecto implementa un sistema de backend para una biblioteca digital que permite:

- Gestionar solicitudes de préstamos/lecturas con prioridad.
- Mantener inventario de ejemplares disponibles.
- Generar recomendaciones recursivas a partir de un libro.
- Ordenar el catálogo por título o por año, comparando QuickSort y MergeSort.
- Producir reportes en formato JSON.

---

## Requerimientos Funcionales

1. **Procesamiento de solicitudes**
   - Las solicitudes se manejan en una cola de prioridad (heap).
   - Reglas de desempate:
     - Menor prioridad numérica primero (1 = más alta).
     - Si hay empate en prioridad, se atiende la solicitud más antigua (menor timestamp).
     - Si todavía empatan, se ordena por `id` de la solicitud.
   - Se reduce el inventario (`ejemplares_disponibles`) al atender un préstamo.

2. **Recomendaciones**
   - Cada libro puede tener una lista de recomendaciones (`recomendaciones`).
   - Se realiza un recorrido recursivo en profundidad hasta una profundidad máxima configurable.

3. **Ordenamiento del catálogo**
   - Dos algoritmos implementados:
     - QuickSort (iterativo).
     - MergeSort (recursivo).
   - Permite ordenar por `titulo` o `anio`.
   - Se mide el tiempo de ejecución de cada algoritmo.

4. **Reportes generados**
   - Solicitudes procesadas (`*_solicitudes.json`).
   - Catálogo ordenado (`*_catalogo.json`).
   - Recomendaciones (`*_recomendaciones.json`).

---


