"""
Módulo que contiene la clase Process para representar procesos en el simulador
"""

class Process:
    """
    Clase que representa un proceso en el simulador.
    
    Attributes:
        pid (str): Identificador único del proceso
        burst_time (int): Tiempo total de ejecución necesario
        arrival_time (int): Tiempo de llegada al sistema
        priority (int): Prioridad del proceso (menor número = mayor prioridad)
        remaining_time (int): Tiempo restante de ejecución
        waiting_time (int): Tiempo que el proceso ha estado esperando
        turnaround_time (int): Tiempo total desde llegada hasta finalización
        start_time (int): Tiempo en que el proceso comenzó a ejecutarse
        finish_time (int): Tiempo en que el proceso terminó su ejecución
        state (str): Estado actual del proceso (READY, RUNNING, WAITING, TERMINATED)
        color (str): Color para representar el proceso en la visualización
    """
    
    # Estados posibles de un proceso
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"
    
    def __init__(self, pid, burst_time, arrival_time, priority=0):
        """
        Inicializa un nuevo proceso.
        
        Args:
            pid (str): Identificador único del proceso
            burst_time (int): Tiempo total de ejecución necesario
            arrival_time (int): Tiempo de llegada al sistema
            priority (int, optional): Prioridad del proceso. Defaults to 0.
        """
        self.pid = pid
        self.burst_time = burst_time
        self.arrival_time = arrival_time
        self.priority = priority
        
        # Atributos calculados durante la simulación
        self.remaining_time = burst_time
        self.waiting_time = 0
        self.turnaround_time = 0
        self.start_time = None
        self.finish_time = None
        self.state = Process.READY
        self.color = None  # Se asignará dinámicamente
    
    def execute(self, time_quantum=1):
        """
        Ejecuta el proceso por un quantum de tiempo.
        
        Args:
            time_quantum (int, optional): Unidades de tiempo a ejecutar. Defaults to 1.
        
        Returns:
            int: Tiempo de ejecución real (puede ser menor que time_quantum si el proceso termina)
        """
        if self.state != Process.RUNNING:
            self.state = Process.RUNNING
        
        executed_time = min(time_quantum, self.remaining_time)
        self.remaining_time -= executed_time
        
        # Si el proceso terminó su ejecución
        if self.remaining_time <= 0:
            self.state = Process.TERMINATED
        
        return executed_time
    
    def wait(self, time=1):
        """
        Incrementa el tiempo de espera del proceso.
        
        Args:
            time (int, optional): Unidades de tiempo a esperar. Defaults to 1.
        """
        if self.state == Process.READY or self.state == Process.WAITING:
            self.waiting_time += time
    
    def set_start_time(self, time):
        """
        Establece el tiempo de inicio de ejecución.
        
        Args:
            time (int): Tiempo de inicio
        """
        if self.start_time is None:
            self.start_time = time
    
    def set_finish_time(self, time):
        """
        Establece el tiempo de finalización y calcula el turnaround time.
        
        Args:
            time (int): Tiempo de finalización
        """
        self.finish_time = time
        self.turnaround_time = self.finish_time - self.arrival_time
    
    def reset(self):
        """Reinicia el proceso a su estado inicial pero mantiene sus atributos básicos."""
        self.remaining_time = self.burst_time
        self.waiting_time = 0
        self.turnaround_time = 0
        self.start_time = None
        self.finish_time = None
        self.state = Process.READY
    
    def __str__(self):
        """Representación en cadena del proceso."""
        return f"Process {self.pid} (BT={self.burst_time}, AT={self.arrival_time}, Prio={self.priority})"
    
    def __repr__(self):
        """Representación de desarrollo del proceso."""
        return self.__str__()
    
    @classmethod
    def from_line(cls, line):
        """
        Crea un proceso a partir de una línea de texto con formato: 
        <PID>, <BT>, <AT>, <Priority>
        
        Args:
            line (str): Línea de texto del archivo
            
        Returns:
            Process: Una nueva instancia de Process
        """
        parts = [part.strip() for part in line.split(',')]
        
        pid = parts[0]
        burst_time = int(parts[1])
        arrival_time = int(parts[2])
        priority = int(parts[3]) if len(parts) > 3 else 0
        
        return cls(pid, burst_time, arrival_time, priority)
