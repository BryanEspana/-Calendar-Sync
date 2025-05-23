"""
Módulo que contiene la clase SyncTab para la pestaña del simulador de mecanismos de sincronización
"""

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
    """
    Clase que maneja la pestaña del simulador de mecanismos de sincronización.
    
    Attributes:
        parent: Widget padre (pestaña)
        processes (dict): Diccionario de procesos cargados por PID
        resources (dict): Diccionario de recursos cargados por nombre
        actions (list): Lista de acciones cargadas
        mechanisms (dict): Diccionario de mecanismos de sincronización
        current_mechanism: Mecanismo seleccionado actualmente
        gantt_chart: Componente para visualizar el diagrama de acciones
    """
    
    def __init__(self, parent):
        """
        Inicializa la pestaña del simulador de mecanismos de sincronización.
        
        Args:
            parent: Widget padre (frame de la pestaña)
        """
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
        self.gantt_chart = GanttChart(gantt_frame)
        
        # Forzar un tamaño mínimo adecuado para el canvas
        self.gantt_chart.canvas.config(width=750, height=300)
        self.gantt_chart.canvas.pack(fill=tk.BOTH, expand=True)
    
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
        """
        Maneja el cambio de mecanismo seleccionado.
        
        Args:
            event: Evento que desencadenó la función
        """
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
        """
        Prepara el historial de ejecución para visualizarlo en el diagrama de Gantt.
        
        Args:
            results (dict): Resultados de la simulación
            
        Returns:
            list: Historial de ejecución adaptado para el diagrama de Gantt
        """
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
                self.gantt_chart = GanttChart(visualization_frame)
                
                # Construir el historial de ejecución basado en las acciones simuladas
                execution_history = self._build_execution_history_from_actions(self.actions)
                
                # Configurar el nuevo diagrama
                max_time = 10  # Mínimo 10 unidades de tiempo
                if execution_history:
                    max_time = max([entry['end_time'] for entry in execution_history] + [max_time])
                
                # Dibujar claramente los bloques de ejecución
                self.gantt_chart.clear()
                self.gantt_chart._draw_timeline(0, max_time)
                
                # Dibujar cada bloque de ejecución con un tamaño más grande y visible
                for item in execution_history:
                    process = item['process']
                    start_time = item['start_time']
                    end_time = item['end_time']
                    state = item['state']
                    
                    # Obtener o asignar color al proceso
                    if not hasattr(process, 'color') or not process.color:
                        # Colores pastel predefinidos
                        pastel_colors = [
                            "#FFB6C1", "#FFD700", "#98FB98", "#87CEFA", "#DDA0DD",
                            "#FFDAB9", "#B0E0E6", "#FFA07A", "#20B2AA", "#F0E68C"
                        ]
                        pid_index = int(process.pid[1:]) if process.pid[0].upper() == 'P' and process.pid[1:].isdigit() else hash(process.pid) % 10
                        process.color = pastel_colors[pid_index % len(pastel_colors)]
                    
                    # Determinar posición vertical basada en el ID del proceso
                    pid_index = int(process.pid[1:]) if process.pid[0].upper() == 'P' and process.pid[1:].isdigit() else 0
                    y_pos = 30 + pid_index * 30
                    
                    # Dibujar el bloque con borde negro y color de relleno
                    x1 = start_time * self.gantt_chart.unit_width
                    x2 = end_time * self.gantt_chart.unit_width
                    y1 = y_pos
                    y2 = y_pos + 25
                    
                    # Ajustar color según el estado
                    block_color = process.color
                    if state == "WAITING":
                        # Usar un tono más claro para estados de espera
                        block_color = self._lighten_color(block_color)
                    
                    # Crear rectángulo con borde más grueso
                    block_id = self.gantt_chart.canvas.create_rectangle(
                        x1, y1, x2, y2, 
                        fill=block_color, outline="black", width=2,
                        tags=f"block_{process.pid}_{start_time}_{end_time}"
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
                
                # Actualizar el canvas
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
        """
        Construye un historial de ejecución a partir de las acciones para visualización.
        
        Args:
            actions (list): Lista de acciones
            
        Returns:
            list: Historial de ejecución para el diagrama de Gantt
        """
        execution_history = []
        
        # Ordenar acciones por ciclo y proceso
        actions_sorted = sorted(actions, key=lambda a: (a.cycle, a.pid))
        
        # Generar entradas para el historial de ejecución
        for action in actions_sorted:
            process = self.processes.get(action.pid)
            if not process:
                continue
                
            # Determinar el estado basado en el estado de la acción
            state = "WAITING"
            if action.state == "COMPLETED":
                state = "ACCESSED"
            elif action.state == "RUNNING":
                state = "ACCESSED"
            
            # Crear la entrada para el historial
            entry = {
                'process': process,
                'start_time': action.cycle,
                'end_time': action.cycle + 1,
                'state': state,
                'action': action
            }
            execution_history.append(entry)
            
        return execution_history
    
    def _lighten_color(self, hex_color):
        """
        Aclara un color hexadecimal para representar estados de espera.
        
        Args:
            hex_color (str): Color hexadecimal (#RRGGBB)
            
        Returns:
            str: Color aclarado
        """
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
