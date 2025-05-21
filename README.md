# Calendar & Sync

Un simulador visual de algoritmos de calendarización y mecanismos de sincronización implementado en Python.

## Características
- Simulador de algoritmos de calendarización (FIFO, SJF, SRTF, RR, Priority)
- Simulador de mecanismos de sincronización (Mutex, Semáforos)
- Carga dinámica de procesos desde archivos .txt
- Visualización en tiempo real con diagrama de Gantt
- Interfaz gráfica amigable e intuitiva

## Estructura del proyecto
```
Calendar&Sync/
├── src/                   # Código fuente
│   ├── models/            # Modelos de datos
│   ├── schedulers/        # Algoritmos de calendarización
│   ├── synchronization/   # Mecanismos de sincronización
│   ├── gui/               # Interfaz gráfica
│   └── utils/             # Utilidades
├── data/                  # Archivos de ejemplo
├── docs/                  # Documentación
└── tests/                 # Pruebas unitarias
```

## Requisitos
- Python 3.8+
- tkinter
- matplotlib
