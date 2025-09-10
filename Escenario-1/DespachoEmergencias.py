import json
import heapq
from datetime import datetime
from typing import List, Dict, Any, Optional
import time
import random
import sys


class EmergencyCall:
    def __init__(self, call_data: Dict[str, Any]):
        self.id = call_data['id']
        self.timestamp = datetime.fromisoformat(call_data['timestamp'].replace('Z', '+00:00'))
        self.prioridad = call_data['prioridad']
        self.categoria = call_data['categoria']
        self.ubicacion = call_data['ubicacion']
        self.descripcion = call_data.get('descripcion', '')
        self.subtareas = call_data.get('subtareas', [])
        self.tiempo_estimado_respuesta = call_data.get('tiempo_estimado_respuesta', 0)
        self.dispatch_time = None

    def __lt__(self, other):
        # Priority comparison for heap (lower priority number = higher priority)
        if self.prioridad != other.prioridad:
            return self.prioridad < other.prioridad
        elif self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        else:
            return self.id < other.id

    def flatten_subtasks(self, subtasks=None, path="") -> List[Dict[str, Any]]:
        """Recursively flatten all subtasks with their paths"""
        if subtasks is None:
            subtasks = self.subtareas

        flattened = []
        for i, subtask in enumerate(subtasks):
            current_path = f"{path}/{i}" if path else str(i)
            flattened.append({
                'tipo': subtask['tipo'],
                'recurso_estimado': subtask['recurso_estimado'],
                'path': current_path
            })
            # Recursively process nested subtasks
            flattened.extend(self.flatten_subtasks(subtask.get('subtareas', []), current_path))
        return flattened


class EmergencyDispatchSystem:
    def __init__(self):
        self.priority_queue = []
        self.dispatched_calls = []
        self.log = []

    def load_calls_from_json(self, filename: str):
        """Load emergency calls from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for call_data in data.get('llamadas', []):
                call = EmergencyCall(call_data)
                heapq.heappush(self.priority_queue, call)

            print(f"Loaded {len(self.priority_queue)} emergency calls")

        except FileNotFoundError:
            print(f"Error: File {filename} not found")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {filename}")
        except KeyError as e:
            print(f"Error: Missing required field {e} in JSON data")
        except Exception as e:
            print(f"Unexpected error loading calls: {e}")

    def dispatch_next_emergency(self) -> Optional[EmergencyCall]:
        """Dispatch the highest priority emergency call"""
        if not self.priority_queue:
            return None

        call = heapq.heappop(self.priority_queue)
        call.dispatch_time = datetime.now()
        self.dispatched_calls.append(call)

        # Log the dispatch decision
        log_entry = {
            'id': call.id,
            'prioridad': call.prioridad,
            'hora_despacho': call.dispatch_time.isoformat(),
            'categoria': call.categoria,
            'ubicacion': call.ubicacion
        }
        self.log.append(log_entry)

        print(f"Dispatched: {call.id} (Priority: {call.prioridad}, Category: {call.categoria})")
        return call

    def process_all_calls(self):
        """Process all calls in the priority queue"""
        print("Starting emergency dispatch processing...")
        start_time = time.time()

        dispatch_count = 0
        while self.priority_queue:
            self.dispatch_next_emergency()
            dispatch_count += 1

        end_time = time.time()
        print(f"Processed {dispatch_count} emergency calls in {end_time - start_time:.4f} seconds")

    def generate_report(self, sort_algorithm: str = 'quicksort'):
        """Generate final report with specified sorting algorithm"""
        if not self.dispatched_calls:
            print("No calls have been dispatched yet")
            return [], 0

        # Copy the list to avoid modifying the original
        calls_to_sort = self.dispatched_calls.copy()

        # Measure sorting performance
        start_time = time.time()

        if sort_algorithm == 'quicksort':
            # Increase recursion limit for large datasets
            original_recursion_limit = sys.getrecursionlimit()
            if len(calls_to_sort) > 1000:
                sys.setrecursionlimit(10000)

            sorted_calls = self.quicksort_iterative(calls_to_sort)

            if len(calls_to_sort) > 1000:
                sys.setrecursionlimit(original_recursion_limit)

        elif sort_algorithm == 'mergesort':
            sorted_calls = self.mergesort(calls_to_sort)
        elif sort_algorithm == 'timsort':
            # Use Python's built-in sorted with our custom key
            sorted_calls = sorted(calls_to_sort, key=self._call_sort_key)
        else:
            raise ValueError("Unsupported sorting algorithm")

        end_time = time.time()
        sort_time = end_time - start_time

        # Generate report data
        report = []
        for call in sorted_calls:
            flattened_subtasks = call.flatten_subtasks()
            report.append({
                'id': call.id,
                'prioridad': call.prioridad,
                'timestamp': call.timestamp.isoformat(),
                'tiempo_estimado_respuesta': call.tiempo_estimado_respuesta,
                'categoria': call.categoria,
                'ubicacion': call.ubicacion,
                'descripcion': call.descripcion,
                'subtareas_flattened': flattened_subtasks,
                'total_subtareas': len(flattened_subtasks),
                'hora_despacho': call.dispatch_time.isoformat() if call.dispatch_time else None
            })

        print(f"Generated report with {len(report)} calls sorted by {sort_algorithm} in {sort_time:.6f} seconds")
        return report, sort_time

    def _call_sort_key(self, call: EmergencyCall) -> tuple:
        """Key function for sorting calls"""
        return (
            call.tiempo_estimado_respuesta,
            call.prioridad,
            call.timestamp,
            call.id
        )

    def quicksort_iterative(self, arr: List[EmergencyCall]) -> List[EmergencyCall]:
        """Iterative QuickSort implementation to avoid recursion limits"""
        if len(arr) <= 1:
            return arr

        stack = [(0, len(arr) - 1)]
        arr_copy = arr.copy()

        while stack:
            low, high = stack.pop()

            if low < high:
                pivot_index = self._partition(arr_copy, low, high)

                # Push left and right subarrays to stack
                if pivot_index - 1 > low:
                    stack.append((low, pivot_index - 1))
                if pivot_index + 1 < high:
                    stack.append((pivot_index + 1, high))

        return arr_copy

    def _partition(self, arr: List[EmergencyCall], low: int, high: int) -> int:
        """Partition function for QuickSort"""
        pivot = arr[high]
        i = low - 1

        for j in range(low, high):
            if self._call_compare(arr[j], pivot) <= 0:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]

        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

    def mergesort(self, arr: List[EmergencyCall]) -> List[EmergencyCall]:
        """MergeSort implementation for emergency calls"""
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left = self.mergesort(arr[:mid])
        right = self.mergesort(arr[mid:])

        return self._merge(left, right)

    def _merge(self, left: List[EmergencyCall], right: List[EmergencyCall]) -> List[EmergencyCall]:
        """Merge two sorted lists of emergency calls"""
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            if self._call_compare(left[i], right[j]) <= 0:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def _call_compare(self, call1: EmergencyCall, call2: EmergencyCall) -> int:
        """Compare two calls for sorting (by estimated response time, then priority, then timestamp, then ID)"""
        # Compare tiempo_estimado_respuesta
        if call1.tiempo_estimado_respuesta != call2.tiempo_estimado_respuesta:
            return call1.tiempo_estimado_respuesta - call2.tiempo_estimado_respuesta

        # Compare prioridad
        if call1.prioridad != call2.prioridad:
            return call1.prioridad - call2.prioridad

        # Compare timestamp
        if call1.timestamp != call2.timestamp:
            return -1 if call1.timestamp < call2.timestamp else 1

        # Compare ID as last resort
        return -1 if call1.id < call2.id else 1

    def save_report_to_json(self, report: List[Dict[str, Any]], filename: str):
        """Save the report to a JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump({
                    'total_llamadas': len(report),
                    'fecha_generacion': datetime.now().isoformat(),
                    'llamadas_atendidas': report
                }, file, indent=2, ensure_ascii=False, default=str)
            print(f"Report saved to {filename}")
        except IOError as e:
            print(f"Error saving report: {e}")

    def print_log(self):
        """Print the dispatch log"""
        print("\nDispatch Log:")
        print("-" * 100)
        for entry in self.log:
            print(f"ID: {entry['id']:12} | Priority: {entry['prioridad']} | "
                  f"Category: {entry['categoria']:15} | Location: {entry['ubicacion']:15} | "
                  f"Dispatch Time: {entry['hora_despacho']}")


