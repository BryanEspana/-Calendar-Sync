# Calendar & Sync

Un simulador visual de algoritmos de calendarización (scheduling) y mecanismos de sincronización implementado en Python. Esta herramienta educativa permite visualizar y comprender el funcionamiento de diferentes algoritmos utilizados en sistemas operativos para la gestión de procesos y recursos compartidos.

## 📋 Tabla de Contenidos
- [Características](#características)
- [Instalación](#instalación)
- [Uso](#uso)
- [Algoritmos de Calendarización](#algoritmos-de-calendarización)
- [Mecanismos de Sincronización](#mecanismos-de-sincronización)
- [Formato de Archivos](#formato-de-archivos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)

## ✨ Características

- **Simulador de algoritmos de calendarización:**
  - First-Come-First-Served (FCFS/FIFO)
  - Shortest Job First (SJF)
  - Shortest Remaining Time First (SRTF)
  - Round Robin (RR) con quantum configurable
  - Priority Scheduling (PS)
  
- **Simulador de mecanismos de sincronización:**
  - Mutex (Exclusión Mutua)
  - Semáforos
  
- **Funcionalidades:**
  - Carga dinámica de procesos desde archivos .txt
  - Visualización de la ejecución con diagrama de Gantt
  - Métricas de rendimiento (tiempo de espera, tiempo de retorno)
  - Interfaz gráfica intuitiva con pestañas separadas
  - Exportación de resultados

## 🔧 Instalación

### Prerrequisitos

- Python 3.8 o superior
- tkinter (incluido en la mayoría de instalaciones de Python)
- matplotlib

### Pasos de instalación

1. Clona este repositorio:
```bash
git clone https://github.com/TuUsuario/Calendar-Sync.git
cd Calendar-Sync
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:
```bash
python src/main.py
```

## 🚀 Uso

### Simulador de Calendarización

1. Selecciona un algoritmo de calendarización (FIFO, SJF, SRTF, Round Robin, Priority)
2. Si seleccionas Round Robin, configura el quantum de tiempo
3. Carga procesos desde un archivo .txt o genera ejemplos
4. Haz clic en "Iniciar Simulación"
5. Observa la ejecución en el diagrama de Gantt y las métricas generadas

### Simulador de Sincronización

1. Carga procesos y recursos desde archivos .txt
2. Configura las acciones de sincronización (adquirir/liberar recursos)
3. Selecciona el mecanismo de sincronización (Mutex o Semáforo)
4. Haz clic en "Iniciar Simulación"
5. Observa la ejecución y el estado de los recursos compartidos

## 📊 Algoritmos de Calendarización

### FIFO (First-In-First-Out) / FCFS (First-Come-First-Served)
- **Descripción**: Los procesos se ejecutan en el orden exacto en que llegan a la cola.
- **Características**: Simple de implementar, sin inanición (todos los procesos eventualmente se ejecutan).
- **Desventajas**: Puede causar el efecto "convoy" donde procesos cortos esperan detrás de procesos largos.

### SJF (Shortest Job First)
- **Descripción**: Se ejecuta primero el proceso con el menor tiempo de ejecución total.
- **Características**: Minimiza el tiempo de espera promedio entre todos los algoritmos no apropiativo.
- **Desventajas**: Puede causar inanición para procesos largos si constantemente llegan procesos más cortos.

### SRTF (Shortest Remaining Time First)
- **Descripción**: Versión apropiativa del SJF. Se ejecuta el proceso con menor tiempo restante.
- **Características**: Teóricamente óptimo en términos de tiempo de espera promedio.
- **Desventajas**: Alta sobrecarga por cambios de contexto frecuentes.

### Round Robin (RR)
- **Descripción**: Asigna a cada proceso un quantum (porción) de tiempo de CPU.
- **Funcionamiento**: Los procesos se ejecutan por turnos durante un tiempo fijo (quantum). Si un proceso no termina en su quantum, se coloca al final de la cola.
- **Características**: Distribución justa del tiempo de CPU, bueno para sistemas de tiempo compartido.

### Priority Scheduling
- **Descripción**: Cada proceso tiene asignada una prioridad y se ejecuta según esta.
- **Características**: Permite dar preferencia a procesos críticos o importantes.
- **Desventajas**: Puede causar inanición para procesos de baja prioridad.

## 🔒 Mecanismos de Sincronización

### Mutex (Exclusión Mutua)
- **Descripción**: Mecanismo fundamental para proteger secciones críticas.
- **Funcionamiento**: Actúa como un candado que solo puede ser adquirido por un proceso a la vez.
- **Estados**: Bloqueado (adquirido) o desbloqueado (disponible).

### Semáforos
- **Descripción**: Generalizan el concepto de mutex permitiendo que múltiples procesos accedan a un número limitado de recursos.
- **Operaciones**: P (wait/acquire) y V (signal/release).
- **Tipos**: Semáforo binario (0 o 1) y semáforo contador (cualquier valor entero no negativo).

## 📁 Formato de Archivos

### Formato de Archivo de Procesos
```
P1, 4, 0, 1
P2, 3, 0, 2
P3, 5, 0, 1
P4, 2, 2, 3
```
Donde cada línea tiene el formato: `ID_Proceso, Tiempo_Ejecución, Tiempo_Llegada, Prioridad`

### Formato de Archivo de Recursos
```
R1, 1
R2, 2
```
Donde cada línea tiene el formato: `ID_Recurso, Cantidad_Disponible`

### Formato de Archivo de Acciones
```
P1, ACQUIRE, R1, 1, 2
P1, RELEASE, R1, 1, 5
```
Donde cada línea tiene el formato: `ID_Proceso, Acción, ID_Recurso, Cantidad, Tiempo`

## 📂 Estructura del Proyecto

```
Calendar&Sync/
├── src/                   # Código fuente
│   ├── models/            # Modelos de datos
│   │   ├── process.py     # Clase Process
│   │   ├── resource.py    # Clase Resource
│   │   └── action.py      # Clase Action
│   ├── schedulers/        # Algoritmos de calendarización
│   │   ├── base_scheduler.py        # Clase base para schedulers
│   │   ├── fifo_scheduler.py        # Implementación FIFO
│   │   ├── sjf_scheduler.py         # Implementación SJF
│   │   ├── srtf_scheduler.py        # Implementación SRTF
│   │   ├── round_robin_scheduler.py # Implementación Round Robin
│   │   └── priority_scheduler.py    # Implementación Priority
│   ├── synchronization/   # Mecanismos de sincronización
│   │   ├── base_sync.py             # Clase base para mecanismos
│   │   ├── mutex_sync.py            # Implementación Mutex
│   │   └── semaphore_sync.py        # Implementación Semáforos
│   ├── gui/               # Interfaz gráfica
│   │   ├── scheduler_tab.py         # Pestaña de calendarización
│   │   ├── sync_tab.py              # Pestaña de sincronización
│   │   └── gantt_chart.py           # Componente de diagrama Gantt
│   ├── utils/             # Utilidades
│   │   └── file_loader.py           # Carga de archivos
│   └── main.py            # Punto de entrada de la aplicación
├── data/                  # Archivos de ejemplo
├── txts/                  # Archivos de entrada para simulaciones
├── requirements.txt       # Dependencias del proyecto
└── README.md             # Este archivo
```

## 🛠 Tecnologías Utilizadas

- **Python**: Lenguaje de programación principal
- **tkinter**: Biblioteca para la interfaz gráfica
- **matplotlib**: Biblioteca para visualización de datos y gráficos



Desarrollado como proyecto final para el curso de Sistemas Operativos en la Universidad del Valle de Guatemala (UVG).
