# Algoritmo Round Robin

Este proyecto implementa el algoritmo de planificación Round Robin para sistemas operativos.

## Descripción

Round Robin es un algoritmo de planificación de procesos que asigna a cada proceso un tiempo fijo de ejecución (quantum) de manera cíclica. Es uno de los algoritmos más utilizados en sistemas de tiempo compartido.

## Características

- **Algoritmo**: Round Robin con quantum configurable
- **Lenguaje**: Python
- **Métricas calculadas**:
  - Tiempo de espera promedio
  - Tiempo de respuesta promedio
  - Tiempo de retorno promedio
  - Tiempo total de ejecución

## Archivos incluidos

- `round robin.py`: Implementación principal del algoritmo
- `resultados_round_robin.txt`: Resultados de la última ejecución
- `error_round_robin.txt`: Log de errores (si los hay)
- `gantt_chart.png`: Diagrama de Gantt visual de la ejecución
- `metricas_barras.png`: Gráfico de barras con las métricas
- `metricas_completas.png`: Visualización completa de métricas

## Cómo ejecutar

```bash
python "round robin.py"
```

## Ejemplo de uso

El programa solicita:
1. Número de procesos
2. Para cada proceso:
   - Tiempo de llegada
   - Tiempo de ráfaga (burst time)
3. Quantum de tiempo

Luego genera:
- Tabla de resultados
- Métricas calculadas
- Diagrama de Gantt
- Gráficos de visualización

## Métricas

- **Tiempo de espera**: Tiempo que un proceso pasa esperando en la cola
- **Tiempo de respuesta**: Tiempo desde la llegada hasta la primera ejecución
- **Tiempo de retorno**: Tiempo total desde llegada hasta finalización
- **Eficiencia**: Relación entre tiempo útil y tiempo total

Desarrollado como parte del curso de Sistemas Operativos.
