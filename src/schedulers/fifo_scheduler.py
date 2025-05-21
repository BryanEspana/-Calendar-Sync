"""
Módulo que contiene la implementación del algoritmo de calendarización FIFO (First In First Out)
"""

from src.schedulers.base_scheduler import BaseScheduler

class FIFOScheduler(BaseScheduler):
    """
    Implementación del algoritmo de calendarización FIFO (First In First Out).
    Los procesos se ejecutan en el orden en que llegan al sistema.
    """
    
    def __init__(self):
        """Inicializa un nuevo calendarizador FIFO."""
        super().__init__("FIFO")
    
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
        
        # Ordenar la cola por tiempo de llegada
        self.ready_queue.sort(key=lambda p: p.arrival_time)
    
    def get_next_process(self):
        """
        Obtiene el siguiente proceso a ejecutar según el algoritmo FIFO.
        
        Returns:
            Process: El siguiente proceso a ejecutar o None si no hay procesos disponibles
        """
        # En FIFO, simplemente tomamos el primer proceso de la cola
        if self.ready_queue:
            return self.ready_queue[0]
        
        return None
