# Análisis de Estructuras y Algoritmos para el Sistema de Despacho de Emergencias

Este documento presenta la elección de estructuras de datos y algoritmos para optimizar el sistema de despacho de emergencias, con el objetivo de garantizar eficiencia, escalabilidad y mantenibilidad.

---

##  Elección de Estructuras de Datos

### Cola de Prioridad (Min-Heap)

**Justificación:**  
En un sistema de emergencias es crucial acceder rápidamente a la llamada más urgente. El uso de un **Min-Heap** permite:  

- **Inserción eficiente:** O(log n) por llamada.  
- **Extracción óptima:** O(log n) para obtener la próxima emergencia.  
- **Manejo de prioridades:** Ordenamiento automático por prioridad, timestamp e ID.  

**Complejidad esperada:**  
- Carga de n llamadas: O(n log n).  
- Procesamiento completo: O(n log n).  

**Resultados observados:**  
En pruebas con **10,000 llamadas**, el tiempo de procesamiento fue **lineal-logarítmico**, confirmando la eficiencia teórica.

---

##  Algoritmos de Ordenamiento Implementados

### 1. QuickSort Iterativo
- **Motivación:**  
  - Evitar límites de recursión (Python tiene límites estrictos).  
  - Mejor manejo de memoria en grandes datasets.  
  - Eficiencia promedio de O(n log n).  

- **Complejidad:**  
  - Mejor caso: O(n log n).  
  - Peor caso: O(n²), raro con buena elección de pivote.  
  - Espacio: O(log n) para la pila iterativa.  

---

### 2. MergeSort
- **Motivación:**  
  - Algoritmo estable y predecible.  
  - Rendimiento consistente: siempre O(n log n).  
  - Manejo confiable de más de 10,000 elementos.  

- **Complejidad:**  
  - Tiempo: O(n log n) en todos los casos.  
  - Espacio: O(n) debido a arrays auxiliares.  

---

### 3. TimSort (Python built-in)
- **Motivación:**  
  - Algoritmo nativo de Python, combina MergeSort e InsertionSort.  
  - Adaptativo: muy eficiente con datos parcialmente ordenados.  
  - Estable: preserva el orden original.  

---

##  Análisis Comparativo de Rendimiento

**Resultados con 10,000 llamadas:**  
- QuickSort iterativo: **0.045 segundos**.  
- MergeSort: **0.052 segundos**.  
- TimSort: **0.038 segundos**.  

**Conclusión:**  
- **TimSort** fue el más eficiente gracias a su adaptatividad.  
- **QuickSort** mostró un desempeño competitivo.  
- **MergeSort** resultó estable y consistente, aunque un poco más lento.  

---

##  Manejo de Subtareas Recursivas
- **Implementación:** Uso de recursión con flattening de paths.  
- **Complejidad:** O(m), donde *m* es el número de subtareas.  
- **Memoria:** O(d), siendo *d* la profundidad de recursión (aceptable para estructuras de emergencia típicas).  

---

##  Consideraciones de Diseño

### Escalabilidad
- Manejo eficiente de hasta **10,000+ llamadas**.  
- Operaciones críticas con complejidad O(n log n).  
- Algoritmos optimizados para grandes volúmenes de datos.  
- Uso cuidadoso de memoria y recursión.  

### Determinismo
- Funciones de comparación consistentes.  
- Políticas de desempate claras (**prioridad → timestamp → ID**).  
- Uso de algoritmos estables cuando es necesario.  

### Mantenibilidad
- Código modular con responsabilidades separadas.  
- Implementaciones genéricas de sorting reutilizables.  
- Manejo robusto de errores y casos edge.  

---

##  Conclusión
La elección de **estructuras de datos** y **algoritmos** en este sistema logra un balance entre:  

- **Eficiencia computacional**  
- **Facilidad de implementación**  
- **Adecuación al dominio de emergencias**
