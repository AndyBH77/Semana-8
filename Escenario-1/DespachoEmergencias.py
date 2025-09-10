import json
import heapq
from datetime import datetime
from typing import List, Dict, Any, Optional
import time
import random
import sys


class LlamadaEmergencia:
    def __init__(self, datos_llamada: Dict[str, Any]):
        self.id = datos_llamada['id']
        self.timestamp = datetime.fromisoformat(datos_llamada['timestamp'].replace('Z', '+00:00'))
        self.prioridad = datos_llamada['prioridad']
        self.categoria = datos_llamada['categoria']
        self.ubicacion = datos_llamada['ubicacion']
        self.descripcion = datos_llamada.get('descripcion', '')
        self.subtareas = datos_llamada.get('subtareas', [])
        self.tiempo_estimado_respuesta = datos_llamada.get('tiempo_estimado_respuesta', 0)
        self.tiempo_despacho = None

    def __lt__(self, otro):
        if self.prioridad != otro.prioridad:
            return self.prioridad < otro.prioridad
        elif self.timestamp != otro.timestamp:
            return self.timestamp < otro.timestamp
        else:
            return self.id < otro.id

    def aplanar_subtareas(self, subtareas=None, ruta="") -> List[Dict[str, Any]]:
        """Aplana recursivamente todas las subtareas con sus rutas"""
        if subtareas is None:
            subtareas = self.subtareas

        aplanadas = []
        for i, subtarea in enumerate(subtareas):
            ruta_actual = f"{ruta}/{i}" if ruta else str(i)
            aplanadas.append({
                'tipo': subtarea['tipo'],
                'recurso_estimado': subtarea['recurso_estimado'],
                'ruta': ruta_actual
            })
            aplanadas.extend(self.aplanar_subtareas(subtarea.get('subtareas', []), ruta_actual))
        return aplanadas


