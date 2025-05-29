#Módulo que contiene la implementación del algoritmo de calendarización SJF (Shortest Job First)

from src.schedulers.base_scheduler import BaseScheduler

class SJFScheduler(BaseScheduler):
    #Implementación del algoritmo de calendarización SJF (Shortest Job First).
    
    def __init__(self):
        #Inicializa un nuevo calendarizador SJF.
        super().__init__("SJF")
    
    def update_queues(self):
        #Actualiza las colas de procesos basado en el tiempo actual.
        for process in self.processes:
            # Si el proceso ha llegado y no está en ninguna cola ni ha terminado
            if (process.arrival_time <= self.current_time and 
                process not in self.ready_queue and 
                process not in self.completed_processes and
                self.current_process != process):
                self.ready_queue.append(process)
        
        # Ordenar la cola por tiempo de ejecución (burst time) y en caso de empate por arrival_time
        # y si aún hay empate, por el índice en la lista original (para mantener consistencia)
        self.ready_queue.sort(key=lambda p: (p.burst_time, p.arrival_time, self.processes.index(p)))
    
    def get_next_process(self):
        #Obtiene el siguiente proceso a ejecutar según el algoritmo SJF.
        # (SJF es no preemptivo)
        if self.current_process and self.current_process.remaining_time > 0:
            return self.current_process
        
        # De lo contrario, seleccionamos el proceso con menor tiempo de ejecución
        if self.ready_queue:
            next_process = self.ready_queue[0]
            # Eliminamos el proceso de la cola para evitar procesarlo múltiples veces
            self.ready_queue.remove(next_process)
            return next_process
        
        return None
        
    def execute_cycle(self):
        #Ejecuta un ciclo de la simulación para SJF con mejor manejo de errores.
        try:
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
                    # El proceso ya ha sido removido de ready_queue en get_next_process
            
            return len(self.completed_processes) < len(self.processes)
            
        except Exception as e:
            import traceback
            print(f"Error en SJF execute_cycle: {e}\n{traceback.format_exc()}")
            # En caso de error, terminar la simulación
            return False
