"""
Módulo que contiene la clase SchedulerTab para la pestaña del simulador de calendarización
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.models.process import Process
from src.schedulers.fifo_scheduler import FIFOScheduler
from src.schedulers.sjf_scheduler import SJFScheduler
from src.schedulers.srtf_scheduler import SRTFScheduler
from src.schedulers.round_robin_scheduler import RoundRobinScheduler
from src.schedulers.priority_scheduler import PriorityScheduler
from src.utils.file_loader import load_processes_file, create_sample_files
from src.gui.gantt_chart import GanttChart

class SchedulerTab:
    #Clase que maneja la pestaña del simulador de calendarización.
    
    def __init__(self, parent):
        #Inicializa la pestaña del simulador de calendarización.
        self.parent = parent
        self.processes = []
        
        # Inicializar algoritmos
        self.schedulers = {
            "FIFO": FIFOScheduler(),
            "SJF": SJFScheduler(),
            "SRTF": SRTFScheduler(),
            "Round Robin": RoundRobinScheduler(quantum=2),
            "Priority": PriorityScheduler()
        }
        self.current_scheduler = None
        
        # Crear componentes de la interfaz
        self._create_control_panel()
        self._create_visualization_panel()
        self._create_metrics_panel()
    
    def _create_control_panel(self):
        """Crea el panel de controles para el simulador."""
        # Frame para controles
        control_frame = ttk.LabelFrame(self.parent, text="Controles")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Selector de algoritmo
        ttk.Label(control_frame, text="Algoritmo:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.algorithm_var = tk.StringVar(value="FIFO")
        algorithm_combo = ttk.Combobox(control_frame, textvariable=self.algorithm_var, 
                                      values=list(self.schedulers.keys()))
        algorithm_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        algorithm_combo.bind("<<ComboboxSelected>>", self._on_algorithm_change)
        
        # Control del quantum para Round Robin
        ttk.Label(control_frame, text="Quantum:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.quantum_var = tk.StringVar(value="2")
        quantum_entry = ttk.Entry(control_frame, textvariable=self.quantum_var, width=5)
        quantum_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        quantum_entry.bind("<FocusOut>", self._on_quantum_change)
        
        # Botón para cargar archivos
        ttk.Button(control_frame, text="Cargar Procesos", 
                  command=self._load_processes).grid(row=0, column=4, padx=5, pady=5)
        
        # Botón para iniciar simulación
        ttk.Button(control_frame, text="Iniciar Simulación", 
                  command=self._run_simulation).grid(row=0, column=5, padx=5, pady=5)
        
        # Inicializar con el algoritmo seleccionado
        self._on_algorithm_change(None)
    
    def _create_visualization_panel(self):
        """Crea el panel de visualización para el simulador."""
        # Frame para visualización
        visualization_frame = ttk.LabelFrame(self.parent, text="Simulación")
        visualization_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear el componente de diagrama de Gantt
        self.gantt_chart = GanttChart(visualization_frame)
    
    def _create_metrics_panel(self):
        """Crea el panel de métricas para el simulador."""
        # Frame para métricas
        metrics_frame = ttk.LabelFrame(self.parent, text="Métricas")
        metrics_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Grid para organizar métricas
        metrics_grid = ttk.Frame(metrics_frame)
        metrics_grid.pack(fill=tk.X, padx=5, pady=5)
        
        # Tiempo promedio de espera
        ttk.Label(metrics_grid, text="Tiempo promedio de espera:").grid(
            row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.avg_waiting_time_var = tk.StringVar(value="0.0")
        ttk.Label(metrics_grid, textvariable=self.avg_waiting_time_var).grid(
            row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Tiempo promedio de turnaround
        ttk.Label(metrics_grid, text="Tiempo promedio de turnaround:").grid(
            row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.avg_turnaround_time_var = tk.StringVar(value="0.0")
        ttk.Label(metrics_grid, textvariable=self.avg_turnaround_time_var).grid(
            row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Tiempo total de ejecución
        ttk.Label(metrics_grid, text="Tiempo total de ejecución:").grid(
            row=2, column=0, padx=5, pady=2, sticky=tk.W)
        self.total_time_var = tk.StringVar(value="0")
        ttk.Label(metrics_grid, textvariable=self.total_time_var).grid(
            row=2, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Lista de procesos
        processes_frame = ttk.LabelFrame(metrics_frame, text="Procesos")
        processes_frame.pack(fill=tk.X, padx=5, pady=5, expand=True)
        
        # Treeview para mostrar los procesos y sus métricas
        columns = ("PID", "Burst Time", "Arrival Time", "Priority", 
                  "Waiting Time", "Turnaround Time")
        self.processes_tree = ttk.Treeview(processes_frame, columns=columns, show="headings", height=5)
        
        # Configurar las columnas
        for col in columns:
            self.processes_tree.heading(col, text=col)
            self.processes_tree.column(col, width=100, anchor=tk.CENTER)
        
        # Añadir scrollbar
        scrollbar = ttk.Scrollbar(processes_frame, orient=tk.VERTICAL, command=self.processes_tree.yview)
        self.processes_tree.configure(yscroll=scrollbar.set)
        
        # Posicionar el treeview y scrollbar
        self.processes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _on_algorithm_change(self, event):
        #Maneja el cambio de algoritmo seleccionado.
        algorithm_name = self.algorithm_var.get()
        self.current_scheduler = self.schedulers[algorithm_name]
        
        # Habilitar/deshabilitar el control de quantum según el algoritmo
        if algorithm_name == "Round Robin":
            self.quantum_var.set(str(self.schedulers["Round Robin"].quantum))
        
    def _on_quantum_change(self, event):
        #Maneja el cambio del valor de quantum para Round Robin.
        try:
            quantum = int(self.quantum_var.get())
            if quantum > 0:
                self.schedulers["Round Robin"].set_quantum(quantum)
        except ValueError:
            self.quantum_var.set("2")
    
    def _load_processes(self):
        """Carga procesos desde un archivo seleccionado por el usuario."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de procesos",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                self.processes = load_processes_file(file_path)
                
                # Actualizar la lista de procesos en la interfaz
                self._update_processes_list()
                
                # Mostrar mensaje de éxito
                messagebox.showinfo("Carga exitosa", 
                                   f"Se cargaron {len(self.processes)} procesos correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar procesos: {e}")
    
    def _update_processes_list(self):
        """Actualiza la lista de procesos en la interfaz."""
        # Limpiar la lista actual
        for item in self.processes_tree.get_children():
            self.processes_tree.delete(item)
        
        # Asignar colores a los procesos para consistencia visual
        colors = {}
        for i, process in enumerate(self.processes):
            # Colores pastel predefinidos
            pastel_colors = [
                "#FFB6C1", "#FFD700", "#98FB98", "#87CEFA", "#DDA0DD",
                "#FFDAB9", "#B0E0E6", "#FFA07A", "#20B2AA", "#F0E68C"
            ]
            pid_index = int(process.pid[1:]) if process.pid[0].upper() == 'P' and process.pid[1:].isdigit() else i
            color_index = pid_index % len(pastel_colors)
            process.color = pastel_colors[color_index]
        
        # Añadir los procesos a la lista
        for process in self.processes:
            # Solo mostrar los datos básicos inicialmente
            self.processes_tree.insert("", tk.END, values=(
                process.pid,
                process.burst_time,
                process.arrival_time,
                process.priority,
                "N/A",
                "N/A"
            ), tags=(process.pid,))
            
            # Configurar el color de fondo para la fila
            self.processes_tree.tag_configure(process.pid, background=process.color)
    
    def _update_metrics(self, results):
        #Actualiza las métricas después de ejecutar una simulación.
        # Actualizar variables de métricas
        self.avg_waiting_time_var.set(f"{results['avg_waiting_time']:.2f}")
        self.avg_turnaround_time_var.set(f"{results['avg_turnaround_time']:.2f}")
        self.total_time_var.set(str(results['total_time']))
        
        # Actualizar la lista de procesos con los tiempos calculados
        for item in self.processes_tree.get_children():
            self.processes_tree.delete(item)
        
        for process in results['processes']:
            self.processes_tree.insert("", tk.END, values=(
                process.pid,
                process.burst_time,
                process.arrival_time,
                process.priority,
                process.waiting_time,
                process.turnaround_time
            ), tags=(process.pid,))
            
            # Configurar el color de fondo para la fila
            self.processes_tree.tag_configure(process.pid, background=process.color)
    
    def _run_simulation(self):
        """Ejecuta la simulación con el algoritmo seleccionado."""
        if not self.processes:
            messagebox.showwarning("Advertencia", "No hay procesos cargados. Por favor cargue procesos primero.")
            return
        
        if not self.current_scheduler:
            messagebox.showwarning("Advertencia", "No se ha seleccionado un algoritmo.")
            return
        
        try:
            # Mostrar un mensaje de cargando mientras se ejecuta la simulación
            loading_window = tk.Toplevel(self.parent)
            loading_window.title("Ejecutando simulación")
            loading_window.geometry("300x100")
            loading_window.transient(self.parent)
            loading_window.grab_set()
            loading_label = ttk.Label(loading_window, text="Ejecutando simulación, por favor espere...")
            loading_label.pack(pady=20, padx=20)
            loading_window.update()
            
            # Cargar los procesos en el calendarizador
            self.current_scheduler.load_processes(self.processes)
            
            # Ejecutar la simulación
            results = self.current_scheduler.run_simulation()
            
            # Cerrar ventana de carga
            loading_window.destroy()
            
            # Actualizar métricas
            self._update_metrics(results)
            
            # Reiniciar completamente el componente de diagrama de Gantt para garantizar visibilidad
            visualization_frame = None
            for child in self.parent.winfo_children():
                if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Simulación":
                    visualization_frame = child
                    break
            
            if visualization_frame:
                # Limpiar el frame de visualización
                for child in visualization_frame.winfo_children():
                    child.destroy()
                
                # Crear un nuevo componente de diagrama de Gantt con dimensiones más grandes
                self.gantt_chart = GanttChart(visualization_frame, width=900, height=400, unit_width=50, process_height=40)
                
                # Configurar el diagrama pero sin dibujar nada aún
                self.gantt_chart.clear()
                self.gantt_chart._draw_timeline(0, results['total_time'])
                
                # Añadir etiquetas de procesos primero
                process_ids = set()
                for item in results['execution_history']:
                    process_ids.add(item['process'].pid)
                
                # Dibujar etiquetas de proceso al lado izquierdo
                for pid in process_ids:
                    pid_index = int(pid[1:]) if pid[0].upper() == 'P' and pid[1:].isdigit() else 0
                    y_pos = 30 + pid_index * 40 + 40/2  # Centrado verticalmente
                    
                    self.gantt_chart.canvas.create_text(
                        15, y_pos,
                        text=pid, fill="black",
                        font=("Arial", 12, "bold"),
                        tags=f"label_{pid}"
                    )
                
                # Asignar colores a los procesos
                process_colors = {}
                pastel_colors = [
                    "#FFB6C1", "#FFD700", "#98FB98", "#87CEFA", "#DDA0DD",
                    "#FFDAB9", "#B0E0E6", "#FFA07A", "#20B2AA", "#F0E68C"
                ]
                
                for pid in process_ids:
                    pid_index = int(pid[1:]) if pid[0].upper() == 'P' and pid[1:].isdigit() else 0
                    color_index = pid_index % len(pastel_colors)
                    process_colors[pid] = pastel_colors[color_index]
                
                # Ordenar el historial de ejecución por tiempo de inicio
                sorted_history = sorted(results['execution_history'], key=lambda x: x['start_time'])
                
                # Función para animar paso a paso manualmente
                def animate_step(index=0):
                    if index >= len(sorted_history):
                        # Animación terminada
                        # Usar el after del widget de gantt_chart para mostrar el mensaje
                        self.gantt_chart.after(200, lambda: messagebox.showinfo(
                            "Simulación completada", 
                            f"Simulación completada exitosamente con el algoritmo {self.algorithm_var.get()}.\n\n"
                            f"Tiempo promedio de espera: {results['avg_waiting_time']:.2f}\n"
                            f"Tiempo promedio de turnaround: {results['avg_turnaround_time']:.2f}\n"
                            f"Tiempo total de ejecución: {results['total_time']}"))
                        return
                    
                    # Obtener el siguiente bloque para dibujar
                    item = sorted_history[index]
                    process = item['process']
                    start_time = item['start_time']
                    end_time = item['end_time']
                    
                    # Obtener el color del proceso
                    color = process_colors.get(process.pid, "#CCCCCC")
                    
                    # Calcular posición vertical
                    pid_index = int(process.pid[1:]) if process.pid[0].upper() == 'P' and process.pid[1:].isdigit() else 0
                    y_pos = 30 + pid_index * 40
                    
                    # Dibujar el bloque con borde negro y color de relleno
                    # Usamos label_width para alinear correctamente con la línea de tiempo
                    x1 = start_time * self.gantt_chart.unit_width + self.gantt_chart.label_width
                    x2 = end_time * self.gantt_chart.unit_width + self.gantt_chart.label_width
                    y1 = y_pos
                    y2 = y_pos + 30
                    
                    # Crear rectángulo con borde más grueso
                    block_id = self.gantt_chart.canvas.create_rectangle(
                        x1, y1, x2, y2, 
                        fill=color, outline="black", width=2,
                        tags=f"block_{process.pid}_{start_time}_{end_time}"
                    )
                    
                    # Añadir texto del proceso en el bloque si hay espacio suficiente
                    block_width = x2 - x1
                    if block_width >= 20:
                        self.gantt_chart.canvas.create_text(
                            (x1 + x2) / 2, (y1 + y2) / 2, 
                            text=process.pid, fill="black", 
                            font=("Arial", 10, "bold"), 
                            tags=f"text_{process.pid}_{start_time}_{end_time}"
                        )
                    
                    # Scroll automático para seguir la animación
                    canvas_width = self.gantt_chart.canvas.winfo_width()
                    if end_time * self.gantt_chart.unit_width > canvas_width:
                        self.gantt_chart.canvas.xview_moveto((end_time * self.gantt_chart.unit_width - canvas_width / 2) / 
                                                      (results['total_time'] * self.gantt_chart.unit_width))
                    
                    # Actualizar la interfaz para mostrar el bloque actual
                    self.parent.update()
                    
                    # Programar el siguiente paso con un retraso
                    delay = 500  # milisegundos entre pasos
                    self.gantt_chart.after(delay, lambda: animate_step(index + 1))
                
                # Iniciar la animación manual
                self.gantt_chart.after(100, lambda: animate_step(0))
                
                # Calcular altura total necesaria basada en el número de procesos
                total_height = max(400, len(process_ids) * 40 + 50)  # 40 es la altura por proceso, 50 es espacio extra
                
                # Configurar la región visible del canvas tanto para scroll horizontal como vertical
                self.gantt_chart.canvas.configure(scrollregion=(0, 0, results['total_time'] * self.gantt_chart.unit_width + 50, total_height))
                
                # Forzar actualización de la interfaz
                self.parent.update()
                self.gantt_chart.canvas.update()

            
        except Exception as e:
            # Cerrar ventana de carga si existe
            try:
                loading_window.destroy()
            except:
                pass
                
            import traceback
            error_message = f"Error durante la simulación: {str(e)}\n\n{traceback.format_exc()}"
            messagebox.showerror("Error en simulación", error_message)
            print(error_message)  # También imprimir en consola para depuración:
    
    def _create_examples(self):
        """Crea archivos de ejemplo para procesos."""
        # Seleccionar directorio
        directory = filedialog.askdirectory(title="Seleccionar directorio para archivos de ejemplo")
        
        if directory:
            try:
                # Crear archivos de ejemplo
                files = create_sample_files(directory)
                
                # Mostrar mensaje de éxito
                messagebox.showinfo("Archivos creados", 
                                   f"Archivos de ejemplo creados en:\n{directory}")
                
                # Preguntar si desea cargar el archivo de procesos
                if messagebox.askyesno("Cargar procesos", 
                                      "¿Desea cargar el archivo de procesos de ejemplo?"):
                    self.processes = load_processes_file(files["processes"])
                    self._update_processes_list()
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear archivos de ejemplo: {e}")