class SistemaDespachoEmergencias:
    def __init__(self):
        self.cola_prioridad = []
        self.llamadas_despachadas = []
        self.registro = []

    def cargar_llamadas_desde_json(self, nombre_archivo: str):
        """Carga llamadas de emergencia desde archivo JSON"""
        try:
            with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
                datos = json.load(archivo)

            for datos_llamada in datos.get('llamadas', []):
                llamada = LlamadaEmergencia(datos_llamada)
                heapq.heappush(self.cola_prioridad, llamada)

            print(f"Cargadas {len(self.cola_prioridad)} llamadas de emergencia")

        except FileNotFoundError:
            print(f"Error: Archivo {nombre_archivo} no encontrado")
        except json.JSONDecodeError:
            print(f"Error: Formato JSON inválido en {nombre_archivo}")
        except KeyError as e:
            print(f"Error: Campo requerido {e} faltante en datos JSON")
        except Exception as e:
            print(f"Error inesperado cargando llamadas: {e}")

    def despachar_siguiente_emergencia(self) -> Optional[LlamadaEmergencia]:
        """Despacha la llamada de emergencia de mayor prioridad"""
        if not self.cola_prioridad:
            return None

        llamada = heapq.heappop(self.cola_prioridad)
        llamada.tiempo_despacho = datetime.now()
        self.llamadas_despachadas.append(llamada)

        entrada_registro = {
            'id': llamada.id,
            'prioridad': llamada.prioridad,
            'hora_despacho': llamada.tiempo_despacho.isoformat(),
            'categoria': llamada.categoria,
            'ubicacion': llamada.ubicacion
        }
        self.registro.append(entrada_registro)

        print(f"Despachada: {llamada.id} (Prioridad: {llamada.prioridad}, Categoría: {llamada.categoria})")
        return llamada

    def procesar_todas_llamadas(self):
        """Procesa todas las llamadas en la cola de prioridad"""
        print("Iniciando procesamiento de despacho de emergencias...")
        tiempo_inicio = time.time()

        contador_despachos = 0
        while self.cola_prioridad:
            self.despachar_siguiente_emergencia()
            contador_despachos += 1

        tiempo_fin = time.time()
        print(f"Procesadas {contador_despachos} llamadas de emergencia en {tiempo_fin - tiempo_inicio:.4f} segundos")

    def generar_reporte(self, algoritmo_ordenamiento: str = 'quicksort'):
        """Genera reporte final con algoritmo de ordenamiento especificado"""
        if not self.llamadas_despachadas:
            print("No se han despachado llamadas aún")
            return [], 0

        llamadas_a_ordenar = self.llamadas_despachadas.copy()

        tiempo_inicio = time.time()

        if algoritmo_ordenamiento == 'quicksort':
            limite_recursion_original = sys.getrecursionlimit()
            if len(llamadas_a_ordenar) > 1000:
                sys.setrecursionlimit(10000)

            llamadas_ordenadas = self.quicksort_iterativo(llamadas_a_ordenar)

            if len(llamadas_a_ordenar) > 1000:
                sys.setrecursionlimit(limite_recursion_original)

        elif algoritmo_ordenamiento == 'mergesort':
            llamadas_ordenadas = self.mergesort(llamadas_a_ordenar)
        elif algoritmo_ordenamiento == 'timsort':
            llamadas_ordenadas = sorted(llamadas_a_ordenar, key=self._clave_ordenamiento_llamada)
        else:
            raise ValueError("Algoritmo de ordenamiento no soportado")

        tiempo_fin = time.time()
        tiempo_ordenamiento = tiempo_fin - tiempo_inicio

        reporte = []
        for llamada in llamadas_ordenadas:
            subtareas_aplanadas = llamada.aplanar_subtareas()
            reporte.append({
                'id': llamada.id,
                'prioridad': llamada.prioridad,
                'timestamp': llamada.timestamp.isoformat(),
                'tiempo_estimado_respuesta': llamada.tiempo_estimado_respuesta,
                'categoria': llamada.categoria,
                'ubicacion': llamada.ubicacion,
                'descripcion': llamada.descripcion,
                'subtareas_aplanadas': subtareas_aplanadas,
                'total_subtareas': len(subtareas_aplanadas),
                'hora_despacho': llamada.tiempo_despacho.isoformat() if llamada.tiempo_despacho else None
            })

        print(f"Reporte generado con {len(reporte)} llamadas ordenadas por {algoritmo_ordenamiento} en {tiempo_ordenamiento:.6f} segundos")
        return reporte, tiempo_ordenamiento

    def _clave_ordenamiento_llamada(self, llamada: LlamadaEmergencia) -> tuple:
        """Función clave para ordenar llamadas"""
        return (
            llamada.tiempo_estimado_respuesta,
            llamada.prioridad,
            llamada.timestamp,
            llamada.id
        )

    def quicksort_iterativo(self, arr: List[LlamadaEmergencia]) -> List[LlamadaEmergencia]:
        """Implementación iterativa de QuickSort para evitar límites de recursión"""
        if len(arr) <= 1:
            return arr

        pila = [(0, len(arr) - 1)]
        copia_arr = arr.copy()

        while pila:
            bajo, alto = pila.pop()

            if bajo < alto:
                indice_pivote = self._particion(copia_arr, bajo, alto)

                if indice_pivote - 1 > bajo:
                    pila.append((bajo, indice_pivote - 1))
                if indice_pivote + 1 < alto:
                    pila.append((indice_pivote + 1, alto))

        return copia_arr

    def _particion(self, arr: List[LlamadaEmergencia], bajo: int, alto: int) -> int:
        """Función de partición para QuickSort"""
        pivote = arr[alto]
        i = bajo - 1

        for j in range(bajo, alto):
            if self._comparar_llamadas(arr[j], pivote) <= 0:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]

        arr[i + 1], arr[alto] = arr[alto], arr[i + 1]
        return i + 1

    def mergesort(self, arr: List[LlamadaEmergencia]) -> List[LlamadaEmergencia]:
        """Implementación de MergeSort para llamadas de emergencia"""
        if len(arr) <= 1:
            return arr

        medio = len(arr) // 2
        izquierda = self.mergesort(arr[:medio])
        derecha = self.mergesort(arr[medio:])

        return self._fusionar(izquierda, derecha)

    def _fusionar(self, izquierda: List[LlamadaEmergencia], derecha: List[LlamadaEmergencia]) -> List[LlamadaEmergencia]:
        """Fusiona dos listas ordenadas de llamadas de emergencia"""
        resultado = []
        i = j = 0

        while i < len(izquierda) and j < len(derecha):
            if self._comparar_llamadas(izquierda[i], derecha[j]) <= 0:
                resultado.append(izquierda[i])
                i += 1
            else:
                resultado.append(derecha[j])
                j += 1

        resultado.extend(izquierda[i:])
        resultado.extend(derecha[j:])
        return resultado

    def _comparar_llamadas(self, llamada1: LlamadaEmergencia, llamada2: LlamadaEmergencia) -> int:
        """Compara dos llamadas para ordenamiento (por tiempo estimado de respuesta, luego prioridad, luego timestamp, luego ID)"""
        if llamada1.tiempo_estimado_respuesta != llamada2.tiempo_estimado_respuesta:
            return llamada1.tiempo_estimado_respuesta - llamada2.tiempo_estimado_respuesta

        if llamada1.prioridad != llamada2.prioridad:
            return llamada1.prioridad - llamada2.prioridad

        if llamada1.timestamp != llamada2.timestamp:
            return -1 if llamada1.timestamp < llamada2.timestamp else 1

        return -1 if llamada1.id < llamada2.id else 1

    def guardar_reporte_json(self, reporte: List[Dict[str, Any]], nombre_archivo: str):
        """Guarda el reporte en un archivo JSON"""
        try:
            with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
                json.dump({
                    'total_llamadas': len(reporte),
                    'fecha_generacion': datetime.now().isoformat(),
                    'llamadas_atendidas': reporte
                }, archivo, indent=2, ensure_ascii=False, default=str)
            print(f"Reporte guardado en {nombre_archivo}")
        except IOError as e:
            print(f"Error guardando reporte: {e}")

    def imprimir_registro(self):
        """Imprime el registro de despachos"""
        print("\nRegistro de Despachos:")
        print("-" * 100)
        for entrada in self.registro:
            print(f"ID: {entrada['id']:12} | Prioridad: {entrada['prioridad']} | "
                  f"Categoría: {entrada['categoria']:15} | Ubicación: {entrada['ubicacion']:15} | "
                  f"Hora Despacho: {entrada['hora_despacho']}")


