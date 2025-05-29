"""
Módulo que contiene la clase GanttChart para visualizar el diagrama de Gantt
"""

import tkinter as tk
from tkinter import ttk
import random

class GanttChart(ttk.Frame):

    
    def __init__(self, parent, width=800, height=300, unit_width=30, process_height=30):
        #Inicializa el componente para el diagrama de Gantt.

        super().__init__(parent)
        self.parent = parent
        self.width = width
        self.height = height
        self.unit_width = unit_width
        self.process_height = process_height
        self.colors = {}
        self.block_counter = 0 

        # Configurar el frame
        self.pack(fill=tk.BOTH, expand=True)
        
        # Crear el canvas con scrollbars horizontal y vertical
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear canvas
        self.canvas = tk.Canvas(self.canvas_frame, width=width, height=height, background="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar horizontal
        self.h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Scrollbar vertical
        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configurar canvas para usar ambos scrollbars
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        
        # Configurar el frame para que se expanda adecuadamente
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Variables de estado
        self.time_markers = []
        self.current_time = 0
        self.execution_history = []
        self.max_time = 0
        
        # Inicializar el diagrama
        self.clear()
    
    def clear(self):
        """Limpia el diagrama y reinicia las variables de estado."""
        self.canvas.delete("all")
        self.time_markers = []
        self.current_time = 0
        self.execution_history = []
        self.max_time = 0
        self.colors = {}
        self.block_counter = 0
        
        # Dibujar línea de tiempo inicial
        self._draw_timeline(0, 10)
    
    def set_execution_history(self, execution_history, max_time=None):
        #Establece el historial de ejecución completo para animarlo.
        self.execution_history = execution_history
        
        # Calcular tiempo máximo si no se proporciona
        if max_time is None and execution_history:
            max_time = max(item['end_time'] for item in execution_history)
        
        self.max_time = max_time or 10
        
        # Asignar colores a los procesos
        self._assign_colors()
        
        # Calcular la altura necesaria basado en el número de procesos
        process_ids = set()
        for item in self.execution_history:
            process_ids.add(item['process'].pid)
        
        # Calcular altura total necesaria (altura por proceso * número de procesos + espacio extra)
        total_height = max(self.height, len(process_ids) * self.process_height + 50)
        
        # Redimensionar el canvas para acomodar todos los procesos horizontalmente y verticalmente
        self.canvas.configure(scrollregion=(0, 0, self.max_time * self.unit_width + 50, total_height))
        
        # Dibujar la línea de tiempo completa
        self._draw_timeline(0, self.max_time)
    
    def animate_execution(self, speed=1.0, callback=None):
        #Anima la ejecución de los procesos paso a paso.
        if not self.execution_history:
            return
        
        self.clear()
        self._draw_timeline(0, self.max_time)
        self.current_time = 0
        
        # Añadir etiquetas de proceso primero
        self._add_process_labels()
        
        # Ordenar por tiempo de inicio
        sorted_history = sorted(self.execution_history, key=lambda x: x['start_time'])
        
        def animate_step(index=0):
            if index >= len(sorted_history):
                if callback:
                    callback()
                return
            
            item = sorted_history[index]
            self._draw_block_only(item)  # Dibujar solo el bloque sin texto
            self.current_time = item['end_time']
            
            # Actualizar marcador de tiempo actual
            self._draw_time_marker(self.current_time)
            
            # Programar el siguiente paso
            delay = int(1000 / speed)  # Convertir speed a milisegundos
            self.after(delay, lambda: animate_step(index + 1))
        
        # Comenzar la animación
        self.after(100, lambda: animate_step())
    
    def draw_full_execution(self):
        """Dibuja toda la ejecución de una vez, sin animación."""
        # Limpiar el canvas
        self.canvas.delete("block")  # Solo eliminar los bloques, mantener líneas y etiquetas
        
        # Si no hay historial de ejecución, crear algunos datos de ejemplo
        if not self.execution_history:
            print("No hay historial de ejecución, generando datos de ejemplo")
            self._generate_sample_data()
        
        # Añadir etiquetas de procesos (si no existen)
        self._add_process_labels()
        
        # Dibujar cada bloque de ejecución
        for item in self.execution_history:
            self._draw_block_only(item)
        
        # Actualizar el marcador de tiempo al final
        if self.execution_history:
            last_time = max(item['end_time'] for item in self.execution_history)
            self._draw_time_marker(last_time)
            self._ensure_visible(last_time)
    
    def _generate_sample_data(self):
        """Genera datos de ejemplo para visualización cuando no hay datos reales."""
        print("Generando datos de ejemplo para visualización")
        # Encontrar qué procesos están definidos
        processes = set()
        for item in self.execution_history:
            if 'process' in item and item['process']:
                processes.add(item['process'])
        
        # Si no hay procesos definidos, crear datos completamente simulados
        if not processes:
            # Simular 3 procesos de ejemplo con diferentes estados
            self.execution_history = []
            states = ["RUNNING", "WAITING", "BLOCKED", "COMPLETED"]
            
            for pid in range(1, 4):  # 3 procesos de ejemplo
                process = type('', (), {})()  # Objeto simple
                process.pid = f"P{pid}"
                
                for t in range(5):  # 5 ciclos de tiempo
                    state = states[t % len(states)]
                    self.execution_history.append({
                        'process': process,
                        'start_time': t,
                        'end_time': t + 1,
                        'state': state
                    })
        else:
            # Usar los procesos existentes para generar datos
            new_history = []
            for process in processes:
                for t in range(5):  # 5 ciclos de tiempo
                    state = "RUNNING" if t % 2 == 0 else "WAITING"
                    new_history.append({
                        'process': process,
                        'start_time': t,
                        'end_time': t + 1,
                        'state': state
                    })
            
            # Añadir estos datos al historial existente
            self.execution_history.extend(new_history)
    
    def _draw_timeline(self, start_time, end_time):
        #Dibuja la línea de tiempo con marcadores.
        # Línea base
        y_pos = self.height - 20
        self.canvas.create_line(
            0, y_pos, 
            end_time * self.unit_width, y_pos, 
            width=2, fill="black"
        )
        
        # Marcadores de tiempo
        for t in range(start_time, end_time + 1):
            x_pos = t * self.unit_width
            self.canvas.create_line(
                x_pos, y_pos - 5, 
                x_pos, y_pos + 5, 
                width=1, fill="black"
            )
            self.canvas.create_text(
                x_pos, y_pos + 15, 
                text=str(t), fill="black", 
                font=("Arial", 8)
            )
    
    def _draw_time_marker(self, time):
        #Dibuja o actualiza el marcador del tiempo actual.

        # Borrar marcadores anteriores
        self.canvas.delete("time_marker")
        
        # Dibujar nuevo marcador
        x_pos = time * self.unit_width
        self.canvas.create_line(
            x_pos, 0, 
            x_pos, self.height, 
            width=1, fill="red", dash=(4, 4), 
            tags="time_marker"
        )
        
        # Asegurarse de que el marcador sea visible
        self._ensure_visible(time)
    
    def _draw_block_only(self, execution_item):
        #Dibuja solo el bloque de ejecución sin texto.
       
        process = execution_item['process']
        start_time = execution_item['start_time']
        end_time = execution_item['end_time']
        
        # Determinar posición vertical
        pid = process.pid
        # Calcular y_pos basado en el PID
        pid_index = int(pid[1:]) if pid[0].upper() == 'P' and pid[1:].isdigit() else hash(pid) % 10
        y_pos = 30 + pid_index * self.process_height
        
        # Obtener color para el proceso
        if pid not in self.colors:
            self._assign_color(pid)
        color = self.colors[pid]
        
        # Dibujar el bloque
        x1 = start_time * self.unit_width
        x2 = end_time * self.unit_width
        y1 = y_pos
        y2 = y_pos + self.process_height - 5
        
        # Dibujar solo el rectángulo, sin texto
        block_id = self.canvas.create_rectangle(
            x1, y1, x2, y2, 
            fill=color, outline="black", 
            tags=f"proc_{pid}"
        )
        
        # Añadir tooltip al bloque
        self._add_tooltip(block_id, f"{pid}: {start_time} -> {end_time}")
    
    def _add_process_labels(self):
        #Añade etiquetas de texto para cada proceso una sola vez.
        # Encontrar todos los procesos únicos
        process_ids = set()
        for item in self.execution_history:
            process_ids.add(item['process'].pid)
        
        # Para cada proceso, añadir un texto en el centro de su fila
        for pid in process_ids:
            # Calcular posición vertical
            pid_index = int(pid[1:]) if pid[0].upper() == 'P' and pid[1:].isdigit() else hash(pid) % 10
            y_pos = 30 + pid_index * self.process_height + self.process_height / 2 - 2.5
            
            # Añadir texto al final de la línea de tiempo
            x_pos = 10  # Al inicio de la línea
            
            text_id = self.canvas.create_text(
                x_pos, y_pos,
                text=pid, fill="black",
                font=("Arial", 9, "bold"),
                tags=f"label_{pid}"
            )
    
    def _add_tooltip(self, item_id, text):
        #Añade un tooltip a un elemento del canvas.
        
        tooltip = None
        
        def show_tooltip(event):
            nonlocal tooltip
            x, y = event.x + self.canvas.winfo_rootx(), event.y + self.canvas.winfo_rooty()
            tooltip = tk.Toplevel(self)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x+10}+{y+10}")
            label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
            label.pack()
        
        def hide_tooltip(event):
            nonlocal tooltip
            if tooltip:
                tooltip.destroy()
                tooltip = None
        
        self.canvas.tag_bind(item_id, "<Enter>", show_tooltip)
        self.canvas.tag_bind(item_id, "<Leave>", hide_tooltip)
    
    def _ensure_visible(self, time):
        #Asegura que el tiempo indicado sea visible en el canvas.
        
        canvas_width = self.canvas.winfo_width()
        content_width = self.max_time * self.unit_width
        
        # Convertir tiempo a coordenadas normalizadas (0-1)
        x_pos = time * self.unit_width / content_width
        
        # Obtener región visible actual
        visible_left, _ = self.scrollbar.get()
        visible_width = canvas_width / content_width
        
        # Si el tiempo está fuera de la región visible, ajustar
        if x_pos > visible_left + visible_width - 0.1:
            # Desplazar para que el tiempo esté visible
            self.canvas.xview_moveto(max(0, x_pos - visible_width + 0.1))
    
    def _assign_colors(self):
        """Asigna colores a los procesos del historial de ejecución."""
        for item in self.execution_history:
            pid = item['process'].pid
            if pid not in self.colors:
                self._assign_color(pid)
    
    def _assign_color(self, pid):
        #Asigna un color a un proceso específico.
        # Colores pastel predefinidos
        pastel_colors = [
            "#FFB6C1", "#FFD700", "#98FB98", "#87CEFA", "#DDA0DD",
            "#FFDAB9", "#B0E0E6", "#FFA07A", "#20B2AA", "#F0E68C"
        ]
        
        # Asignar un color basado en el índice numérico del PID o un hash
        pid_index = int(pid[1:]) if pid[0].upper() == 'P' and pid[1:].isdigit() else hash(pid)
        color_index = pid_index % len(pastel_colors)
        self.colors[pid] = pastel_colors[color_index]
