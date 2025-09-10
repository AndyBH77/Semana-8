import json
import heapq
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
import time
import sys


class Libro:
    def __init__(self, libro_data: Dict[str, Any]):
        self.id = libro_data['id']
        self.titulo = libro_data['titulo']
        self.anio = libro_data['anio']
        self.popularidad = libro_data.get('popularidad', 0)
        self.recomendaciones = libro_data.get('recomendaciones', [])
        self.ejemplares_disponibles = libro_data.get('ejemplares_disponibles', 0)
        self.metadatos = libro_data.get('metadatos', {})

    def __lt__(self, other):
        return self.titulo < other.titulo


class Solicitud:
    def __init__(self, solicitud_data: Dict[str, Any]):
        self.id = solicitud_data['id']
        self.usuario_id = solicitud_data['usuario_id']
        self.libro_id = solicitud_data['libro_id']
        self.prioridad = solicitud_data['prioridad']
        self.timestamp = datetime.fromisoformat(solicitud_data['timestamp'].replace('Z', '+00:00'))
        self.tipo = solicitud_data.get('tipo', 'prestamo')
        self.procesada = False
        self.resultado = None

    def __lt__(self, other):
        if self.prioridad != other.prioridad:
            return self.prioridad < other.prioridad
        elif self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        else:
            return self.id < other.id


