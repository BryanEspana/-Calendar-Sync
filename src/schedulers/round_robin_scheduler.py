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
        self.quantum_remaining = quantum  # Inicializar quantum restante
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
        # Agregar procesos recién llegados en orden de llegada
        nuevos_procesos = []
        
        for process in self.processes:
            # Si el proceso ha llegado y no está en ninguna cola ni ha terminado
            if (process.arrival_time <= self.current_time and 
                process not in self.process_queue and 
                process not in self.completed_processes and
                process != self.current_process):
                nuevos_procesos.append(process)
        
        # Ordenar los nuevos procesos por tiempo de llegada y luego por ID
        nuevos_procesos.sort(key=lambda p: (p.arrival_time, p.pid))
        
        # Añadir los procesos ordenados a la cola
        for process in nuevos_procesos:
            self.process_queue.append(process)
            if process not in self.ready_queue:
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
        try:
            # Actualizar colas con nuevos procesos que llegaron en este ciclo
            self.update_queues()
            
            # Si no hay proceso actual, obtener el siguiente proceso de la cola
            if self.current_process is None:
                self.current_process = self.get_next_process()
                # Reiniciar el quantum cuando se asigna un nuevo proceso
                self.quantum_remaining = self.quantum
            
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
            
            # Ejecutar SOLO UN CICLO por vez (no todo el quantum de una vez)
            time_executed = self.current_process.execute(1)  # Ejecutar solo 1 ciclo
            
            # Registrar ejecución para el diagrama de Gantt (ciclo por ciclo)
            self.execution_history.append({
                'process': self.current_process,
                'start_time': self.current_time,
                'end_time': self.current_time + time_executed
            })
            
            # Si el proceso comienza su ejecución por primera vez
            if self.current_process.start_time is None:
                self.current_process.set_start_time(self.current_time)
            
            # Avanzar el tiempo (siempre 1 ciclo)
            self.current_time += time_executed
            
            # Decrementar quantum restante
            self.quantum_remaining -= 1
            
            # Guardar una referencia al proceso actual antes de cambiar
            current = self.current_process
            
            # Verificar si el proceso ha terminado o si se agotó el quantum
            process_finished = current.state == "TERMINATED"
            quantum_expired = self.quantum_remaining <= 0
            
            if process_finished:
                # Proceso terminado
                current.set_finish_time(self.current_time)
                if current not in self.completed_processes:
                    self.completed_processes.append(current)
                # Eliminar de la cola de listos
                if current in self.ready_queue:
                    self.ready_queue.remove(current)
                # Pasar al siguiente proceso
                self.current_process = None
                
            elif quantum_expired:
                # Quantum agotado, cambiar de proceso
                # Solo mover a la cola si hay otros procesos esperando
                if len(self.ready_queue) > 1 or any(p.arrival_time <= self.current_time for p in self.processes if p not in self.completed_processes and p != current):
                    # Remover de ready_queue temporalmente
                    if current in self.ready_queue:
                        self.ready_queue.remove(current)
                    # Agregarlo al final de la cola
                    self.process_queue.append(current)
                    self.ready_queue.append(current)
                    # Pasar al siguiente proceso
                    self.current_process = None
                # Si es el único proceso, continúa ejecutándose
                else:
                    self.quantum_remaining = self.quantum  # Reiniciar quantum
            
            # Si no se terminó el proceso ni expiró el quantum, continúa ejecutándose
            # (self.current_process mantiene su valor)
            
            return len(self.completed_processes) < len(self.processes)
            
        except Exception as e:
            import traceback
            print(f"Error en Round Robin execute_cycle: {e}\n{traceback.format_exc()}")
            return False
    
    def reset(self):
        """Reinicia la simulación."""
        super().reset()
        self.process_queue = deque()
        self.quantum_remaining = self.quantum