def main():
    """Función principal para ejecutar el sistema de despacho de emergencias"""
    sistema = SistemaDespachoEmergencias()

    sistema.cargar_llamadas_desde_json('calls.json')

    sistema.procesar_todas_llamadas()

    print("\nGenerando reportes...")

    try:
        reporte_quicksort, tiempo_quicksort = sistema.generar_reporte('quicksort')
        sistema.guardar_reporte_json(reporte_quicksort, 'emergency_report_quicksort.json')
    except Exception as e:
        print(f"Error con QuickSort: {e}")

    try:
        reporte_mergesort, tiempo_mergesort = sistema.generar_reporte('mergesort')
        sistema.guardar_reporte_json(reporte_mergesort, 'emergency_report_mergesort.json')
    except Exception as e:
        print(f"Error con MergeSort: {e}")

    try:
        reporte_timsort, tiempo_timsort = sistema.generar_reporte('timsort')
        sistema.guardar_reporte_json(reporte_timsort, 'emergency_report_timsort.json')

        print(f"\nComparación de Rendimiento de Ordenamiento:")
        print(f"QuickSort (iterativo): {tiempo_quicksort:.6f} segundos")
        print(f"MergeSort: {tiempo_mergesort:.6f} segundos")
        print(f"TimSort (integrado): {tiempo_timsort:.6f} segundos")

    except Exception as e:
        print(f"Error con TimSort: {e}")

    sistema.imprimir_registro()

    print("\n" + "=" * 100)
    print("ANÁLISIS DE COMPLEJIDAD")
    print("=" * 100)
    print("1. Operaciones de Cola de Prioridad:")
    print("   - Inserción (heapq.heappush): O(log n)")
    print("   - Extracción (heapq.heappop): O(log n)")
    print("   - Total para n llamadas: O(n log n)")
    print()
    print("2. Algoritmos de Ordenamiento:")
    print("   - QuickSort (iterativo): Promedio O(n log n), Peor caso O(n²)")
    print("   - MergeSort: Siempre O(n log n), estable, espacio O(n)")
    print("   - TimSort (integrado en Python): O(n log n), adaptativo, estable")
    print()
    print("3. Aplanamiento de Subtareas:")
    print("   - Recorrido recursivo: O(m) donde m es el total de subtareas")
    print()
    print("4. Complejidad de Espacio:")
    print("   - Cola de Prioridad: O(n)")
    print("   - Almacenamiento de llamadas despachadas: O(n)")
    print("   - Ordenamiento: O(n) para MergeSort, O(log n) pila para QuickSort iterativo")


if __name__ == "__main__":
    main()