import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time

# Definir una función para limpiar la pantalla sin depender de IPython
def clear_screen():
    """Función alternativa para limpiar la pantalla"""
    print("\n" * 50)  # Imprimir líneas en blanco como alternativa

class RoundRobinSimulator:
    def __init__(self, quantum):
        """
        Inicializa el simulador de Round Robin con un quantum especificado
        
        Args:
            quantum (int): Cantidad de tiempo asignado a cada proceso
        """
        self.quantum = quantum
        self.processes = pd.DataFrame()
        self.current_time = 0
        self.execution_sequence = []
        self.gantt_data = []
        self.process_status = []
        self.waiting_times = {}
        self.turnaround_times = {}
    
    def add_process(self, process_id, arrival_time, burst_time):
        """
        Agrega un proceso a la simulación
        
        Args:
            process_id (str): Identificador único del proceso
            arrival_time (int): Tiempo de llegada del proceso
            burst_time (int): Tiempo de CPU requerido por el proceso
        """
        new_process = pd.DataFrame({
            'process_id': [process_id],             # ID del proceso
            'arrival_time': [arrival_time],         # Tiempo de llegada al sistema
            'burst_time': [burst_time],             # Tiempo total de ejecución requerido
            'remaining_time': [burst_time],         # Tiempo restante de ejecución
            'completion_time': [0],                 # Tiempo de finalización
            'waiting_time': [0],                    # Tiempo de espera en cola
            'turnaround_time': [0],                 # Tiempo total en el sistema
            'first_response': [-1],                 # Tiempo de primera respuesta
            'state': ['NEW']                        # Estado del proceso
        })
        
        # Concatenar el nuevo proceso al DataFrame de procesos
        self.processes = pd.concat([self.processes, new_process], ignore_index=True)
        
        # Ordenar los procesos por tiempo de llegada
        self.processes = self.processes.sort_values(by=['arrival_time', 'process_id']).reset_index(drop=True)
        
    def add_processes_from_dataframe(self, df):
        """
        Agrega múltiples procesos desde un DataFrame
        
        Args:
            df (DataFrame): DataFrame con columnas 'process_id', 'arrival_time', 'burst_time'
        """
        for _, row in df.iterrows():
            self.add_process(row['process_id'], row['arrival_time'], row['burst_time'])
            
    def is_arrived(self, process_id, current_time):
        """Verifica si un proceso ha llegado al sistema"""
        process = self.processes[self.processes['process_id'] == process_id]
        return process['arrival_time'].values[0] <= current_time
            
    def get_ready_queue(self, current_time):
        """
        Obtiene la cola de procesos listos en el tiempo actual
        
        Returns:
            DataFrame: DataFrame con los procesos listos para ejecutar
        """
        # Procesos que han llegado y aún no han terminado
        ready = self.processes[
            (self.processes['arrival_time'] <= current_time) & 
            (self.processes['remaining_time'] > 0)
        ]
        return ready
    
    def run_simulation(self, visualize=False, step_by_step=False, delay=0.5):
        """
        Ejecuta la simulación del algoritmo Round Robin
        
        Args:
            visualize (bool): Si es True, muestra la simulación visualmente
            step_by_step (bool): Si es True, espera entrada del usuario entre pasos
            delay (float): Tiempo de espera entre pasos si step_by_step es False
        """sssssssssssssssssssssssssssssssssss
        self.execution_sequence = []
        self.gantt_data = []
        self.process_status = []
        self.current_time = 0
        ready_queue = []
        
        # Inicializar el tiempo restante para cada proceso
        self.processes['remaining_time'] = self.processes['burst_time']
        self.processes['state'] = 'NEW'
        self.processes['first_response'] = -
        
        # Función auxiliar para agregar procesos que han llegado
        def add_arrived_processes():
            for i, row in self.processes.iterrows():
                if (row['arrival_time'] <= self.current_time and 
                    row['remaining_time'] > 0 and 
                    row['process_id'] not in ready_queue and 
                    row['state'] != 'TERMINATED'):
                    
                    ready_queue.append(row['process_id'])
                    
                    # Actualizar el estado del proceso a READY
                    if self.processes.loc[i, 'state'] == 'NEW':
                        self.processes.loc[i, 'state'] = 'READY'
        
        # Agregar procesos que ya han llegado al tiempo 0
        add_arrived_processes()
        
        # Mientras haya procesos con tiempo restante
        while True:
            # Si la cola está vacía pero aún hay procesos que no han llegado
            if not ready_queue and self.processes[self.processes['remaining_time'] > 0].shape[0] > 0:
                next_arrival = self.processes[
                    (self.processes['remaining_time'] > 0) & 
                    (self.processes['arrival_time'] > self.current_time)
                ]['arrival_time'].min()
                
                # Registrar tiempo ocioso
                idle_duration = next_arrival - self.current_time
                self.execution_sequence.append(('IDLE', self.current_time, next_arrival))
                self.gantt_data.append({
                    'process': 'IDLE',
                    'start': self.current_time,
                    'end': next_arrival
                })
                
                # Avanzar el tiempo al próximo arribo
                self.current_time = next_arrival
                
                # Agregar procesos que acaban de llegar
                add_arrived_processes()
                continue
            
            # Si no hay más procesos en la cola y no hay más procesos por llegar
            if not ready_queue:
                break
            
            # Obtener el próximo proceso a ejecutar (FIFO - First In First Out)
            current_process_id = ready_queue.pop(0)
            current_process_idx = self.processes[self.processes['process_id'] == current_process_id].index[0]
            
            # Registrar primera respuesta si no se ha hecho
            if self.processes.loc[current_process_idx, 'first_response'] == -1:
                self.processes.loc[current_process_idx, 'first_response'] = self.current_time
            
            # Actualizar el estado del proceso a RUNNING
            self.processes.loc[current_process_idx, 'state'] = 'RUNNING'
            
            # Determinar cuánto tiempo se ejecutará este proceso
            remaining = self.processes.loc[current_process_idx, 'remaining_time']
            execution_time = min(self.quantum, remaining)
            
            # Registrar ejecución en la secuencia
            start_time = self.current_time
            end_time = self.current_time + execution_time
            self.execution_sequence.append((current_process_id, start_time, end_time))
            self.gantt_data.append({
                'process': current_process_id,
                'start': start_time,
                'end': end_time
            })
            
            # Actualizar el tiempo actual
            self.current_time += execution_time
            
            # Actualizar el tiempo restante del proceso
            new_remaining = remaining - execution_time
            self.processes.loc[current_process_idx, 'remaining_time'] = new_remaining
            
            # IMPORTANTE: Agregar procesos que llegaron DURANTE la ejecución actual
            add_arrived_processes()
            
            # Guardar el estado actual de los procesos para visualización
            current_status = self.processes.copy()
            current_status['current_time'] = self.current_time
            self.process_status.append(current_status)
            
            # Si el proceso ha terminado
            if new_remaining == 0:
                self.processes.loc[current_process_idx, 'state'] = 'TERMINATED'
                self.processes.loc[current_process_idx, 'completion_time'] = self.current_time
                
                # Calcular tiempos de espera y retorno
                arrival = self.processes.loc[current_process_idx, 'arrival_time']
                burst = self.processes.loc[current_process_idx, 'burst_time']
                completion = self.processes.loc[current_process_idx, 'completion_time']
                
                turnaround_time = completion - arrival
                waiting_time = turnaround_time - burst
                
                self.processes.loc[current_process_idx, 'turnaround_time'] = turnaround_time
                self.processes.loc[current_process_idx, 'waiting_time'] = waiting_time
                
                self.turnaround_times[current_process_id] = turnaround_time
                self.waiting_times[current_process_id] = waiting_time
            else:
                # Si el proceso aún necesita más tiempo, vuelve AL FINAL de la cola
                self.processes.loc[current_process_idx, 'state'] = 'READY'
                ready_queue.append(current_process_id)  # Esto mantiene el orden Round Robin
            
            # Visualización paso a paso si está activada
            if visualize:
                self.visualize_step(current_process_id, execution_time, step_by_step, delay)
        
        # Calcular métricas finales
        avg_waiting_time = self.processes['waiting_time'].mean()
        avg_turnaround_time = self.processes['turnaround_time'].mean()
        
        return {
            'processes': self.processes,
            'execution_sequence': self.execution_sequence,
            'gantt_data': self.gantt_data,
            'avg_waiting_time': avg_waiting_time,
            'avg_turnaround_time': avg_turnaround_time
        }
    
    def visualize_step(self, current_process, time_slice, step_by_step, delay):
        """Visualiza un paso de la simulación"""
        # Usar la función definida al principio del archivo
        clear_screen()
        
        print(f"\n{'='*80}")
        print(f"Tiempo actual: {self.current_time}")
        print(f"Ejecutando proceso: {current_process} por {time_slice} unidades de tiempo")
        print(f"{'='*80}\n")
        
        # Mostrar estado de todos los procesos
        status_df = self.processes.copy()
        status_df['progress'] = ((status_df['burst_time'] - status_df['remaining_time']) / 
                                status_df['burst_time'] * 100).round(1)
        
        print(status_df[['process_id', 'arrival_time', 'burst_time', 
                        'remaining_time', 'progress', 'state']].to_string(index=False))
        
        if step_by_step:
            input("\nPresiona Enter para continuar...")
        else:
            time.sleep(delay)
    
    def generate_gantt_chart(self, fig_size=(12, 4)):
        """
        Genera un diagrama de Gantt de la ejecución
        
        Args:
            fig_size (tuple): Tamaño de la figura (ancho, alto)
        """
        if not self.gantt_data:
            print("No hay datos de ejecución. Ejecuta la simulación primero.")
            return
        
        # Crear el diagrama de Gantt
        fig, ax = plt.subplots(figsize=fig_size)
        
        # Configurar etiquetas en español
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.labelsize'] = 10
        
        # Colores para los procesos (ciclo entre varios colores)
        colors = plt.cm.tab10.colors
        process_colors = {}
        
        # Asignar un color a cada proceso
        unique_processes = set([d['process'] for d in self.gantt_data if d['process'] != 'IDLE'])
        for i, process in enumerate(unique_processes):
            process_colors[process] = colors[i % len(colors)]
        
        # IDLE siempre en gris
        process_colors['IDLE'] = 'lightgrey'
        
        # Dibujar barras para cada bloque de ejecución
        y_pos = 0
        for i, data in enumerate(self.gantt_data):
            process = data['process']
            start = data['start']
            end = data['end']
            duration = end - start
            
            ax.barh(y_pos, duration, left=start, height=0.5, 
                    color=process_colors[process], alpha=0.8, 
                    edgecolor='black', linewidth=1)
            
            # Añadir etiqueta en el centro de la barra
            if duration > 0.5:  # Solo si hay espacio suficiente
                ax.text(start + duration/2, y_pos, process, 
                        ha='center', va='center', color='black',
                        fontweight='bold')
        
        # Configuración de ejes y etiquetas en español
        ax.set_yticks([])
        ax.set_xlabel('Tiempo (unidades)')
        ax.set_title('Diagrama de Gantt - Algoritmo Round Robin')
        
        # Ajustar los límites del eje x
        ax.set_xlim(0, self.current_time)
        
        # Añadir cuadrícula
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        return fig
    
    def generate_metrics_summary(self):
        """
        Genera un resumen de métricas de la simulación
        
        Returns:
            DataFrame: DataFrame con las métricas de cada proceso
        """
        # Crear una copia del DataFrame original
        metrics = self.processes[['process_id', 'arrival_time', 'burst_time', 
                                'completion_time', 'turnaround_time', 'waiting_time']].copy()
        
        # Renombrar las columnas a español
        metrics = metrics.rename(columns={
            'process_id': 'ID Proceso',
            'arrival_time': 'Tiempo Llegada',
            'burst_time': 'Tiempo Ráfaga',
            'completion_time': 'Tiempo Finalización',
            'turnaround_time': 'Tiempo Retorno',
            'waiting_time': 'Tiempo Espera'
        })
        
        # Añadir promedios
        averages = pd.DataFrame({
            'ID Proceso': ['PROMEDIO'],
            'Tiempo Llegada': [None],
            'Tiempo Ráfaga': [metrics['Tiempo Ráfaga'].mean()],
            'Tiempo Finalización': [None],
            'Tiempo Retorno': [metrics['Tiempo Retorno'].mean()],
            'Tiempo Espera': [metrics['Tiempo Espera'].mean()]
        })
        
        metrics = pd.concat([metrics, averages], ignore_index=True)
        return metrics
        
    def plot_comprehensive_metrics(self, fig_size=(14, 10)):
        """
        Genera un gráfico completo con todas las métricas importantes
        
        Args:
            fig_size (tuple): Tamaño de la figura (ancho, alto)
            
        Returns:
            Figure: Figura de matplotlib con el gráfico
        """
        if self.processes.empty:
            print("No hay datos de procesos. Ejecuta la simulación primero.")
            return
            
        # Crear una figura más completa con 4 subplots
        fig, axes = plt.subplots(2, 2, figsize=fig_size)
        
        # Configurar estilo y fuentes en español
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.labelsize'] = 10
        
        # Filtrar datos excluyendo el promedio si existe
        process_data = self.processes[self.processes['process_id'] != 'PROMEDIO'].copy()
        
        # Ordenar los procesos para mejor visualización
        process_data = process_data.sort_values('process_id')
        
        # Colores para los gráficos
        colors_cycle = plt.cm.tab10(np.linspace(0, 1, len(process_data)))
        
        # 1. Gráfico de tiempo de espera
        axes[0, 0].bar(process_data['process_id'], process_data['waiting_time'], 
                      color=colors_cycle, edgecolor='black', linewidth=1.2)
        axes[0, 0].set_title('Tiempo de Espera', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Proceso')
        axes[0, 0].set_ylabel('Tiempo (unidades)')
        axes[0, 0].grid(axis='y', linestyle='--', alpha=0.7)
        
        # Añadir línea de promedio
        avg_waiting = process_data['waiting_time'].mean()
        axes[0, 0].axhline(y=avg_waiting, color='red', linestyle='--')
        axes[0, 0].text(0, avg_waiting * 1.05, f'Promedio: {avg_waiting:.2f}', 
                      color='red', fontweight='bold')
                      
        # 2. Gráfico de tiempo de retorno
        axes[0, 1].bar(process_data['process_id'], process_data['turnaround_time'], 
                      color=colors_cycle, edgecolor='black', linewidth=1.2)
        axes[0, 1].set_title('Tiempo de Retorno', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Proceso')
        axes[0, 1].set_ylabel('Tiempo (unidades)')
        axes[0, 1].grid(axis='y', linestyle='--', alpha=0.7)
        
        # Añadir línea de promedio
        avg_turnaround = process_data['turnaround_time'].mean()
        axes[0, 1].axhline(y=avg_turnaround, color='red', linestyle='--')
        axes[0, 1].text(0, avg_turnaround * 1.05, f'Promedio: {avg_turnaround:.2f}', 
                       color='red', fontweight='bold')
        
        # 3. Gráfico comparativo de tiempos
        processes = process_data['process_id'].tolist()
        burst_times = process_data['burst_time'].tolist()
        waiting_times = process_data['waiting_time'].tolist()
        turnaround_times = process_data['turnaround_time'].tolist()
        
        x = np.arange(len(processes))  # Posiciones en el eje x
        width = 0.25  # Ancho de las barras
        
        axes[1, 0].bar(x - width, burst_times, width, label='Tiempo de Ráfaga',
                      color='skyblue', edgecolor='black', linewidth=1.2)
        axes[1, 0].bar(x, waiting_times, width, label='Tiempo de Espera',
                      color='lightgreen', edgecolor='black', linewidth=1.2)
        axes[1, 0].bar(x + width, turnaround_times, width, label='Tiempo de Retorno',
                      color='salmon', edgecolor='black', linewidth=1.2)
        
        axes[1, 0].set_title('Comparación de Tiempos', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Proceso')
        axes[1, 0].set_ylabel('Tiempo (unidades)')
        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels(processes)
        axes[1, 0].legend()
        axes[1, 0].grid(axis='y', linestyle='--', alpha=0.7)
        
        # 4. Diagrama de Gantt simplificado
        gantt_data = pd.DataFrame(self.gantt_data)
        
        # Crear un conjunto de colores para cada proceso
        unique_processes = gantt_data['process'].unique()
        process_colors = {}
        for i, proc in enumerate(unique_processes):
            if proc != 'IDLE':
                process_colors[proc] = plt.cm.tab10(i % 10)
            else:
                process_colors[proc] = (0.8, 0.8, 0.8, 1.0)  # Gris para IDLE
                
        # Dibujar barras para cada bloque de ejecución
        for i, row in gantt_data.iterrows():
            process = row['process']
            start = row['start']
            end = row['end']
            duration = end - start
            
            axes[1, 1].barh(0, duration, left=start, height=0.5,
                           color=process_colors[process], edgecolor='black')
            
            # Añadir etiqueta en el centro de la barra
            if duration > 0.5:
                axes[1, 1].text(start + duration/2, 0, process,
                              ha='center', va='center', fontweight='bold')
        
        axes[1, 1].set_title('Diagrama de Gantt Simplificado', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Tiempo (unidades)')
        axes[1, 1].set_yticks([])
        axes[1, 1].grid(axis='x', linestyle='--', alpha=0.7)
        axes[1, 1].set_xlim(0, gantt_data['end'].max())
        
        # Título general y ajustes
        plt.tight_layout()
        fig.suptitle(f'Análisis del Algoritmo Round Robin (Quantum = {self.quantum})', 
                    fontsize=16, fontweight='bold', y=1.02)
        
        return fig
    
    def plot_metrics(self, fig_size=(12, 6)):
        """
        Genera gráficos de barras para visualizar las métricas
        
        Args:
            fig_size (tuple): Tamaño de la figura (ancho, alto)
        """
        if self.processes.empty:
            print("No hay datos de procesos. Ejecuta la simulación primero.")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=fig_size)
        
        # Configurar estilo y fuentes en español
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.labelsize'] = 10
        
        # Filtrar datos excluyendo el promedio si existe
        process_data = self.processes[self.processes['process_id'] != 'PROMEDIO'].copy()
        
        # Ordenar los procesos para mejor visualización
        process_data = process_data.sort_values('process_id')
        
        # Colores para los gráficos
        colors_waiting = plt.cm.Blues(np.linspace(0.6, 0.9, len(process_data)))
        colors_turnaround = plt.cm.Greens(np.linspace(0.6, 0.9, len(process_data)))
        
        # Gráfico de tiempos de espera
        bars_wait = axes[0].bar(process_data['process_id'], process_data['waiting_time'], 
                         color=colors_waiting, edgecolor='black', linewidth=1.5)
        
        axes[0].set_title('Tiempo de Espera por Proceso', fontsize=12, fontweight='bold')
        axes[0].set_xlabel('Proceso', fontsize=10)
        axes[0].set_ylabel('Tiempo de Espera (unidades)', fontsize=10)
        axes[0].grid(axis='y', linestyle='--', alpha=0.7)
        
        # Añadir etiquetas de valor en las barras
        for bar in bars_wait:
            height = bar.get_height()
            axes[0].text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Gráfico de tiempos de retorno
        bars_turn = axes[1].bar(process_data['process_id'], process_data['turnaround_time'], 
                         color=colors_turnaround, edgecolor='black', linewidth=1.5)
        
        axes[1].set_title('Tiempo de Retorno por Proceso', fontsize=12, fontweight='bold')
        axes[1].set_xlabel('Proceso', fontsize=10)
        axes[1].set_ylabel('Tiempo de Retorno (unidades)', fontsize=10)
        axes[1].grid(axis='y', linestyle='--', alpha=0.7)
        
        # Añadir etiquetas de valor en las barras
        for bar in bars_turn:
            height = bar.get_height()
            axes[1].text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Añadir línea horizontal para el promedio
        if len(self.processes) > 1:
            avg_waiting = self.processes['waiting_time'].mean()
            avg_turnaround = self.processes['turnaround_time'].mean()
            
            axes[0].axhline(y=avg_waiting, color='red', linestyle='--', linewidth=2)
            axes[0].text(len(process_data) * 0.5, avg_waiting + 0.2, 
                  f'Promedio: {avg_waiting:.2f}', ha='center', va='bottom', 
                  color='red', fontweight='bold')
            
            axes[1].axhline(y=avg_turnaround, color='red', linestyle='--', linewidth=2)
            axes[1].text(len(process_data) * 0.5, avg_turnaround + 0.2, 
                  f'Promedio: {avg_turnaround:.2f}', ha='center', va='bottom', 
                  color='red', fontweight='bold')
        
        # Ajustar márgenes y espaciado
        plt.tight_layout()
        fig.suptitle('Métricas del Algoritmo Round Robin', fontsize=14, fontweight='bold', y=1.05)
        
        return fig


# Función para generar un conjunto de ejemplo de procesos
def generate_example_processes(n=5):
    """
    Genera un conjunto de ejemplo de procesos
    
    Args:
        n (int): Número de procesos a generar
    
    Returns:
        DataFrame: DataFrame con los procesos generados
    """
    # Generar datos aleatorios para los procesos
    np.random.seed(42)  # Para reproducibilidad
    
    process_ids = [f'P{i+1}' for i in range(n)]
    arrival_times = np.sort(np.random.randint(0, 10, n))  # Tiempos de llegada ordenados
    burst_times = np.random.randint(1, 10, n)  # Tiempos de ráfaga entre 1 y 10
    
    # Crear DataFrame
    processes = pd.DataFrame({
        'process_id': process_ids,        # ID del proceso
        'arrival_time': arrival_times,    # Tiempo de llegada
        'burst_time': burst_times         # Tiempo de ráfaga (tiempo total de CPU requerido)
    })
    
    # Renombrar las columnas a español para mostrarlas
    processes_display = processes.rename(columns={
        'process_id': 'ID Proceso',
        'arrival_time': 'Tiempo Llegada',
        'burst_time': 'Tiempo Ráfaga'
    })
    
    # Mostrar la explicación de las columnas
    print("\nExplicación de las columnas:")
    print("- ID Proceso: Identificador único del proceso")
    print("- Tiempo Llegada: Momento en que el proceso llega al sistema")
    print("- Tiempo Ráfaga: Tiempo total que necesita el proceso para completar su ejecución")
    
    return processes

# Función para obtener procesos del usuario
def get_user_processes():
    """
    Permite al usuario ingresar los procesos manualmente
    
    Returns:
        DataFrame: DataFrame con los procesos ingresados por el usuario
    """
    processes_data = []
    
    try:
        num_processes = int(input("Ingrese el número de procesos: "))
        
        for i in range(num_processes):
            print(f"\n--- Proceso {i+1} ---")
            process_id = input(f"Identificador del proceso (por defecto P{i+1}): ")
            if not process_id:
                process_id = f"P{i+1}"
                
            arrival_time = int(input("Tiempo de llegada: "))
            burst_time = int(input("Tiempo de ejecución (burst time): "))
            
            processes_data.append({
                'process_id': process_id,
                'arrival_time': arrival_time,
                'burst_time': burst_time
            })
        
        return pd.DataFrame(processes_data)
    
    except ValueError as e:
        print(f"Error: Debe ingresar valores numéricos para tiempos. {e}")
        return None

# Ejemplo de uso de la simulación
if __name__ == "__main__":
    try:
        print("=" * 60)
        print("      SIMULADOR DE ALGORITMO ROUND ROBIN")
        print("=" * 60)
        
        # Preguntar si desea ingresar procesos manualmente o usar ejemplos
        choice = input("¿Desea ingresar procesos manualmente? (s/n): ").lower()
        
        if choice.startswith('s'):
            # Obtener procesos del usuario
            processes = get_user_processes()
            if processes is None or processes.empty:
                print("No se ingresaron procesos válidos. Usando procesos de ejemplo.")
                processes = generate_example_processes(5)
        else:
            # Usar procesos generados aleatoriamente
            num_processes = int(input("¿Cuántos procesos aleatorios desea generar? (por defecto: 5): ") or 5)
            processes = generate_example_processes(num_processes)
        
        print("\nProcesos a simular:")
        print(processes)
        
        # Obtener quantum del usuario
        quantum = int(input("\nIngrese el quantum de tiempo (por defecto: 2): ") or 2)
        
        print(f"\nIniciando simulación de Round Robin con quantum = {quantum}...")
        
        # Crear y ejecutar el simulador
        simulator = RoundRobinSimulator(quantum=quantum)
        simulator.add_processes_from_dataframe(processes)
        
        # Preguntar si desea visualización paso a paso
        visualize = input("¿Desea ver la simulación paso a paso? (s/n): ").lower().startswith('s')
        
        # Ejecutar la simulación
        results = simulator.run_simulation(visualize=visualize, step_by_step=visualize)
        
        # Mostrar resultados
        print("\nResultados de la simulación:")
        print(f"Tiempo promedio de espera: {results['avg_waiting_time']:.2f}")
        print(f"Tiempo promedio de retorno: {results['avg_turnaround_time']:.2f}")
        
        # Mostrar tabla de métricas
        print("\nMétricas por proceso:")
        metrics = simulator.generate_metrics_summary()
        print(metrics.to_string(index=False))
        
        # Mostrar explicación de las métricas
        print("\nExplicación de las métricas:")
        print("- ID Proceso: Identificador único de cada proceso")
        print("- Tiempo Llegada: Momento en que el proceso llega al sistema")
        print("- Tiempo Ráfaga: Tiempo total que el proceso necesita para completar su ejecución")
        print("- Tiempo Finalización: Momento en que el proceso termina su ejecución")
        print("- Tiempo Retorno: Tiempo total que el proceso pasa en el sistema (Finalización - Llegada)")
        print("- Tiempo Espera: Tiempo que el proceso pasa esperando en cola (Retorno - Ráfaga)")
        
        print("\nSecuencia de ejecución:")
        for proc, start, end in simulator.execution_sequence:
            print(f"Proceso {proc}: {start} -> {end}")
        
        # Guardar resultados en archivo
        with open("d:\\cloud computing\\resultados_round_robin.txt", "w") as f:
            f.write("Procesos simulados:\n")
            f.write(str(processes) + "\n\n")
            
            f.write(f"Quantum utilizado: {quantum}\n\n")
            
            f.write("Resultados de la simulación:\n")
            f.write(f"Tiempo promedio de espera: {results['avg_waiting_time']:.2f}\n")
            f.write(f"Tiempo promedio de retorno: {results['avg_turnaround_time']:.2f}\n\n")
            
            f.write("Métricas por proceso:\n")
            f.write(metrics.to_string(index=False) + "\n\n")
            
            f.write("Secuencia de ejecución:\n")
            for proc, start, end in simulator.execution_sequence:
                f.write(f"Proceso {proc}: {start} -> {end}\n")
        
        print("\n¡Resultados guardados en d:\\cloud computing\\resultados_round_robin.txt!")
        
        # Generar y mostrar gráficos
        print("\nGenerando gráficos...")
        
        # Preguntamos qué gráficos quiere ver
        print("\n¿Qué gráficos desea visualizar?")
        print("1. Diagrama de Gantt")
        print("2. Gráficos de barras con métricas")
        print("3. Gráfico completo con todas las métricas")
        print("4. Todos los gráficos")
        
        try:
            choice = int(input("\nIngrese su elección (1-4): "))
        except ValueError:
            choice = 2  # Por defecto mostramos los gráficos de barras
        
        # Según la elección, mostramos diferentes gráficos
        if choice == 1 or choice == 4:
            try:
                gantt_fig = simulator.generate_gantt_chart()
                gantt_fig.savefig("d:\\cloud computing\\gantt_chart.png")
                print("Diagrama de Gantt guardado como: d:\\cloud computing\\gantt_chart.png")
                plt.figure(gantt_fig.number)
                plt.show(block=False if choice == 4 else True)
            except Exception as e:
                print(f"No se pudo generar el diagrama de Gantt: {e}")
        
        if choice == 2 or choice == 4:
            try:
                metrics_fig = simulator.plot_metrics()
                metrics_fig.savefig("d:\\cloud computing\\metricas_barras.png")
                print("Gráficos de métricas en barras guardados como: d:\\cloud computing\\metricas_barras.png")
                plt.figure(metrics_fig.number)
                plt.show(block=False if choice == 4 else True)
            except Exception as e:
                print(f"No se pudo generar el gráfico de métricas en barras: {e}")
        
        if choice == 3 or choice == 4:
            try:
                comp_fig = simulator.plot_comprehensive_metrics()
                comp_fig.savefig("d:\\cloud computing\\metricas_completas.png")
                print("Gráfico completo guardado como: d:\\cloud computing\\metricas_completas.png")
                plt.figure(comp_fig.number)
                plt.show()  # Este es el último, así que bloqueamos para mantener las figuras abiertas
            except Exception as e:
                print(f"No se pudo generar el gráfico completo: {e}")
        
        print("\n¡Simulación completada con éxito!")
        
    except Exception as e:
        print(f"\nError durante la ejecución: {e}")
        # Guardar el error en un archivo
        with open("d:\\cloud computing\\error_round_robin.txt", "w") as f:
            f.write(f"Error durante la ejecución: {e}")
        print(f"Detalles del error guardados en: d:\\cloud computing\\error_round_robin.txt")