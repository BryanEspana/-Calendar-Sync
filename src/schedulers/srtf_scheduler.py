"""
Módulo que contiene la implementación del algoritmo de calendarización SRTF (Shortest Remaining Time First)
"""

from src.schedulers.base_scheduler import BaseScheduler

class SRTFScheduler(BaseScheduler):
    """
    Implementación del algoritmo de calendarización SRTF (Shortest Remaining Time First).
    Similar al SJF, pero es preemptivo - interrumpe la ejecución si llega un proceso 
    con menor tiempo restante.
    """
    
    def __init__(self):
        """Inicializa un nuevo calendarizador SRTF."""
        super().__init__("SRTF")
    
    def update_queues(self):
        """
        Actualiza las colas de procesos basado en el tiempo actual.
        Agrega a la ready_queue los procesos que han llegado al sistema.
        """
        # Agregar procesos recién llegados
        for process in self.processes:
            # Si el proceso ha llegado y no está en ninguna cola ni ha terminado
            if (process.arrival_time <= self.current_time and 
                process not in self.ready_queue and 
                process not in self.completed_processes and
                process != self.current_process):
                self.ready_queue.append(process)
        
        # Si hay un proceso en ejecución, verificar si debe ser interrumpido
        if self.current_process and self.current_process.remaining_time > 0:
            # Añadir el proceso actual a la cola para comparar con los demás
            if self.current_process not in self.ready_queue:
                self.ready_queue.append(self.current_process)
        
        # Ordenar la cola por tiempo restante
        self.ready_queue.sort(key=lambda p: p.remaining_time)
    
    def get_next_process(self):
        """
        Obtiene el siguiente proceso a ejecutar según el algoritmo SRTF.
        
        Returns:
            Process: El siguiente proceso a ejecutar o None si no hay procesos disponibles
        """
        # En SRTF, siempre seleccionamos el proceso con menor tiempo restante
        if self.ready_queue:
            return self.ready_queue[0]
        
        return None
    
    def execute_cycle(self):
        """
        Ejecuta un ciclo de la simulación para SRTF.
        A diferencia de otros algoritmos, SRTF ejecuta en unidades de tiempo de 1.
        
        Returns:
            bool: True si la simulación debe continuar, False si ha terminado
        """
        # Actualizar colas con nuevos procesos que llegaron en este ciclo
        self.update_queues()
        
        # Obtener el proceso con menor tiempo restante
        self.current_process = self.get_next_process()
        
        # Si no hay procesos para ejecutar pero quedan procesos por completar,
        # avanzar el tiempo y continuar
        if self.current_process is None:
            if len(self.completed_processes) < len(self.processes):
                self.current_time += 1
                return True
            else:
                return False  # Simulación terminada
        
        # Incrementar tiempo de espera para procesos en ready_queue
        for process in self.ready_queue:
            if process != self.current_process:
                process.wait()
        
        # Eliminar el proceso actual de la cola de listos mientras se ejecuta
        if self.current_process in self.ready_queue:
            self.ready_queue.remove(self.current_process)
        
        # Ejecutar el proceso actual por una unidad de tiempo
        time_executed = self.current_process.execute(1)
        
        # Registrar ejecución para el diagrama de Gantt
        self.execution_history.append({
            'process': self.current_process,
            'start_time': self.current_time,
            'end_time': self.current_time + time_executed
        })
        
        # Si el proceso comienza su ejecución por primera vez
        if self.current_process.start_time is None:
            self.current_process.set_start_time(self.current_time)
        
        # Avanzar el tiempo
        self.current_time += time_executed
        
        # Si el proceso ha terminado, moverlo a la lista de completados
        if self.current_process.state == "TERMINATED":
            self.current_process.set_finish_time(self.current_time)
            if self.current_process not in self.completed_processes:
                self.completed_processes.append(self.current_process)
        
        return len(self.completed_processes) < len(self.processes)
