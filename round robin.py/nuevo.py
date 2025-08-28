class Proceso:
    def __init__(self, nombre, llegada, cpu, prioridad):
        self.nombre = nombre
        self.llegada = llegada
        self.cpu = cpu
        self.tiempo_restante = cpu
        self.prioridad = prioridad
        self.inicio = None
        self.fin = None
        self.espera = 0
        self.retorno = 0

def round_robin(procesos, quantum):
    tiempo = 0
    cola = []
    completados = []
    gantt = []
    
    print("=== SIMULACIÓN ROUND ROBIN (Quantum = 3) ===\n")
    
    while len(completados) < len(procesos):
        # Agregar procesos que llegan en este tiempo
        for p in procesos:
            if (p.llegada <= tiempo and p not in cola and 
                p not in completados and p.tiempo_restante > 0):
                cola.append(p)
                print(f"Tiempo {tiempo}: {p.nombre} entra a la cola")
        
        if cola:
            proceso_actual = cola.pop(0)
            
            # Marcar inicio si es primera vez
            if proceso_actual.inicio is None:
                proceso_actual.inicio = tiempo
            
            # Calcular tiempo de ejecución
            tiempo_ejecucion = min(quantum, proceso_actual.tiempo_restante)
            
            # Registrar en diagrama de Gantt
            gantt.append({
                'proceso': proceso_actual.nombre,
                'inicio': tiempo,
                'fin': tiempo + tiempo_ejecucion
            })
            
            print(f"Tiempo {tiempo}-{tiempo + tiempo_ejecucion}: Ejecutando {proceso_actual.nombre}")
            print(f"  Tiempo restante antes: {proceso_actual.tiempo_restante}")
            
            # Actualizar tiempos
            tiempo += tiempo_ejecucion
            proceso_actual.tiempo_restante -= tiempo_ejecucion
            
            print(f"  Tiempo restante después: {proceso_actual.tiempo_restante}")
            
            # Agregar nuevos procesos que llegaron durante la ejecución
            for p in procesos:
                if (p.llegada <= tiempo and p not in cola and 
                    p not in completados and p.tiempo_restante > 0 and p != proceso_actual):
                    cola.append(p)
                    print(f"  {p.nombre} entra a la cola durante ejecución")
            
            # Verificar si el proceso terminó
            if proceso_actual.tiempo_restante == 0:
                proceso_actual.fin = tiempo
                proceso_actual.retorno = proceso_actual.fin - proceso_actual.llegada
                proceso_actual.espera = proceso_actual.retorno - proceso_actual.cpu
                completados.append(proceso_actual)
                print(f"  {proceso_actual.nombre} COMPLETADO")
            else:
                # Volver a la cola si no terminó
                cola.append(proceso_actual)
                print(f"  {proceso_actual.nombre} regresa a la cola")
            
            print(f"  Cola actual: {[p.nombre for p in cola]}\n")
        else:
            # CPU inactiva
            gantt.append({'proceso': 'IDLE', 'inicio': tiempo, 'fin': tiempo + 1})
            tiempo += 1
            print(f"Tiempo {tiempo-1}-{tiempo}: CPU INACTIVA\n")
    
    return completados, gantt

# Crear procesos
procesos = [
    Proceso('P1', 1, 10, 2),
    Proceso('P2', 1, 4, 1),
    Proceso('P3', 2, 6, 3)
]

# Ejecutar algoritmo
procesos_completados, diagrama_gantt = round_robin(procesos, 3)

# Mostrar diagrama de Gantt
print("=== DIAGRAMA DE GANTT ===")
for entrada in diagrama_gantt:
    print(f"Tiempo {entrada['inicio']}-{entrada['fin']}: {entrada['proceso']}")

# Crear diagrama visual
print(f"\n=== DIAGRAMA VISUAL ===")
timeline = ""
marcas = ""
for entrada in diagrama_gantt:
    if entrada['proceso'] != 'IDLE':
        duracion = entrada['fin'] - entrada['inicio']
        timeline += f"|{entrada['proceso']:^{duracion*3}}"
        marcas += f"{entrada['inicio']:<{duracion*3+1}}"

print(timeline + "|")
print(marcas + f"{diagrama_gantt[-1]['fin']}")

# Tabla de resultados
print(f"\n=== TABLA DE RESULTADOS ===")
print("Proceso | Llegada | CPU | Inicio | Fin | Espera | Retorno")
print("-" * 60)

total_espera = 0
total_retorno = 0

for p in sorted(procesos_completados, key=lambda x: x.nombre):
    print(f"{p.nombre:7} | {p.llegada:7} | {p.cpu:3} | {p.inicio:6} | "
          f"{p.fin:3} | {p.espera:6} | {p.retorno:7}")
    total_espera += p.espera
    total_retorno += p.retorno

print("-" * 60)
print(f"PROMEDIOS:")
print(f"Tiempo de espera promedio: {total_espera/len(procesos_completados):.2f}")
print(f"Tiempo de retorno promedio: {total_retorno/len(procesos_completados):.2f}")