def main():
    """Main function to run the emergency dispatch system"""
    # Initialize the system
    system = EmergencyDispatchSystem()

    # Load emergency calls
    system.load_calls_from_json('calls.json')

    # Process all calls
    system.process_all_calls()

    # Generate reports with different sorting algorithms
    print("\nGenerating reports...")

    try:
        # QuickSort report (iterative version)
        quicksort_report, quicksort_time = system.generate_report('quicksort')
        system.save_report_to_json(quicksort_report, 'emergency_report_quicksort.json')
    except Exception as e:
        print(f"Error with QuickSort: {e}")

    try:
        # MergeSort report
        mergesort_report, mergesort_time = system.generate_report('mergesort')
        system.save_report_to_json(mergesort_report, 'emergency_report_mergesort.json')
    except Exception as e:
        print(f"Error with MergeSort: {e}")

    try:
        # TimSort (Python's built-in) report
        timsort_report, timsort_time = system.generate_report('timsort')
        system.save_report_to_json(timsort_report, 'emergency_report_timsort.json')

        # Print performance comparison
        print(f"\nSorting Performance Comparison:")
        print(f"QuickSort (iterative): {quicksort_time:.6f} seconds")
        print(f"MergeSort: {mergesort_time:.6f} seconds")
        print(f"TimSort (built-in): {timsort_time:.6f} seconds")

    except Exception as e:
        print(f"Error with TimSort: {e}")

    # Print dispatch log
    system.print_log()

    # Complexity analysis
    print("\n" + "=" * 100)
    print("COMPLEXITY ANALYSIS")
    print("=" * 100)
    print("1. Priority Queue Operations:")
    print("   - Insertion (heapq.heappush): O(log n)")
    print("   - Extraction (heapq.heappop): O(log n)")
    print("   - Total for n calls: O(n log n)")
    print()
    print("2. Sorting Algorithms:")
    print("   - QuickSort (iterative): Average O(n log n), Worst O(n²)")
    print("   - MergeSort: Always O(n log n), stable, O(n) space")
    print("   - TimSort (Python built-in): O(n log n), adaptive, stable")
    print()
    print("3. Subtask Flattening:")
    print("   - Recursive traversal: O(m) where m is total subtasks")
    print()
    print("4. Space Complexity:")
    print("   - Priority Queue: O(n)")
    print("   - Dispatched calls storage: O(n)")
    print("   - Sorting: O(n) for MergeSort, O(log n) stack for iterative QuickSort")


if __name__ == "__main__":
    main()

