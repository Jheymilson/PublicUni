import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
from enum import Enum

class AlgoritmoType(Enum):
    """Enumeración de tipos de algoritmos de planificación"""
    FIFO = "FIFO"
    SJF = "SJF"
    ROUND_ROBIN = "Round Robin"
    PRIORIDAD = "Prioridad"

def clear_screen():
    """Función para limpiar la pantalla"""
    print("\n" * 50)

class PlanificadorCompleto:
    def __init__(self, quantum=3):
        """
        Inicializa el planificador con soporte para múltiples algoritmos
        
        Args:
            quantum (int): Quantum para Round Robin
        """
        self.quantum = quantum
        self.processes = pd.DataFrame()
        self.current_time = 0
        self.execution_sequence = []
        self.gantt_data = []
        self.waiting_times = {}
        self.turnaround_times = {}
        self.response_times = {}
        
    def add_process(self, process_id, arrival_time, burst_time, priority=0):
        """
        Agrega un proceso al planificador
        
        Args:
            process_id (str): ID del proceso
            arrival_time (int): Tiempo de llegada
            burst_time (int): Tiempo de CPU requerido
            priority (int): Prioridad (menor número = mayor prioridad)
        """
        new_process = pd.DataFrame({
            'process_id': [process_id],
            'arrival_time': [arrival_time],
            'burst_time': [burst_time],
            'priority': [priority],
            'remaining_time': [burst_time],
            'completion_time': [0],
            'waiting_time': [0],
            'turnaround_time': [0],
            'response_time': [0],
            'first_response': [-1],
            'state': ['NEW']
        })
        
        self.processes = pd.concat([self.processes, new_process], ignore_index=True)
        self.processes = self.processes.sort_values(['arrival_time', 'process_id']).reset_index(drop=True)
    
    def reset_simulation(self):
        """Reinicia las variables para una nueva simulación"""
        self.current_time = 0
        self.execution_sequence = []
        self.gantt_data = []
        self.waiting_times = {}
        self.turnaround_times = {}
        self.response_times = {}
        
        # Reiniciar estados de procesos
        self.processes['remaining_time'] = self.processes['burst_time']
        self.processes['completion_time'] = 0
        self.processes['waiting_time'] = 0
        self.processes['turnaround_time'] = 0
        self.processes['response_time'] = 0
        self.processes['first_response'] = -1
        self.processes['state'] = 'NEW'
    
    def simulate_fifo(self):
        """
        Simula el algoritmo FIFO (First In, First Out)
        También conocido como FCFS (First Come, First Served)
        """
        self.reset_simulation()
        print("🔄 Ejecutando algoritmo FIFO (First In, First Out)...")
        
        # Ordenar procesos por tiempo de llegada
        processes_sorted = self.processes.sort_values(['arrival_time', 'process_id']).copy()
        
        for _, process in processes_sorted.iterrows():
            process_id = process['process_id']
            arrival_time = process['arrival_time']
            burst_time = process['burst_time']
            
            # Si el proceso llega después del tiempo actual, esperar
            if arrival_time > self.current_time:
                # Tiempo ocioso
                if arrival_time > self.current_time:
                    self.gantt_data.append({
                        'process': 'IDLE',
                        'start': self.current_time,
                        'end': arrival_time
                    })
                self.current_time = arrival_time
            
            # Registrar tiempo de respuesta (primera vez que se ejecuta)
            idx = self.processes[self.processes['process_id'] == process_id].index[0]
            response_time = self.current_time - arrival_time
            self.processes.loc[idx, 'response_time'] = response_time
            self.processes.loc[idx, 'first_response'] = self.current_time
            
            # Ejecutar el proceso completo
            start_time = self.current_time
            end_time = self.current_time + burst_time
            
            self.execution_sequence.append((process_id, start_time, end_time))
            self.gantt_data.append({
                'process': process_id,
                'start': start_time,
                'end': end_time
            })
            
            # Actualizar tiempos
            self.current_time = end_time
            completion_time = end_time
            turnaround_time = completion_time - arrival_time
            waiting_time = turnaround_time - burst_time
            
            # Guardar métricas
            self.processes.loc[idx, 'completion_time'] = completion_time
            self.processes.loc[idx, 'turnaround_time'] = turnaround_time
            self.processes.loc[idx, 'waiting_time'] = waiting_time
            self.processes.loc[idx, 'state'] = 'TERMINATED'
        
        return self._calculate_averages()
    
    def simulate_sjf(self):
        """
        Simula el algoritmo SJF (Shortest Job First)
        Versión no preemptiva
        """
        self.reset_simulation()
        print("⚡ Ejecutando algoritmo SJF (Shortest Job First)...")
        
        completed_processes = set()
        
        while len(completed_processes) < len(self.processes):
            # Obtener procesos disponibles (que han llegado y no están completados)
            available_processes = self.processes[
                (self.processes['arrival_time'] <= self.current_time) & 
                (~self.processes['process_id'].isin(completed_processes))
            ].copy()
            
            if available_processes.empty:
                # No hay procesos disponibles, avanzar al siguiente arrival_time
                next_arrival = self.processes[
                    ~self.processes['process_id'].isin(completed_processes)
                ]['arrival_time'].min()
                
                if next_arrival > self.current_time:
                    self.gantt_data.append({
                        'process': 'IDLE',
                        'start': self.current_time,
                        'end': next_arrival
                    })
                    self.current_time = next_arrival
                continue
            
            # Seleccionar el proceso con menor burst_time (SJF)
            selected_process = available_processes.loc[available_processes['burst_time'].idxmin()]
            process_id = selected_process['process_id']
            arrival_time = selected_process['arrival_time']
            burst_time = selected_process['burst_time']
            
            # Registrar tiempo de respuesta
            idx = self.processes[self.processes['process_id'] == process_id].index[0]
            response_time = self.current_time - arrival_time
            self.processes.loc[idx, 'response_time'] = response_time
            self.processes.loc[idx, 'first_response'] = self.current_time
            
            # Ejecutar el proceso completo
            start_time = self.current_time
            end_time = self.current_time + burst_time
            
            self.execution_sequence.append((process_id, start_time, end_time))
            self.gantt_data.append({
                'process': process_id,
                'start': start_time,
                'end': end_time
            })
            
            # Actualizar tiempos
            self.current_time = end_time
            completion_time = end_time
            turnaround_time = completion_time - arrival_time
            waiting_time = turnaround_time - burst_time
            
            # Guardar métricas
            self.processes.loc[idx, 'completion_time'] = completion_time
            self.processes.loc[idx, 'turnaround_time'] = turnaround_time
            self.processes.loc[idx, 'waiting_time'] = waiting_time
            self.processes.loc[idx, 'state'] = 'TERMINATED'
            
            completed_processes.add(process_id)
        
        return self._calculate_averages()
    
    def simulate_round_robin(self):
        """
        Simula el algoritmo Round Robin
        """
        self.reset_simulation()
        print(f"🔄 Ejecutando algoritmo Round Robin (Quantum = {self.quantum})...")
        
        ready_queue = []
        
        # Función auxiliar para agregar procesos que han llegado
        def add_arrived_processes():
            for i, row in self.processes.iterrows():
                if (row['arrival_time'] <= self.current_time and 
                    row['remaining_time'] > 0 and 
                    row['process_id'] not in ready_queue and 
                    row['state'] != 'TERMINATED'):
                    
                    ready_queue.append(row['process_id'])
                    if self.processes.loc[i, 'state'] == 'NEW':
                        self.processes.loc[i, 'state'] = 'READY'
        
        # Agregar procesos que ya han llegado al tiempo 0
        add_arrived_processes()
        
        while True:
            # Si la cola está vacía pero hay procesos que no han llegado
            if not ready_queue and self.processes[self.processes['remaining_time'] > 0].shape[0] > 0:
                next_arrival = self.processes[
                    (self.processes['remaining_time'] > 0) & 
                    (self.processes['arrival_time'] > self.current_time)
                ]['arrival_time'].min()
                
                # Tiempo ocioso
                if next_arrival > self.current_time:
                    self.gantt_data.append({
                        'process': 'IDLE',
                        'start': self.current_time,
                        'end': next_arrival
                    })
                    self.current_time = next_arrival
                
                add_arrived_processes()
                continue
            
            # Si no hay más procesos
            if not ready_queue:
                break
            
            # Obtener el siguiente proceso (FIFO en la cola)
            current_process_id = ready_queue.pop(0)
            current_process_idx = self.processes[self.processes['process_id'] == current_process_id].index[0]
            
            # Registrar primera respuesta
            if self.processes.loc[current_process_idx, 'first_response'] == -1:
                arrival_time = self.processes.loc[current_process_idx, 'arrival_time']
                response_time = self.current_time - arrival_time
                self.processes.loc[current_process_idx, 'first_response'] = self.current_time
                self.processes.loc[current_process_idx, 'response_time'] = response_time
            
            # Determinar tiempo de ejecución
            remaining = self.processes.loc[current_process_idx, 'remaining_time']
            execution_time = min(self.quantum, remaining)
            
            # Ejecutar
            start_time = self.current_time
            end_time = self.current_time + execution_time
            
            self.execution_sequence.append((current_process_id, start_time, end_time))
            self.gantt_data.append({
                'process': current_process_id,
                'start': start_time,
                'end': end_time
            })
            
            # Actualizar tiempo y remaining_time
            self.current_time = end_time
            new_remaining = remaining - execution_time
            self.processes.loc[current_process_idx, 'remaining_time'] = new_remaining
            
            # Agregar procesos que llegaron durante la ejecución
            add_arrived_processes()
            
            # Si el proceso terminó
            if new_remaining == 0:
                arrival_time = self.processes.loc[current_process_idx, 'arrival_time']
                burst_time = self.processes.loc[current_process_idx, 'burst_time']
                completion_time = self.current_time
                turnaround_time = completion_time - arrival_time
                waiting_time = turnaround_time - burst_time
                
                self.processes.loc[current_process_idx, 'completion_time'] = completion_time
                self.processes.loc[current_process_idx, 'turnaround_time'] = turnaround_time
                self.processes.loc[current_process_idx, 'waiting_time'] = waiting_time
                self.processes.loc[current_process_idx, 'state'] = 'TERMINATED'
            else:
                # El proceso vuelve al final de la cola
                ready_queue.append(current_process_id)
        
        return self._calculate_averages()
    
    def simulate_priority(self):
        """
        Simula el algoritmo de Prioridades (no preemptivo)
        Menor número = mayor prioridad
        """
        self.reset_simulation()
        print("⭐ Ejecutando algoritmo de Prioridades...")
        
        completed_processes = set()
        
        while len(completed_processes) < len(self.processes):
            # Obtener procesos disponibles
            available_processes = self.processes[
                (self.processes['arrival_time'] <= self.current_time) & 
                (~self.processes['process_id'].isin(completed_processes))
            ].copy()
            
            if available_processes.empty:
                # No hay procesos disponibles
                next_arrival = self.processes[
                    ~self.processes['process_id'].isin(completed_processes)
                ]['arrival_time'].min()
                
                if next_arrival > self.current_time:
                    self.gantt_data.append({
                        'process': 'IDLE',
                        'start': self.current_time,
                        'end': next_arrival
                    })
                    self.current_time = next_arrival
                continue
            
            # Seleccionar proceso con mayor prioridad (menor número)
            # En caso de empate, usar arrival_time como desempate
            selected_process = available_processes.loc[
                available_processes.groupby('priority')['arrival_time'].idxmin().loc[
                    available_processes['priority'].min()
                ]
            ]
            
            process_id = selected_process['process_id']
            arrival_time = selected_process['arrival_time']
            burst_time = selected_process['burst_time']
            priority = selected_process['priority']
            
            # Registrar tiempo de respuesta
            idx = self.processes[self.processes['process_id'] == process_id].index[0]
            response_time = self.current_time - arrival_time
            self.processes.loc[idx, 'response_time'] = response_time
            self.processes.loc[idx, 'first_response'] = self.current_time
            
            # Ejecutar el proceso completo
            start_time = self.current_time
            end_time = self.current_time + burst_time
            
            self.execution_sequence.append((process_id, start_time, end_time))
            self.gantt_data.append({
                'process': process_id,
                'start': start_time,
                'end': end_time
            })
            
            # Actualizar tiempos
            self.current_time = end_time
            completion_time = end_time
            turnaround_time = completion_time - arrival_time
            waiting_time = turnaround_time - burst_time
            
            # Guardar métricas
            self.processes.loc[idx, 'completion_time'] = completion_time
            self.processes.loc[idx, 'turnaround_time'] = turnaround_time
            self.processes.loc[idx, 'waiting_time'] = waiting_time
            self.processes.loc[idx, 'state'] = 'TERMINATED'
            
            completed_processes.add(process_id)
        
        return self._calculate_averages()
    
    def _calculate_averages(self):
        """Calcula las métricas promedio"""
        avg_waiting = self.processes['waiting_time'].mean()
        avg_turnaround = self.processes['turnaround_time'].mean()
        avg_response = self.processes['response_time'].mean()
        
        return {
            'processes': self.processes.copy(),
            'execution_sequence': self.execution_sequence.copy(),
            'gantt_data': self.gantt_data.copy(),
            'avg_waiting_time': avg_waiting,
            'avg_turnaround_time': avg_turnaround,
            'avg_response_time': avg_response
        }
    
    def compare_algorithms(self):
        """
        Compara todos los algoritmos y muestra resultados
        """
        print("\n" + "="*80)
        print("              COMPARACIÓN DE ALGORITMOS DE PLANIFICACIÓN")
        print("="*80)
        
        algorithms = [
            ("FIFO", self.simulate_fifo),
            ("SJF", self.simulate_sjf),
            ("Round Robin", self.simulate_round_robin),
            ("Prioridad", self.simulate_priority)
        ]
        
        results = {}
        
        for name, algorithm in algorithms:
            print(f"\n--- Ejecutando {name} ---")
            result = algorithm()
            results[name] = result
            
            print(f"Tiempo promedio de espera: {result['avg_waiting_time']:.2f}")
            print(f"Tiempo promedio de retorno: {result['avg_turnaround_time']:.2f}")
            print(f"Tiempo promedio de respuesta: {result['avg_response_time']:.2f}")
        
        return results
    
    def generate_comparison_chart(self, results):
        """
        Genera un gráfico comparativo de todos los algoritmos
        """
        algorithms = list(results.keys())
        waiting_times = [results[alg]['avg_waiting_time'] for alg in algorithms]
        turnaround_times = [results[alg]['avg_turnaround_time'] for alg in algorithms]
        response_times = [results[alg]['avg_response_time'] for alg in algorithms]
        
        # Crear gráfico comparativo
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Colores para cada algoritmo
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        # 1. Gráfico de tiempos de espera
        bars1 = axes[0, 0].bar(algorithms, waiting_times, color=colors, edgecolor='black', linewidth=1.5)
        axes[0, 0].set_title('Tiempo Promedio de Espera', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylabel('Tiempo (unidades)')
        axes[0, 0].grid(axis='y', linestyle='--', alpha=0.7)
        
        # Añadir valores en las barras
        for bar in bars1:
            height = bar.get_height()
            axes[0, 0].text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # 2. Gráfico de tiempos de retorno
        bars2 = axes[0, 1].bar(algorithms, turnaround_times, color=colors, edgecolor='black', linewidth=1.5)
        axes[0, 1].set_title('Tiempo Promedio de Retorno', fontsize=14, fontweight='bold')
        axes[0, 1].set_ylabel('Tiempo (unidades)')
        axes[0, 1].grid(axis='y', linestyle='--', alpha=0.7)
        
        for bar in bars2:
            height = bar.get_height()
            axes[0, 1].text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # 3. Gráfico de tiempos de respuesta
        bars3 = axes[1, 0].bar(algorithms, response_times, color=colors, edgecolor='black', linewidth=1.5)
        axes[1, 0].set_title('Tiempo Promedio de Respuesta', fontsize=14, fontweight='bold')
        axes[1, 0].set_ylabel('Tiempo (unidades)')
        axes[1, 0].grid(axis='y', linestyle='--', alpha=0.7)
        
        for bar in bars3:
            height = bar.get_height()
            axes[1, 0].text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # 4. Gráfico comparativo conjunto
        x = np.arange(len(algorithms))
        width = 0.25
        
        axes[1, 1].bar(x - width, waiting_times, width, label='Tiempo Espera', 
                      color='#FF6B6B', edgecolor='black', linewidth=1)
        axes[1, 1].bar(x, turnaround_times, width, label='Tiempo Retorno', 
                      color='#4ECDC4', edgecolor='black', linewidth=1)
        axes[1, 1].bar(x + width, response_times, width, label='Tiempo Respuesta', 
                      color='#45B7D1', edgecolor='black', linewidth=1)
        
        axes[1, 1].set_title('Comparación General', fontsize=14, fontweight='bold')
        axes[1, 1].set_ylabel('Tiempo (unidades)')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(algorithms)
        axes[1, 1].legend()
        axes[1, 1].grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        fig.suptitle('Comparación de Algoritmos de Planificación', 
                    fontsize=16, fontweight='bold', y=1.02)
        
        return fig
    
    def generate_gantt_charts(self, results):
        """
        Genera diagramas de Gantt para todos los algoritmos
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        axes = axes.flatten()
        
        algorithms = list(results.keys())
        colors = plt.cm.tab10.colors
        
        for i, algorithm in enumerate(algorithms):
            ax = axes[i]
            gantt_data = results[algorithm]['gantt_data']
            
            # Crear colores para procesos
            process_colors = {}
            unique_processes = set([d['process'] for d in gantt_data if d['process'] != 'IDLE'])
            for j, process in enumerate(unique_processes):
                process_colors[process] = colors[j % len(colors)]
            process_colors['IDLE'] = 'lightgrey'
            
            # Dibujar barras
            for data in gantt_data:
                process = data['process']
                start = data['start']
                end = data['end']
                duration = end - start
                
                ax.barh(0, duration, left=start, height=0.5,
                       color=process_colors[process], edgecolor='black', alpha=0.8)
                
                # Añadir etiqueta
                if duration > 0.5:
                    ax.text(start + duration/2, 0, process,
                           ha='center', va='center', fontweight='bold')
            
            ax.set_title(f'{algorithm}', fontsize=12, fontweight='bold')
            ax.set_xlabel('Tiempo (unidades)')
            ax.set_yticks([])
            ax.grid(axis='x', linestyle='--', alpha=0.7)
            
            if gantt_data:
                ax.set_xlim(0, max([d['end'] for d in gantt_data]))
        
        plt.tight_layout()
        fig.suptitle('Diagramas de Gantt - Comparación de Algoritmos', 
                    fontsize=16, fontweight='bold', y=1.02)
        
        return fig

def get_user_processes():
    """Permite al usuario ingresar procesos manualmente"""
    processes_data = []
    
    try:
        num_processes = int(input("Ingrese el número de procesos: "))
        
        for i in range(num_processes):
            print(f"\n--- Proceso {i+1} ---")
            process_id = input(f"ID del proceso (por defecto P{i+1}): ") or f"P{i+1}"
            arrival_time = int(input("Tiempo de llegada: "))
            burst_time = int(input("Tiempo de ejecución (burst time): "))
            priority = int(input("Prioridad (menor número = mayor prioridad): "))
            
            processes_data.append({
                'process_id': process_id,
                'arrival_time': arrival_time,
                'burst_time': burst_time,
                'priority': priority
            })
        
        return pd.DataFrame(processes_data)
    
    except ValueError as e:
        print(f"Error: {e}")
        return None

def generate_example_processes():
    """Genera procesos de ejemplo"""
    processes_data = [
        {'process_id': 'P1', 'arrival_time': 0, 'burst_time': 10, 'priority': 3},
        {'process_id': 'P2', 'arrival_time': 1, 'burst_time': 4, 'priority': 1},
        {'process_id': 'P3', 'arrival_time': 3, 'burst_time': 6, 'priority': 2},
        {'process_id': 'P4', 'arrival_time': 4, 'burst_time': 2, 'priority': 4},
        {'process_id': 'P5', 'arrival_time': 6, 'burst_time': 8, 'priority': 2}
    ]
    
    return pd.DataFrame(processes_data)

# Programa principal
if __name__ == "__main__":
    try:
        print("=" * 80)
        print("        SIMULADOR COMPLETO DE ALGORITMOS DE PLANIFICACIÓN")
        print("=" * 80)
        print("Algoritmos incluidos:")
        print("1. FIFO (First In, First Out)")
        print("2. SJF (Shortest Job First)")
        print("3. Round Robin")
        print("4. Prioridades")
        print("=" * 80)
        
        # Obtener procesos
        choice = input("\n¿Desea ingresar procesos manualmente? (s/n): ").lower()
        
        if choice.startswith('s'):
            processes_df = get_user_processes()
            if processes_df is None or processes_df.empty:
                print("Usando procesos de ejemplo...")
                processes_df = generate_example_processes()
        else:
            processes_df = generate_example_processes()
        
        print("\nProcesos a simular:")
        print(processes_df.to_string(index=False))
        
        # Configurar quantum para Round Robin
        quantum = int(input(f"\nQuantum para Round Robin (por defecto 3): ") or 3)
        
        # Crear planificador
        planificador = PlanificadorCompleto(quantum=quantum)
        
        # Agregar procesos
        for _, process in processes_df.iterrows():
            planificador.add_process(
                process['process_id'],
                process['arrival_time'],
                process['burst_time'],
                process['priority']
            )
        
        # Ejecutar comparación
        print("\n🚀 Iniciando simulación de todos los algoritmos...")
        results = planificador.compare_algorithms()
        
        # Mostrar tabla comparativa
        print("\n" + "="*80)
        print("                    TABLA COMPARATIVA FINAL")
        print("="*80)
        
        comparison_data = []
        for algorithm, result in results.items():
            comparison_data.append({
                'Algoritmo': algorithm,
                'Tiempo Espera': f"{result['avg_waiting_time']:.2f}",
                'Tiempo Retorno': f"{result['avg_turnaround_time']:.2f}",
                'Tiempo Respuesta': f"{result['avg_response_time']:.2f}"
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        print(comparison_df.to_string(index=False))
        
        # Encontrar el mejor algoritmo para cada métrica
        best_waiting = min(results.items(), key=lambda x: x[1]['avg_waiting_time'])
        best_turnaround = min(results.items(), key=lambda x: x[1]['avg_turnaround_time'])
        best_response = min(results.items(), key=lambda x: x[1]['avg_response_time'])
        
        print(f"\n🏆 MEJORES ALGORITMOS:")
        print(f"Menor tiempo de espera: {best_waiting[0]} ({best_waiting[1]['avg_waiting_time']:.2f})")
        print(f"Menor tiempo de retorno: {best_turnaround[0]} ({best_turnaround[1]['avg_turnaround_time']:.2f})")
        print(f"Menor tiempo de respuesta: {best_response[0]} ({best_response[1]['avg_response_time']:.2f})")
        
        # Generar gráficos
        print("\n📊 Generando gráficos comparativos...")
        
        # Gráfico de comparación de métricas
        comparison_fig = planificador.generate_comparison_chart(results)
        comparison_fig.savefig("d:\\cloud computing\\round robin.py\\comparacion_algoritmos.png", 
                              dpi=300, bbox_inches='tight')
        print("✅ Gráfico de comparación guardado: comparacion_algoritmos.png")
        
        # Diagramas de Gantt
        gantt_fig = planificador.generate_gantt_charts(results)
        gantt_fig.savefig("d:\\cloud computing\\round robin.py\\gantt_comparacion.png", 
                         dpi=300, bbox_inches='tight')
        print("✅ Diagramas de Gantt guardados: gantt_comparacion.png")
        
        # Guardar resultados detallados
        with open("d:\\cloud computing\\round robin.py\\resultados_comparacion.txt", "w", encoding='utf-8') as f:
            f.write("COMPARACIÓN DE ALGORITMOS DE PLANIFICACIÓN\n")
            f.write("="*50 + "\n\n")
            
            f.write("PROCESOS SIMULADOS:\n")
            f.write(processes_df.to_string(index=False) + "\n\n")
            
            f.write(f"QUANTUM ROUND ROBIN: {quantum}\n\n")
            
            for algorithm, result in results.items():
                f.write(f"--- {algorithm.upper()} ---\n")
                f.write(f"Tiempo promedio de espera: {result['avg_waiting_time']:.2f}\n")
                f.write(f"Tiempo promedio de retorno: {result['avg_turnaround_time']:.2f}\n")
                f.write(f"Tiempo promedio de respuesta: {result['avg_response_time']:.2f}\n")
                
                f.write("\nSecuencia de ejecución:\n")
                for proc, start, end in result['execution_sequence']:
                    f.write(f"{proc}: {start} -> {end}\n")
                f.write("\n")
            
            f.write("MEJORES ALGORITMOS:\n")
            f.write(f"Menor tiempo de espera: {best_waiting[0]}\n")
            f.write(f"Menor tiempo de retorno: {best_turnaround[0]}\n")
            f.write(f"Menor tiempo de respuesta: {best_response[0]}\n")
        
        print("✅ Resultados detallados guardados: resultados_comparacion.txt")
        
        # Mostrar gráficos
        plt.show()
        
        print("\n🎉 ¡Simulación completada exitosamente!")
        print("Archivos generados:")
        print("- comparacion_algoritmos.png")
        print("- gantt_comparacion.png") 
        print("- resultados_comparacion.txt")
        
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
