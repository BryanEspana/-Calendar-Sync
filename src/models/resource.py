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
        using_processes (dict): Diccionario de procesos usando el recurso {proceso: acción}
        sync_mode (str): Modo de sincronización ('mutex' o 'semaphore')
    """
    
    def __init__(self, name, counter=1, sync_mode='mutex'):
        """
        Inicializa un nuevo recurso.
        
        Args:
            name (str): Nombre del recurso
            counter (int, optional): Contador del recurso. Defaults to 1 (mutex).
            sync_mode (str): Modo de sincronización ('mutex' o 'semaphore')
        """
        self.name = name
        self.counter = counter
        self.current_counter = counter
        self.process_queue = []  # Procesos esperando
        self.using_processes = {}  # {proceso: acción} para saber qué está haciendo cada proceso
        self.sync_mode = sync_mode
    
    def is_available_for(self, action):
        """
        Verifica si el recurso está disponible para una acción específica.
        
        Args:
            action (str): 'READ' o 'WRITE'
            
        Returns:
            bool: True si el recurso está disponible para esa acción
        """
        if self.sync_mode == 'mutex':
            # Para mutex, solo importa si hay espacio disponible
            return self.current_counter > 0
        
        elif self.sync_mode == 'semaphore':
            if action == 'READ':
                # Para READ: permitir si no hay WRITE activo
                active_actions = list(self.using_processes.values())
                return 'WRITE' not in active_actions
            
            elif action == 'WRITE':
                # Para WRITE: permitir solo si no hay ninguna operación activa
                return len(self.using_processes) == 0
        
        return False
    
    def acquire(self, process, action):
        """
        Intenta adquirir el recurso para un proceso con una acción específica.
        
        Args:
            process: Proceso que intenta adquirir el recurso
            action (str): 'READ' o 'WRITE'
            
        Returns:
            bool: True si el recurso fue adquirido, False en caso contrario
        """
        if self.is_available_for(action):
            if self.sync_mode == 'mutex':
                self.current_counter -= 1
            
            self.using_processes[process] = action
            return True
        else:
            # Si el recurso no está disponible, el proceso se agrega a la cola
            if (process, action) not in self.process_queue:
                self.process_queue.append((process, action))
            return False
    
    def release(self, process):
        """
        Libera el recurso usado por un proceso.
        
        Args:
            process: Proceso que libera el recurso
            
        Returns:
            list: Lista de procesos que obtuvieron el recurso tras la liberación
        """
        released_processes = []
        
        if process in self.using_processes:
            action = self.using_processes[process]
            del self.using_processes[process]
            
            if self.sync_mode == 'mutex':
                self.current_counter += 1
            
            # Intentar asignar el recurso a procesos en espera
            processes_to_remove = []
            for waiting_process, waiting_action in self.process_queue:
                if self.is_available_for(waiting_action):
                    if self.sync_mode == 'mutex':
                        self.current_counter -= 1
                    
                    self.using_processes[waiting_process] = waiting_action
                    released_processes.append(waiting_process)
                    processes_to_remove.append((waiting_process, waiting_action))
                    
                    # Para mutex, solo uno a la vez
                    if self.sync_mode == 'mutex':
                        break
                    
                    # Para semáforos, continuar solo si es READ y el siguiente también es READ
                    if waiting_action == 'WRITE':
                        break
            
            # Remover procesos asignados de la cola
            for item in processes_to_remove:
                self.process_queue.remove(item)
        
        return released_processes
    
    def get_status(self, process):
        """
        Obtiene el estado de un proceso respecto a este recurso.
        
        Args:
            process: Proceso a verificar
            
        Returns:
            str: 'ACCESED', 'WAITING', o 'NONE'
        """
        if process in self.using_processes:
            return 'ACCESED'
        
        for waiting_process, _ in self.process_queue:
            if waiting_process == process:
                return 'WAITING'
        
        return 'NONE'
    
    def get_readers_count(self):
        """Retorna el número de procesos haciendo READ."""
        return sum(1 for action in self.using_processes.values() if action == 'READ')
    
    def get_writers_count(self):
        """Retorna el número de procesos haciendo WRITE."""
        return sum(1 for action in self.using_processes.values() if action == 'WRITE')
    
    def has_writer(self):
        """Verifica si hay un proceso escribiendo."""
        return 'WRITE' in self.using_processes.values()
    
    def reset(self):
        """Reinicia el recurso a su estado inicial."""
        self.current_counter = self.counter
        self.process_queue = []
        self.using_processes = {}
    
    def __str__(self):
        """Representación en cadena del recurso."""
        using_info = f"Using: {len(self.using_processes)}, Waiting: {len(self.process_queue)}"
        return f"Resource {self.name} ({self.sync_mode}) - {using_info}"
    
    def __repr__(self):
        """Representación de desarrollo del recurso."""
        return self.__str__()
    
    @classmethod
    def from_line(cls, line, sync_mode='mutex'):
        """
        Crea un recurso a partir de una línea de texto con formato: 
        <NOMBRE RECURSO>, <CONTADOR>
        
        Args:
            line (str): Línea de texto del archivo
            sync_mode (str): Modo de sincronización
            
        Returns:
            Resource: Una nueva instancia de Resource
        """
        parts = [part.strip() for part in line.split(',')]
        
        name = parts[0]
        counter = int(parts[1]) if len(parts) > 1 else 1
        
        return cls(name, counter, sync_mode)