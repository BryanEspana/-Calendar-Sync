"""
Módulo que contiene la implementación del algoritmo de calendarización Round Robin
"""

from collections import deque
from src.schedulers.base_scheduler import BaseScheduler

class RoundRobinScheduler(BaseScheduler):
    """
    Implementación del algoritmo de calendarización Round Robin.
    Cada proceso se ejecuta por un quantum de tiempo, luego cede el CPU al siguiente proceso.
    """
    
    def __init__(self, quantum=2):
        """
        Inicializa un nuevo calendarizador Round Robin.
        
        Args:
            quantum (int, optional): Quantum de tiempo para cada proceso. Defaults to 2.
        """
        super().__init__("Round Robin")
        self.quantum = quantum
        self.process_queue = deque()
    
    def set_quantum(self, quantum):
        """
        Establece el quantum de tiempo para el algoritmo.
        
        Args:
            quantum (int): Nuevo quantum de tiempo
        """
        self.quantum = int(quantum)
    
    def update_queues(self):
        """
        Actualiza las colas de procesos basado en el tiempo actual.
        Agrega a la process_queue los procesos que han llegado al sistema.
        """
        # Agregar procesos recién llegados
        for process in self.processes:
            # Si el proceso ha llegado y no está en ninguna cola ni ha terminado
            if (process.arrival_time <= self.current_time and 
                process not in self.process_queue and 
                process not in self.completed_processes and
                process != self.current_process):
                self.process_queue.append(process)
                self.ready_queue.append(process)
    
    def get_next_process(self):
        """
        Obtiene el siguiente proceso a ejecutar según el algoritmo Round Robin.
        
        Returns:
            Process: El siguiente proceso a ejecutar o None si no hay procesos disponibles
        """
        # En Round Robin, tomamos el siguiente proceso de la cola circular
        if self.process_queue:
            next_process = self.process_queue.popleft()
            if next_process.state != "TERMINATED":
                return next_process
        
        return None
    
    def execute_cycle(self):
        """
        Ejecuta un ciclo de la simulación para Round Robin.
        
        Returns:
            bool: True si la simulación debe continuar, False si ha terminado
        """
        # Actualizar colas con nuevos procesos que llegaron en este ciclo
        self.update_queues()
        
        # Si no hay proceso actual o el proceso actual ha terminado su quantum o su ejecución
        if self.current_process is None:
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
        
        # Ejecutar el proceso actual por el quantum de tiempo (o menos si termina antes)
        time_executed = self.current_process.execute(self.quantum)
        
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
            # Eliminar de la cola de listos
            if self.current_process in self.ready_queue:
                self.ready_queue.remove(self.current_process)
        else:
            # Si el proceso no ha terminado, lo enviamos al final de la cola
            self.process_queue.append(self.current_process)
        
        # Pasar al siguiente proceso
        self.current_process = None
        
        return len(self.completed_processes) < len(self.processes)
    
    def reset(self):
        """Reinicia la simulación."""
        super().reset()
        self.process_queue = deque()
