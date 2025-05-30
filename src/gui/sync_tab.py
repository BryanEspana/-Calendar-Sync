#Módulo que contiene la clase SyncTab para la pestaña del simulador de mecanismos de sincronización

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.models.process import Process
from src.models.resource import Resource
from src.models.action import Action
from src.synchronization.mutex_sync import MutexSynchronization
from src.synchronization.semaphore_sync import SemaphoreSynchronization
from src.utils.file_loader import load_processes_file, load_resources_file, load_actions_file, create_sample_files
from src.gui.gantt_chart import GanttChart

class SyncTab:
    #Clase que maneja la pestaña del simulador de mecanismos de sincronización.
    
    def __init__(self, parent):
        #Inicializa la pestaña del simulador de mecanismos de sincronización.
        self.parent = parent
        self.processes = {}
        self.resources = {}
        self.actions = []
        
        # Inicializar mecanismos
        self.mechanisms = {
            "Mutex": MutexSynchronization(),
            "Semáforo": SemaphoreSynchronization()
        }
        self.current_mechanism = self.mechanisms["Mutex"]  # Establecer valor inicial
        
        # Crear componentes de la interfaz
        self._create_control_panel()
        self._create_visualization_panel()
        self._create_info_panel()
    
    def _create_control_panel(self):
        """Crea el panel de controles para el simulador."""
        # Frame para controles
        control_frame = ttk.LabelFrame(self.parent, text="Controles")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Selector de mecanismo
        ttk.Label(control_frame, text="Mecanismo:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.mechanism_var = tk.StringVar(value="Mutex")
        mechanism_combo = ttk.Combobox(control_frame, textvariable=self.mechanism_var, 
                                      values=list(self.mechanisms.keys()))
        mechanism_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        mechanism_combo.bind("<<ComboboxSelected>>", self._on_mechanism_change)
        
        # Botones para cargar archivos
        ttk.Button(control_frame, text="Cargar Procesos", 
                  command=self._load_processes).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(control_frame, text="Cargar Recursos", 
                  command=self._load_resources).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(control_frame, text="Cargar Acciones", 
                  command=self._load_actions).grid(row=0, column=4, padx=5, pady=5)
        
        # Botón para iniciar simulación
        ttk.Button(control_frame, text="Iniciar Simulación", 
                  command=self._run_simulation).grid(row=0, column=5, padx=5, pady=5)
        
        # Inicializar con el mecanismo seleccionado
        self._on_mechanism_change(None)
    
    def _create_visualization_panel(self):
        """Crea el panel de visualización para el simulador."""
        # Frame para visualización
        visualization_frame = ttk.LabelFrame(self.parent, text="Simulación")
        visualization_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear una etiqueta informativa
        ttk.Label(visualization_frame, 
                 text="Diagrama de Gantt: Cada fila representa un proceso y sus acciones en el tiempo").pack(pady=5)
        
        # Frame para contener el diagrama
        gantt_frame = ttk.Frame(visualization_frame)
        gantt_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear el componente de diagrama de Gantt para visualizar las acciones
        self.gantt_chart = GanttChart(gantt_frame, width=1200, height=600, unit_width=80, process_height=60)
        
        # En lugar de pack, usamos grid para el componente gantt_chart
        # ya que internamente GanttChart usa grid para sus componentes
        self.gantt_chart.grid(row=0, column=0, sticky="nsew")
        
        # Configurar el frame para que se expanda correctamente
        gantt_frame.grid_rowconfigure(0, weight=1)
        gantt_frame.grid_columnconfigure(0, weight=1)
    
    def _create_info_panel(self):
        """Crea el panel de información para el simulador."""
        # Frame para información
        info_frame = ttk.LabelFrame(self.parent, text="Información")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Crear notebook para pestañas de procesos, recursos y acciones
        notebook = ttk.Notebook(info_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña de procesos
        processes_frame = ttk.Frame(notebook)
        notebook.add(processes_frame, text="Procesos")
        
        # Treeview para mostrar los procesos
        columns_p = ("PID", "Burst Time", "Arrival Time", "Priority")
        self.processes_tree = ttk.Treeview(processes_frame, columns=columns_p, show="headings", height=5)
        
        # Configurar las columnas
        for col in columns_p:
            self.processes_tree.heading(col, text=col)
            self.processes_tree.column(col, width=100, anchor=tk.CENTER)
        
        # Añadir scrollbar
        scrollbar_p = ttk.Scrollbar(processes_frame, orient=tk.VERTICAL, command=self.processes_tree.yview)
        self.processes_tree.configure(yscroll=scrollbar_p.set)
        
        # Posicionar el treeview y scrollbar
        self.processes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_p.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pestaña de recursos
        resources_frame = ttk.Frame(notebook)
        notebook.add(resources_frame, text="Recursos")
        
        # Treeview para mostrar los recursos
        columns_r = ("Nombre", "Contador")
        self.resources_tree = ttk.Treeview(resources_frame, columns=columns_r, show="headings", height=5)
        
        # Configurar las columnas
        for col in columns_r:
            self.resources_tree.heading(col, text=col)
            self.resources_tree.column(col, width=100, anchor=tk.CENTER)
        
        # Añadir scrollbar
        scrollbar_r = ttk.Scrollbar(resources_frame, orient=tk.VERTICAL, command=self.resources_tree.yview)
        self.resources_tree.configure(yscroll=scrollbar_r.set)
        
        # Posicionar el treeview y scrollbar
        self.resources_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_r.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pestaña de acciones
        actions_frame = ttk.Frame(notebook)
        notebook.add(actions_frame, text="Acciones")
        
        # Treeview para mostrar las acciones
        columns_a = ("PID", "Acción", "Recurso", "Ciclo", "Estado")
        self.actions_tree = ttk.Treeview(actions_frame, columns=columns_a, show="headings", height=5)
        
        # Configurar las columnas
        for col in columns_a:
            self.actions_tree.heading(col, text=col)
            self.actions_tree.column(col, width=100, anchor=tk.CENTER)
        
        # Añadir scrollbar
        scrollbar_a = ttk.Scrollbar(actions_frame, orient=tk.VERTICAL, command=self.actions_tree.yview)
        self.actions_tree.configure(yscroll=scrollbar_a.set)
        
        # Posicionar el treeview y scrollbar
        self.actions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_a.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _on_mechanism_change(self, event):
        #Maneja el cambio de mecanismo seleccionado.
        mechanism_name = self.mechanism_var.get()
        self.current_mechanism = self.mechanisms[mechanism_name]
    
    def _load_processes(self):
        """Carga procesos desde un archivo seleccionado por el usuario."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de procesos",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                processes = load_processes_file(file_path)
                self.processes = {process.pid: process for process in processes}
                
                # Actualizar la lista de procesos en la interfaz
                self._update_processes_list()
                
                # Mostrar mensaje de éxito
                messagebox.showinfo("Carga exitosa", 
                                   f"Se cargaron {len(processes)} procesos correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar procesos: {e}")
    
    def _load_resources(self):
        """Carga recursos desde un archivo seleccionado por el usuario."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de recursos",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                resources = load_resources_file(file_path)
                self.resources = {resource.name: resource for resource in resources}
                
                # Actualizar la lista de recursos en la interfaz
                self._update_resources_list()
                
                # Mostrar mensaje de éxito
                messagebox.showinfo("Carga exitosa", 
                                   f"Se cargaron {len(resources)} recursos correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar recursos: {e}")
    
    def _load_actions(self):
        """Carga acciones desde un archivo seleccionado por el usuario."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de acciones",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                self.actions = load_actions_file(file_path)
                
                # Actualizar la lista de acciones en la interfaz
                self._update_actions_list()
                
                # Mostrar mensaje de éxito
                messagebox.showinfo("Carga exitosa", 
                                   f"Se cargaron {len(self.actions)} acciones correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar acciones: {e}")
    
    def _update_processes_list(self):
        """Actualiza la lista de procesos en la interfaz."""
        # Limpiar la lista actual
        for item in self.processes_tree.get_children():
            self.processes_tree.delete(item)
        
        # Añadir los procesos a la lista
        for pid, process in self.processes.items():
            self.processes_tree.insert("", tk.END, values=(
                process.pid,
                process.burst_time,
                process.arrival_time,
                process.priority
            ))
    
    def _update_resources_list(self):
        """Actualiza la lista de recursos en la interfaz."""
        # Limpiar la lista actual
        for item in self.resources_tree.get_children():
            self.resources_tree.delete(item)
        
        # Añadir los recursos a la lista
        for name, resource in self.resources.items():
            self.resources_tree.insert("", tk.END, values=(
                resource.name,
                resource.counter
            ))
    
    def _update_actions_list(self):
        """Actualiza la lista de acciones en la interfaz."""
        # Limpiar la lista actual
        for item in self.actions_tree.get_children():
            self.actions_tree.delete(item)
        
        # Añadir las acciones a la lista, ordenadas por ciclo
        sorted_actions = sorted(self.actions, key=lambda a: a.cycle)
        for action in sorted_actions:
            self.actions_tree.insert("", tk.END, values=(
                action.pid,
                action.action_type,
                action.resource_name,
                action.cycle,
                action.state
            ))
    
    def _prepare_execution_history(self, results):
        #Prepara el historial de ejecución para visualizarlo en el diagrama de Gantt.
        execution_history = []
        
        for cycle_info in results['execution_history']:
            cycle = cycle_info['cycle']
            
            for action_info in cycle_info['actions']:
                action = action_info['action']
                process = self.processes.get(action.pid)
                
                if not process:
                    continue
                
                # Crear una entrada compatible con el diagrama de Gantt
                entry = {
                    'process': process,
                    'start_time': cycle,
                    'end_time': cycle + 1,
                    'state': "ACCESSED" if action_info['success'] else "WAITING",
                    'action': action
                }
                execution_history.append(entry)
        
        return execution_history
    
    def _run_simulation(self):
        """Ejecuta la simulación con el mecanismo seleccionado."""
        if not self.processes:
            messagebox.showwarning("Advertencia", "No hay procesos cargados. Por favor cargue procesos primero.")
            return
        
        if not self.resources:
            messagebox.showwarning("Advertencia", "No hay recursos cargados. Por favor cargue recursos primero.")
            return
        
        if not self.actions:
            messagebox.showwarning("Advertencia", "No hay acciones cargadas. Por favor cargue acciones primero.")
            return
        
        if not self.current_mechanism:
            messagebox.showwarning("Advertencia", "No se ha seleccionado un mecanismo de sincronización.")
            return
            
        try:
            # Cargar los datos en el mecanismo de sincronización
            self.current_mechanism.load_processes(list(self.processes.values()))
            self.current_mechanism.load_resources(list(self.resources.values()))
            self.current_mechanism.load_actions(self.actions)
            
            # Ejecutar la simulación
            results = self.current_mechanism.run_simulation(max_cycles=100)
            
            # Actualizar la lista de acciones con los nuevos estados
            self._update_actions_list()
            
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
                
                # Crear un nuevo componente de diagrama de Gantt
                self.gantt_chart = GanttChart(visualization_frame, width=1200, height=600, unit_width=80, process_height=60)
                
                # Construir el historial de ejecución basado en las acciones simuladas
                execution_history = self._build_execution_history_from_actions(self.actions)
                
                # Configurar el nuevo diagrama
                max_time = 10  # Mínimo 10 unidades de tiempo
                if execution_history:
                    max_time = max([entry['end_time'] for entry in execution_history] + [max_time])
                
                # Dibujar claramente los bloques de ejecución
                self.gantt_chart.clear()
                self.gantt_chart._draw_timeline(0, max_time)
                
                # Organizar recursos y procesos
                process_rows = {}  # Mapeo de ID de proceso a fila
                resource_rows = {}  # Mapeo de nombre de recurso a fila
                
                # Primero, recopilar todos los procesos y recursos únicos
                processes = set()
                resources = set()
                
                for item in execution_history:
                    if 'is_resource' in item and item['is_resource']:
                        resources.add(item['resource_name'])
                    elif 'is_process_action' in item and item['is_process_action']:
                        processes.add(item['process'].pid)
                
                # Si no hay procesos en el historial (no hay acciones detectadas), usar los procesos cargados
                if not processes and self.processes:
                    for pid in self.processes.keys():
                        processes.add(pid)
                
                # Asignar filas - primero recursos, luego procesos
                row = 0
                
                # Crear encabezado para recursos en el área fija
                header_y = 40
                self.gantt_chart.canvas.create_text(
                    self.gantt_chart.label_width/2, header_y, text="RECURSOS", 
                    font=("Arial", 18, "bold"), anchor="center", fill="black",
                    tags="fixed_header"
                )
                
                resource_start_y = 70  # Posición inicial de los recursos
                row = 0
                for resource in sorted(resources):
                    resource_rows[resource] = row
                    y_pos = resource_start_y + row * 70
                    
                    # Crear etiqueta del recurso en la columna fija
                    self.gantt_chart.canvas.create_text(
                        self.gantt_chart.label_width/2, y_pos + 25, 
                        text=resource, font=("Arial", 16, "bold"), 
                        anchor="center", fill="black", tags="fixed_label"
                    )
                    row += 1
                
                # Calcular posición para el encabezado de procesos
                process_start_y = resource_start_y + (len(resources) * 70) + 50
                
                # Crear encabezado para procesos con un poco de espacio
                self.gantt_chart.canvas.create_text(
                    self.gantt_chart.label_width/2, process_start_y - 30, text="PROCESOS", 
                    font=("Arial", 18, "bold"), anchor="center", fill="black",
                    tags="fixed_header"
                )
                
                # Asignar filas para procesos
                row = 0
                for process in sorted(processes):
                    process_rows[process] = row
                    y_pos = process_start_y + row * 70
                    
                    # Crear etiqueta del proceso en la columna fija
                    self.gantt_chart.canvas.create_text(
                        self.gantt_chart.label_width/2, y_pos + 25, 
                        text=process, font=("Arial", 16, "bold"), 
                        anchor="center", fill="black", tags="fixed_label"
                    )
                    row += 1
                
                # Ya hemos asignado las filas para los procesos arriba
                
                # Ahora dibujamos cada elemento
                for item in execution_history:
                    if 'is_resource' in item and item['is_resource']:
                        # Dibujar estado del recurso
                        resource_name = item['resource_name']
                        start_time = item['start_time']
                        end_time = item['end_time']
                        
                        # Posición vertical basada en la fila asignada
                        row = resource_rows[resource_name]
                        y_pos = resource_start_y + row * 70
                        
                        # Coordenadas del bloque con desplazamiento para el área de etiquetas
                        x1 = (start_time * self.gantt_chart.unit_width) + self.gantt_chart.label_width
                        x2 = (end_time * self.gantt_chart.unit_width) + self.gantt_chart.label_width
                        y1 = y_pos
                        y2 = y_pos + 50
                        
                        # Color basado en si está en uso o libre
                        if item['using_processes']:
                            # Recurso en uso
                            block_color = "#FFDAB9"  # Color para recurso en uso
                            # Agregar borde más grueso si hay procesos esperando
                            border_width = 3 if item['waiting_processes'] else 1
                            border_color = "red" if item['waiting_processes'] else "black"
                        else:
                            # Recurso libre
                            block_color = "#98FB98"  # Color para recurso libre
                            border_width = 1
                            border_color = "black"
                        
                        # Crear rectángulo para el recurso
                        block_id = self.gantt_chart.canvas.create_rectangle(
                            x1, y1, x2, y2, 
                            fill=block_color, outline=border_color, width=border_width,
                            tags=f"resource_{resource_name}_{start_time}"
                        )
                        
                        # No necesitamos crear etiquetas a la izquierda, ya las creamos antes
                        
                        # Texto dentro del bloque en formato multilínea
                        using_text = item['display_text']
                        
                        # Si el texto contiene ':', separarlo en dos líneas
                        if ':' in using_text:
                            parts = using_text.split(':', 1)
                            action_type = parts[0].strip()
                            processes = parts[1].strip()
                            
                            # Dibujar el tipo de acción en la primera línea (más arriba)
                            self.gantt_chart.canvas.create_text(
                                (x1 + x2) / 2, (y1 + y2) / 2 - 15, 
                                text=action_type, 
                                font=("Arial", 14, "bold"), 
                                fill="black"
                            )
                            
                            # Dibujar los procesos en la segunda línea (más abajo)
                            self.gantt_chart.canvas.create_text(
                                (x1 + x2) / 2, (y1 + y2) / 2 + 15, 
                                text=processes, 
                                font=("Arial", 12), 
                                fill="black"
                            )
                        else:
                            # Si es "Libre", mostrarlo un poco más abajo para evitar superposiciones
                            y_offset = 0  # Posición vertical predeterminada
                            
                            # Si el texto es "Libre", ajustar la posición vertical
                            if using_text == "Libre":
                                y_offset = 10
                                
                            # Mostrar el texto en el centro con posible ajuste vertical
                            self.gantt_chart.canvas.create_text(
                                (x1 + x2) / 2, (y1 + y2) / 2 + y_offset, 
                                text=using_text, 
                                font=("Arial", 14, "bold"), 
                                fill="black"
                            )
                        
                        # Si hay procesos esperando, mostrar indicador
                        if item['waiting_processes']:
                            waiting_text = f"Esperando: {', '.join(item['waiting_processes'])}"
                            self.gantt_chart.canvas.create_text(
                                (x1 + x2) / 2, y2 + 15, 
                                text=waiting_text, 
                                font=("Arial", 14), 
                                fill="red"
                            )
                    
                    elif 'is_process_action' in item and item['is_process_action']:
                        # Dibujar acciones de procesos
                        process = item['process']
                        start_time = item['start_time']
                        end_time = item['end_time']
                        state = item['state']
                        
                        # Obtener o asignar color al proceso
                        if not hasattr(process, 'color') or not process.color:
                            # Colores predefinidos
                            process_colors = [
                                "#FFB6C1", "#FFD700", "#87CEFA", "#DDA0DD",
                                "#B0E0E6", "#FFA07A", "#20B2AA", "#F0E68C"
                            ]
                            pid_index = int(process.pid[1:]) if process.pid[0].upper() == 'P' and process.pid[1:].isdigit() else hash(process.pid) % 8
                            process.color = process_colors[pid_index % len(process_colors)]
                        
                        # Posición vertical basada en la fila asignada
                        row = process_rows[process.pid]
                        y_pos = process_start_y + row * 70
                        
                        # Coordenadas del bloque con desplazamiento para el área de etiquetas
                        x1 = (start_time * self.gantt_chart.unit_width) + self.gantt_chart.label_width
                        x2 = (end_time * self.gantt_chart.unit_width) + self.gantt_chart.label_width
                        y1 = y_pos
                        y2 = y_pos + 50
                        
                        # Ajustar color según el estado
                        block_color = process.color
                        if state == "WAITING":
                            # Usar un tono más claro para estados de espera
                            block_color = self._lighten_color(block_color)
                            border_color = "red"
                        else:
                            border_color = "black"
                        
                        # Crear rectángulo con borde más grueso
                        block_id = self.gantt_chart.canvas.create_rectangle(
                            x1, y1, x2, y2, 
                            fill=block_color, outline=border_color, width=2,
                            tags=f"block_{process.pid}_{start_time}_{end_time}"
                        )
                        
                        # No necesitamos crear etiquetas a la izquierda, ya las creamos antes
                        
                        # Mostrar el ID del proceso en el bloque (parte superior)
                        self.gantt_chart.canvas.create_text(
                            (x1 + x2) / 2, (y1 + y2) / 2 - 15, 
                            text=process.pid, 
                            font=("Arial", 14, "bold"), 
                            fill="black"
                        )
                        
                        # Mostrar acción ejecutada dentro del bloque (parte inferior)
                        action_info = item['action']
                        action_text = f"{action_info.action_type} {action_info.resource_name}"
                        self.gantt_chart.canvas.create_text(
                            (x1 + x2) / 2, (y1 + y2) / 2 + 15, 
                            text=action_text, 
                            font=("Arial", 12), 
                            fill="black"
                        )
                    
                    # Añadir texto del proceso en el bloque si hay suficiente espacio
                    block_width = x2 - x1
                    if block_width >= 20:  # Solo mostrar texto si hay suficiente espacio
                        self.gantt_chart.canvas.create_text(
                            (x1 + x2) / 2, (y1 + y2) / 2, 
                            text=process.pid, fill="black", 
                            font=("Arial", 10, "bold"), 
                            tags=f"text_{process.pid}_{start_time}_{end_time}"  # Tag único para evitar superposición
                        )
                
                # Añadir etiquetas para los procesos al lado izquierdo
                # NOTA: Se han eliminado las etiquetas de texto a petición del usuario
                
                # Ajustar la región de desplazamiento del canvas para mostrar todo el contenido
                total_rows = len(processes) + len(resources) + 2  # +2 para los encabezados
                canvas_height = process_start_y + (len(processes) * 70) + 50  # altura adicional para márgenes
                
                # Definir la región de desplazamiento incluyendo el área de etiquetas
                self.gantt_chart.canvas.config(scrollregion=(0, 0, 
                                                           (max_time * self.gantt_chart.unit_width) + self.gantt_chart.label_width + 150, 
                                                           canvas_height))
                
                # Crear una línea vertical para separar el área de etiquetas y el área de bloques
                self.gantt_chart.canvas.create_line(
                    self.gantt_chart.label_width, 0, 
                    self.gantt_chart.label_width, canvas_height,
                    fill="gray", width=2, tags="separator_line"
                )
                
                self.gantt_chart.canvas.update()
            
            # Mostrar un mensaje de confirmación
            messagebox.showinfo("Simulación Completada", 
                              f"Simulación completada exitosamente.\nAcciones completadas: {results['completed_actions']}/{results['total_actions']}")
                              
        except Exception as e:
            # Mostrar error detallado
            import traceback
            error_msg = f"Error al ejecutar la simulación: {e}\n\n{traceback.format_exc()}"
            print(error_msg)
            messagebox.showerror("Error en la Simulación", error_msg)
    
    def _build_execution_history_from_actions(self, actions):
        """Construye un historial de ejecución a partir de las acciones para visualización."""
        execution_history = []
        
        # Ordenar acciones por ciclo y proceso
        actions_sorted = sorted(actions, key=lambda a: (a.cycle, a.pid))
        
        # Encontrar el ciclo máximo para dimensionar nuestras estructuras de datos
        max_cycle = max([a.cycle for a in actions_sorted]) if actions_sorted else 5
        
        # Crear un diccionario para mantener el estado de los recursos por ciclo
        resources_state = {}
        
        # Inicializar el estado de los recursos en cada ciclo
        for cycle in range(max_cycle + 2):  # +1 para incluir el último ciclo, +1 para el fin de la última acción
            for resource_name, resource in self.resources.items():
                key = (resource_name, cycle)
                
                # Estado inicial del recurso
                if cycle == 0:
                    resources_state[key] = {
                        'resource_name': resource_name,
                        'start_time': cycle,
                        'end_time': cycle + 1,
                        'using_processes': [],
                        'waiting_processes': [],
                        'is_resource': True,
                        'display_text': 'Libre'
                    }
                else:
                    # Copiar el estado del ciclo anterior
                    prev_key = (resource_name, cycle - 1)
                    prev_state = resources_state.get(prev_key)
                    
                    # Si no existe estado anterior, crear uno por defecto
                    if not prev_state:
                        prev_state = {
                            'resource_name': resource_name,
                            'using_processes': [],
                            'waiting_processes': [],
                            'is_resource': True,
                            'display_text': 'Libre'
                        }
                    
                    # Crear el estado actual como copia del anterior
                    resources_state[key] = {
                        'resource_name': resource_name,
                        'start_time': cycle,
                        'end_time': cycle + 1,
                        'using_processes': prev_state['using_processes'][:],  # Copiar lista
                        'waiting_processes': prev_state['waiting_processes'][:],  # Copiar lista
                        'is_resource': True,
                        'display_text': prev_state['display_text']
                    }
        
        # Procesar las acciones para actualizar estados
        for action in actions_sorted:
            process = self.processes.get(action.pid)
            if not process:
                continue
            
            # Determinar el estado basado en el estado de la acción
            state = "WAITING"
            if action.state == "COMPLETED" or action.state == "RUNNING":
                state = "ACCESSED"
            
            # Crear la entrada para el historial de la acción del proceso
            entry = {
                'process': process,
                'start_time': action.cycle,
                'end_time': action.cycle + 1,
                'state': state,
                'action': action,
                'is_process_action': True  # Marcar que es una acción de proceso
            }
            execution_history.append(entry)
            
            # Actualizar el estado del recurso correspondiente
            resource_name = action.resource_name
            cycle = action.cycle
            key = (resource_name, cycle)
            
            if resource_name in self.resources and key in resources_state:
                resource_state = resources_state[key]
                
                # Actualizar el estado según si la acción se completó o está esperando
                if state == "ACCESSED":
                    # El proceso accedió al recurso
                    if process.pid not in resource_state['using_processes']:
                        resource_state['using_processes'].append(process.pid)
                    
                    # Actualizar el texto que se mostrará en el bloque
                    action_type = action.action_type
                    using_procs = resource_state['using_processes']
                    resource_state['display_text'] = f"{action_type}: {', '.join(using_procs)}"
                    
                    # Quitar de la lista de espera si estaba
                    if process.pid in resource_state['waiting_processes']:
                        resource_state['waiting_processes'].remove(process.pid)
                else:
                    # El proceso está esperando por el recurso
                    if process.pid not in resource_state['waiting_processes']:
                        resource_state['waiting_processes'].append(process.pid)
        
        # Añadir todos los estados de recursos al historial
        for key, state in resources_state.items():
            execution_history.append(state)
        
        return execution_history
    
    def _lighten_color(self, hex_color):
        #Aclara un color hexadecimal para representar estados de espera.
        # Convertir hex a RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Aclarar (mezclar con blanco)
        r = int(r * 0.5 + 255 * 0.5)
        g = int(g * 0.5 + 255 * 0.5)
        b = int(b * 0.5 + 255 * 0.5)
        
        # Convertir de vuelta a hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _create_examples(self):
        """Crea archivos de ejemplo para procesos, recursos y acciones."""
        # Seleccionar directorio
        directory = filedialog.askdirectory(title="Seleccionar directorio para archivos de ejemplo")
        
        if directory:
            try:
                # Crear archivos de ejemplo
                files = create_sample_files(directory)
                
                # Mostrar mensaje de éxito
                messagebox.showinfo("Archivos creados", 
                                   f"Archivos de ejemplo creados en:\n{directory}")
                
                # Preguntar si desea cargar los archivos de ejemplo
                if messagebox.askyesno("Cargar archivos", 
                                      "¿Desea cargar los archivos de ejemplo?"):
                    # Cargar procesos
                    processes = load_processes_file(files["processes"])
                    self.processes = {process.pid: process for process in processes}
                    self._update_processes_list()
                    
                    # Cargar recursos
                    resources = load_resources_file(files["resources"])
                    self.resources = {resource.name: resource for resource in resources}
                    self._update_resources_list()
                    
                    # Cargar acciones
                    self.actions = load_actions_file(files["actions"])
                    self._update_actions_list()
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear archivos de ejemplo: {e}")
