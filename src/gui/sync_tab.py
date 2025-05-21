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
        self.current_mechanism = None
        
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
        
        # Botón para generar archivos de ejemplo
        ttk.Button(control_frame, text="Generar Ejemplos", 
                  command=self._create_examples).grid(row=0, column=6, padx=5, pady=5)
        
        # Inicializar con el mecanismo seleccionado
        self._on_mechanism_change(None)
    
    def _create_visualization_panel(self):
        """Crea el panel de visualización para el simulador."""
        # Frame para visualización
        visualization_frame = ttk.LabelFrame(self.parent, text="Simulación")
        visualization_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear el componente de diagrama de Gantt para visualizar las acciones
        self.gantt_chart = GanttChart(visualization_frame)
    
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
        
        # Cargar los datos en el mecanismo de sincronización
        self.current_mechanism.load_processes(list(self.processes.values()))
        self.current_mechanism.load_resources(list(self.resources.values()))
        self.current_mechanism.load_actions(self.actions)
        
        # Ejecutar la simulación
        results = self.current_mechanism.run_simulation(max_cycles=100)
        
        # Actualizar la lista de acciones con los nuevos estados
        self._update_actions_list()
        
        # Preparar el historial de ejecución para el diagrama de Gantt
        execution_history = self._prepare_execution_history(results)
        
        # Actualizar el diagrama de Gantt
        self.gantt_chart.set_execution_history(execution_history, results['total_time'])
        self.gantt_chart.animate_execution(speed=1.0)
    
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
