"""
Módulo que contiene la clase Action para representar acciones sobre recursos en el simulador
"""

class Action:
    """
    Clase que representa una acción sobre un recurso en el simulador.
    
    Attributes:
        pid (str): Identificador del proceso que realiza la acción
        action_type (str): Tipo de acción (READ, WRITE)
        resource_name (str): Nombre del recurso sobre el que se realiza la acción
        cycle (int): Ciclo en el que se debe realizar la acción
        state (str): Estado actual de la acción (PENDING, RUNNING, WAITING, COMPLETED)
    """
    
    # Tipos de acciones
    READ = "READ"
    WRITE = "WRITE"
    
    # Estados posibles de una acción
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    
    def __init__(self, pid, action_type, resource_name, cycle):
        """
        Inicializa una nueva acción.
        
        Args:
            pid (str): Identificador del proceso que realiza la acción
            action_type (str): Tipo de acción (READ, WRITE)
            resource_name (str): Nombre del recurso sobre el que se realiza la acción
            cycle (int): Ciclo en el que se debe realizar la acción
        """
        self.pid = pid
        self.action_type = action_type
        self.resource_name = resource_name
        self.cycle = cycle
        self.state = Action.PENDING
    
    def is_due(self, current_cycle):
        """
        Verifica si la acción debe realizarse en el ciclo actual.
        
        Args:
            current_cycle (int): Ciclo actual de la simulación
            
        Returns:
            bool: True si la acción debe realizarse, False en caso contrario
        """
        return current_cycle >= self.cycle and self.state == Action.PENDING
    
    def set_waiting(self):
        """Establece el estado de la acción como WAITING."""
        self.state = Action.WAITING
    
    def set_running(self):
        """Establece el estado de la acción como RUNNING."""
        self.state = Action.RUNNING
    
    def set_completed(self):
        """Establece el estado de la acción como COMPLETED."""
        self.state = Action.COMPLETED
    
    def __str__(self):
        """Representación en cadena de la acción."""
        return f"Action {self.pid} {self.action_type} {self.resource_name} at cycle {self.cycle} (State: {self.state})"
    
    def __repr__(self):
        """Representación de desarrollo de la acción."""
        return self.__str__()
    
    @classmethod
    def from_line(cls, line):
        """
        Crea una acción a partir de una línea de texto con formato: 
        <PID>, <ACCION>, <RECURSO>, <CICLO>
        
        Args:
            line (str): Línea de texto del archivo
            
        Returns:
            Action: Una nueva instancia de Action
        """
        parts = [part.strip() for part in line.split(',')]
        
        pid = parts[0]
        action_type = parts[1]
        resource_name = parts[2]
        cycle = int(parts[3])
        
        return cls(pid, action_type, resource_name, cycle)
