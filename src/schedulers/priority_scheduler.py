"""
Módulo que contiene la implementación del algoritmo de calendarización Priority
"""

from src.schedulers.base_scheduler import BaseScheduler

class PriorityScheduler(BaseScheduler):
    """
    Implementación del algoritmo de calendarización Priority.
    Los procesos se ejecutan según su prioridad (menor valor numérico = mayor prioridad).
    Esta implementación es no preemptiva.
    """
    
    def __init__(self):
        """Inicializa un nuevo calendarizador Priority."""
        super().__init__("Priority")
    
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
        
        # Ordenar la cola por prioridad (menor valor = mayor prioridad)
        self.ready_queue.sort(key=lambda p: p.priority)
    
    def get_next_process(self):
        """
        Obtiene el siguiente proceso a ejecutar según el algoritmo Priority.
        
        Returns:
            Process: El siguiente proceso a ejecutar o None si no hay procesos disponibles
        """
        # Si hay un proceso en ejecución que aún no termina, continuamos con él
        # (esta implementación de Priority es no preemptiva)
        if self.current_process and self.current_process.remaining_time > 0:
            return self.current_process
        
        # De lo contrario, seleccionamos el proceso con mayor prioridad
        if self.ready_queue:
            return self.ready_queue[0]
        
        return None
