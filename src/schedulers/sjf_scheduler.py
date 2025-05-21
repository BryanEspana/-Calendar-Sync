"""
Módulo que contiene la implementación del algoritmo de calendarización SJF (Shortest Job First)
"""

from src.schedulers.base_scheduler import BaseScheduler

class SJFScheduler(BaseScheduler):
    """
    Implementación del algoritmo de calendarización SJF (Shortest Job First).
    Los procesos se ejecutan en orden de menor a mayor tiempo de ejecución.
    Este es un algoritmo no preemptivo.
    """
    
    def __init__(self):
        """Inicializa un nuevo calendarizador SJF."""
        super().__init__("SJF")
    
    def update_queues(self):
        """
        Actualiza las colas de procesos basado en el tiempo actual.
        Agrega a la ready_queue los procesos que han llegado al sistema.
        """
        for process in self.processes:
            # Si el proceso ha llegado y no está en ninguna cola ni ha terminado
            if (process.arrival_time <= self.current_time and 
                process not in self.ready_queue and 
                process not in self.completed_processes):
                self.ready_queue.append(process)
        
        # Ordenar la cola por tiempo de ejecución (burst time)
        self.ready_queue.sort(key=lambda p: p.burst_time)
    
    def get_next_process(self):
        """
        Obtiene el siguiente proceso a ejecutar según el algoritmo SJF.
        
        Returns:
            Process: El siguiente proceso a ejecutar o None si no hay procesos disponibles
        """
        # Si hay un proceso en ejecución que aún no termina, continuamos con él
        # (SJF es no preemptivo)
        if self.current_process and self.current_process.remaining_time > 0:
            return self.current_process
        
        # De lo contrario, seleccionamos el proceso con menor tiempo de ejecución
        if self.ready_queue:
            return self.ready_queue[0]
        
        return None
