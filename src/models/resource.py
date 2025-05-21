"""
Módulo que contiene la clase Resource para representar recursos en el simulador de sincronización
"""

class Resource:
    """
    Clase que representa un recurso en el simulador de sincronización.
    
    Attributes:
        name (str): Nombre del recurso
        counter (int): Contador del recurso (1 para mutex, n para semáforo)
        current_counter (int): Valor actual del contador
        process_queue (list): Cola de procesos esperando el recurso
        using_processes (list): Lista de procesos usando actualmente el recurso
    """
    
    def __init__(self, name, counter=1):
        """
        Inicializa un nuevo recurso.
        
        Args:
            name (str): Nombre del recurso
            counter (int, optional): Contador del recurso. Defaults to 1 (mutex).
        """
        self.name = name
        self.counter = counter
        self.current_counter = counter
        self.process_queue = []  # Procesos esperando
        self.using_processes = []  # Procesos usando el recurso
    
    def is_available(self):
        """
        Verifica si el recurso está disponible.
        
        Returns:
            bool: True si el recurso está disponible, False en caso contrario
        """
        return self.current_counter > 0
    
    def acquire(self, process):
        """
        Intenta adquirir el recurso para un proceso.
        
        Args:
            process: Proceso que intenta adquirir el recurso
            
        Returns:
            bool: True si el recurso fue adquirido, False en caso contrario
        """
        if self.is_available():
            self.current_counter -= 1
            self.using_processes.append(process)
            return True
        else:
            # Si el recurso no está disponible, el proceso se agrega a la cola
            if process not in self.process_queue:
                self.process_queue.append(process)
            return False
    
    def release(self, process):
        """
        Libera el recurso usado por un proceso.
        
        Args:
            process: Proceso que libera el recurso
            
        Returns:
            process: Siguiente proceso que obtiene el recurso o None si no hay procesos en espera
        """
        if process in self.using_processes:
            self.using_processes.remove(process)
            self.current_counter += 1
            
            # Si hay procesos esperando, asignar el recurso al siguiente
            if self.process_queue and self.current_counter > 0:
                next_process = self.process_queue.pop(0)
                self.current_counter -= 1
                self.using_processes.append(next_process)
                return next_process
        
        return None
    
    def reset(self):
        """Reinicia el recurso a su estado inicial."""
        self.current_counter = self.counter
        self.process_queue = []
        self.using_processes = []
    
    def __str__(self):
        """Representación en cadena del recurso."""
        return f"Resource {self.name} (Counter={self.counter}, Available={self.current_counter})"
    
    def __repr__(self):
        """Representación de desarrollo del recurso."""
        return self.__str__()
    
    @classmethod
    def from_line(cls, line):
        """
        Crea un recurso a partir de una línea de texto con formato: 
        <NOMBRE RECURSO>, <CONTADOR>
        
        Args:
            line (str): Línea de texto del archivo
            
        Returns:
            Resource: Una nueva instancia de Resource
        """
        parts = [part.strip() for part in line.split(',')]
        
        name = parts[0]
        counter = int(parts[1]) if len(parts) > 1 else 1
        
        return cls(name, counter)