class SistemaBiblioteca:
    def __init__(self):
        self.catalogo: Dict[str, Libro] = {}  
        self.solicitudes_heap = [] 
        self.solicitudes_procesadas = []  
        self.libros_ordenados = [] 

    def cargar_catalogo(self, filename: str):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for libro_data in data.get('libros', []):
                libro = Libro(libro_data)
                self.catalogo[libro.id] = libro

            print(f"Catálogo cargado: {len(self.catalogo)} libros")

        except Exception as e:
            print(f"Error cargando catálogo: {e}")

    def cargar_solicitudes(self, filename: str):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for solicitud_data in data.get('solicitudes', []):
                if solicitud_data['libro_id'] in self.catalogo:
                    solicitud = Solicitud(solicitud_data)
                    heapq.heappush(self.solicitudes_heap, solicitud)
                else:
                    print(
                        f"Advertencia: Libro {solicitud_data['libro_id']} no encontrado para solicitud {solicitud_data['id']}")

            print(f"Solicitudes cargadas: {len(self.solicitudes_heap)}")

        except Exception as e:
            print(f"Error cargando solicitudes: {e}")

    def procesar_solicitudes(self):
        print("Procesando solicitudes...")
        procesadas = 0
        exitosas = 0

        while self.solicitudes_heap:
            solicitud = heapq.heappop(self.solicitudes_heap)
            libro = self.catalogo.get(solicitud.libro_id)

            if libro and libro.ejemplares_disponibles > 0:
                # Hay ejemplares disponibles
                libro.ejemplares_disponibles -= 1
                solicitud.resultado = "éxito"
                exitosas += 1
            else:
                # No hay ejemplares disponibles
                solicitud.resultado = "sin_ejemplares"

            solicitud.procesada = True
            self.solicitudes_procesadas.append(solicitud)
            procesadas += 1

            if procesadas % 1000 == 0:
                print(f"Procesadas {procesadas} solicitudes...")

        print(f"Procesamiento completado: {procesadas} solicitudes, {exitosas} exitosas")

    def obtener_recomendaciones(self, libro_id: str, profundidad_maxima: int = 3) -> List[str]:
        """Obtener recomendaciones recursivas para un libro"""
        if libro_id not in self.catalogo:
            return []

        recomendaciones = set()
        self._buscar_recomendaciones_recursivo(libro_id, recomendaciones, profundidad_maxima, 0)
        return list(recomendaciones)

    def _buscar_recomendaciones_recursivo(self, libro_id: str, recomendaciones: Set[str],
                                          profundidad_maxima: int, profundidad_actual: int):
        """Función recursiva auxiliar para buscar recomendaciones"""
        if profundidad_actual >= profundidad_maxima or libro_id not in self.catalogo:
            return

        libro = self.catalogo[libro_id]

        for recomendacion_id in libro.recomendaciones:
            if recomendacion_id not in recomendaciones and recomendacion_id in self.catalogo:
                recomendaciones.add(recomendacion_id)
                self._buscar_recomendaciones_recursivo(
                    recomendacion_id, recomendaciones, profundidad_maxima, profundidad_actual + 1
                )

    def ordenar_catalogo(self, criterio: str = 'titulo', algoritmo: str = 'quicksort'):
        """Ordenar el catálogo por el criterio y algoritmo especificados"""
        libros = list(self.catalogo.values())

        start_time = time.time()

        if algoritmo == 'quicksort':
            libros_ordenados = self.quicksort_iterativo(libros, criterio)
        elif algoritmo == 'mergesort':
            libros_ordenados = self.mergesort(libros, criterio)
        else:
            raise ValueError("Algoritmo no soportado")

        end_time = time.time()
        tiempo_ordenamiento = end_time - start_time

        self.libros_ordenados = libros_ordenados
        print(f"Catálogo ordenado por {criterio} usando {algoritmo} en {tiempo_ordenamiento:.4f} segundos")

        return libros_ordenados, tiempo_ordenamiento

    def quicksort_iterativo(self, arr: List[Any], criterio: str) -> List[Any]:
        """QuickSort iterativo para evitar límites de recursión"""
        if len(arr) <= 1:
            return arr

        stack = [(0, len(arr) - 1)]
        arr_copy = arr.copy()

        while stack:
            low, high = stack.pop()

            if low < high:
                pivot_index = self._partition(arr_copy, low, high, criterio)

                if pivot_index - 1 > low:
                    stack.append((low, pivot_index - 1))
                if pivot_index + 1 < high:
                    stack.append((pivot_index + 1, high))

        return arr_copy

    def _partition(self, arr: List[Any], low: int, high: int, criterio: str) -> int:
        """Función de partición para QuickSort"""
        pivot = arr[high]
        i = low - 1

        for j in range(low, high):
            if self._comparar_libros(arr[j], pivot, criterio) <= 0:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]

        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

    def mergesort(self, arr: List[Any], criterio: str) -> List[Any]:
        """MergeSort para ordenamiento estable"""
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left = self.mergesort(arr[:mid], criterio)
        right = self.mergesort(arr[mid:], criterio)

        return self._merge(left, right, criterio)

    def _merge(self, left: List[Any], right: List[Any], criterio: str) -> List[Any]:
        """Función de mezcla para MergeSort"""
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            if self._comparar_libros(left[i], right[j], criterio) <= 0:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def _comparar_libros(self, libro1: Libro, libro2: Libro, criterio: str) -> int:
        """Comparar dos libros según el criterio especificado"""
        if criterio == 'titulo':
            if libro1.titulo != libro2.titulo:
                return -1 if libro1.titulo < libro2.titulo else 1
            # Desempate por año si los títulos son iguales
            return libro1.anio - libro2.anio

        elif criterio == 'anio':
            if libro1.anio != libro2.anio:
                return libro1.anio - libro2.anio
            # Desempate por título si los años son iguales
            return -1 if libro1.titulo < libro2.titulo else 1

        else:
            raise ValueError("Criterio de ordenamiento no válido")

    def generar_reporte_solicitudes(self) -> List[Dict[str, Any]]:
        """Generar reporte de solicitudes procesadas"""
        reporte = []
        for solicitud in self.solicitudes_procesadas:
            reporte.append({
                'id_solicitud': solicitud.id,
                'prioridad': solicitud.prioridad,
                'timestamp': solicitud.timestamp.isoformat(),
                'libro_id': solicitud.libro_id,
                'resultado': solicitud.resultado,
                'usuario_id': solicitud.usuario_id,
                'tipo': solicitud.tipo
            })
        return reporte

    def generar_reporte_recomendaciones(self, libro_id: str, profundidad: int = 2) -> Dict[str, Any]:
        """Generar reporte de recomendaciones para un libro"""
        if libro_id not in self.catalogo:
            return {'error': 'Libro no encontrado'}

        recomendaciones = self.obtener_recomendaciones(libro_id, profundidad)

        return {
            'libro_origen': libro_id,
            'titulo_origen': self.catalogo[libro_id].titulo,
            'profundidad': profundidad,
            'recomendaciones': [
                {
                    'id': rec_id,
                    'titulo': self.catalogo[rec_id].titulo,
                    'anio': self.catalogo[rec_id].anio
                } for rec_id in recomendaciones
            ],
            'total_recomendaciones': len(recomendaciones)
        }

    def generar_reporte_catalogo_ordenado(self, max_libros: int = 50) -> List[Dict[str, Any]]:
        """Generar reporte del catálogo ordenado"""
        if not self.libros_ordenados:
            self.ordenar_catalogo('titulo', 'quicksort')

        return [
            {
                'id': libro.id,
                'titulo': libro.titulo,
                'anio': libro.anio,
                'ejemplares_disponibles': libro.ejemplares_disponibles
            } for libro in self.libros_ordenados[:max_libros]
        ]

    def guardar_reportes(self, prefijo_archivo: str = "reporte"):
        """Guardar todos los reportes en archivos JSON"""
        # Reporte de solicitudes
        with open(f"{prefijo_archivo}_solicitudes.json", 'w', encoding='utf-8') as f:
            json.dump(self.generar_reporte_solicitudes(), f, indent=2, ensure_ascii=False)

        # Reporte de catálogo ordenado
        with open(f"{prefijo_archivo}_catalogo.json", 'w', encoding='utf-8') as f:
            json.dump(self.generar_reporte_catalogo_ordenado(), f, indent=2, ensure_ascii=False)

        # Reporte de recomendaciones (para el primer libro del catálogo como ejemplo)
        if self.catalogo:
            primer_libro_id = next(iter(self.catalogo.keys()))
            with open(f"{prefijo_archivo}_recomendaciones.json", 'w', encoding='utf-8') as f:
                json.dump(self.generar_reporte_recomendaciones(primer_libro_id), f, indent=2, ensure_ascii=False)

        print(f"Reportes guardados con prefijo: {prefijo_archivo}")


