"""
Módulo que contiene la clase base para los algoritmos de calendarización
"""

class BaseScheduler:
    #Clase base que define la interfaz común para todos los algoritmos de calendarización.
    def __init__(self, name):
        """
        Inicializa un nuevo calendarizador.
        
        Args:
            name (str): Nombre del algoritmo
        """
        self.name = name
        self.processes = []
        self.current_time = 0
        self.execution_history = []
        self.completed_processes = []
        self.ready_queue = []
        self.current_process = None
    
    def add_process(self, process):
        #Añade un proceso a la lista de procesos.
        self.processes.append(process)
    
    def load_processes(self, processes):
        #Carga una lista de procesos.
        self.processes = processes.copy()
        self.reset()
        self.processes = processes.copy()
        self.reset()
    
    def update_queues(self):
        #Actualiza las colas de procesos basado en el tiempo actual.
        raise NotImplementedError("Las clases hijas deben implementar este método")
    
    def get_next_process(self):
        #Obtiene el siguiente proceso a ejecutar según el algoritmo.
        raise NotImplementedError("Las clases hijas deben implementar este método")
    
    def execute_cycle(self):
        #Ejecuta un ciclo de la simulación.
        # Actualizar colas con nuevos procesos que llegaron en este ciclo
        self.update_queues()
        
        # Si no hay proceso actual o se ha completado, obtener el siguiente
        if self.current_process is None or self.current_process.state == "TERMINATED":
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
        
        # Ejecutar el proceso actual
        time_executed = self.current_process.execute()
        
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
    
    def run_simulation(self):
        #Ejecuta la simulación completa.
        self.reset()
        
        # Ejecutar la simulación hasta que termine
        while self.execute_cycle():
            pass
        
        return self.get_results()
        self.reset()
        
        # Ejecutar la simulación hasta que termine
        while self.execute_cycle():
            pass
        
        return self.get_results()
    
    def get_results(self):
        #Obtiene los resultados de la simulación.
        total_waiting_time = sum(p.waiting_time for p in self.processes)
        avg_waiting_time = total_waiting_time / len(self.processes) if self.processes else 0
        
        total_turnaround_time = sum(p.turnaround_time for p in self.processes)
        avg_turnaround_time = total_turnaround_time / len(self.processes) if self.processes else 0
        
        return {
            'algorithm': self.name,
            'total_time': self.current_time,
            'processes': self.processes,
            'execution_history': self.execution_history,
            'avg_waiting_time': avg_waiting_time,
            'avg_turnaround_time': avg_turnaround_time,
        }
        total_waiting_time = sum(p.waiting_time for p in self.processes)
        avg_waiting_time = total_waiting_time / len(self.processes) if self.processes else 0
        
        total_turnaround_time = sum(p.turnaround_time for p in self.processes)
        avg_turnaround_time = total_turnaround_time / len(self.processes) if self.processes else 0
        
        return {
            'algorithm': self.name,
            'total_time': self.current_time,
            'processes': self.processes,
            'execution_history': self.execution_history,
            'avg_waiting_time': avg_waiting_time,
            'avg_turnaround_time': avg_turnaround_time,
        }
    
    def reset(self):
        #Reinicia la simulación.
        self.current_time = 0
        self.execution_history = []
        self.completed_processes = []
        self.ready_queue = []
        self.current_process = None
        
        # Reiniciar todos los procesos
        for process in self.processes:
            process.reset()