# Función principal
def main():
    """Función principal para ejecutar el sistema de biblioteca"""
    sistema = SistemaBiblioteca()

    # Cargar datos
    sistema.cargar_catalogo('catalogo.json')
    sistema.cargar_solicitudes('solicitudes.json')

    # Procesar solicitudes
    sistema.procesar_solicitudes()

    # Ordenar catálogo con diferentes algoritmos y comparar
    print("\nComparando algoritmos de ordenamiento:")

    # QuickSort por título
    libros_quicksort, tiempo_quicksort = sistema.ordenar_catalogo('titulo', 'quicksort')

    # MergeSort por título
    libros_mergesort, tiempo_mergesort = sistema.ordenar_catalogo('titulo', 'mergesort')

    # QuickSort por año
    libros_quicksort_anio, tiempo_quicksort_anio = sistema.ordenar_catalogo('anio', 'quicksort')

    print(f"\nResultados de ordenamiento:")
    print(f"QuickSort (título): {tiempo_quicksort:.4f} segundos")
    print(f"MergeSort (título): {tiempo_mergesort:.4f} segundos")
    print(f"QuickSort (año): {tiempo_quicksort_anio:.4f} segundos")

    # Generar recomendaciones para algunos libros
    if sistema.catalogo:
        ejemplo_libro_id = next(iter(sistema.catalogo.keys()))
        recomendaciones = sistema.generar_reporte_recomendaciones(ejemplo_libro_id)
        print(f"\nRecomendaciones para '{sistema.catalogo[ejemplo_libro_id].titulo}':")
        print(f"Encontradas {recomendaciones['total_recomendaciones']} recomendaciones")

    # Guardar reportes
    sistema.guardar_reportes()

    # Análisis de complejidad
    print("\n" + "=" * 60)
    print("ANÁLISIS DE COMPLEJIDAD")
    print("=" * 60)
    print("1. Estructuras de datos:")
    print("   - Catálogo (diccionario): O(1) acceso por ID")
    print("   - Cola de prioridad (min-heap): O(log n) inserción/extracción")
    print()
    print("2. Algoritmos de ordenamiento:")
    print("   - QuickSort iterativo: O(n log n) promedio, O(n²) peor caso")
    print("   - MergeSort: O(n log n) en todos los casos, O(n) espacio")
    print()
    print("3. Búsqueda de recomendaciones:")
    print("   - Recorrido en profundidad: O(b^d) donde b es el factor de ramificación")
    print("   - Memoria: O(d) para la pila de recursión")
    print()
    print("4. Procesamiento de solicitudes:")
    print("   - Para n solicitudes: O(n log n) por la cola de prioridad")


if __name__ == "__main__":
    main()