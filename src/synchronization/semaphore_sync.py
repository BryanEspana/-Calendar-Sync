"""
Módulo que contiene la implementación del mecanismo de sincronización Semáforo
"""

from src.synchronization.base_sync import BaseSynchronization

class SemaphoreSynchronization(BaseSynchronization):
    """
    Implementación del mecanismo de sincronización Semáforo.
    En este mecanismo, múltiples procesos pueden acceder a un recurso hasta su límite de contador.
    """
    
    def __init__(self):
        """Inicializa un nuevo mecanismo de sincronización Semáforo."""
        super().__init__("Semáforo")
    
    def process_action(self, action):
        """
        Procesa una acción según el mecanismo de sincronización Semáforo.
        
        Args:
            action: Acción a procesar
            
        Returns:
            bool: True si la acción se ejecutó con éxito, False si está esperando
        """
        # Obtener el recurso asociado a la acción
        resource = self.resources.get(action.resource_name)
        if not resource:
            # Si el recurso no existe, marcar la acción como completada y devolver éxito
            action.set_completed()
            return True
        
        # Obtener el proceso asociado a la acción
        process = self.processes.get(action.pid)
        if not process:
            # Si el proceso no existe, marcar la acción como completada y devolver éxito
            action.set_completed()
            return True
        
        # Verificar si el recurso está disponible o el proceso ya lo está usando
        if resource.is_available() or process in resource.using_processes:
            # Adquirir el recurso para el proceso (si aún no lo tiene)
            if process not in resource.using_processes:
                resource.acquire(process)
            
            # Marcar la acción como ejecutada y completada
            action.set_running()
            action.set_completed()
            
            # Liberar el recurso después de usarlo (una acción dura un ciclo)
            resource.release(process)
            
            return True
        else:
            # El recurso no está disponible, el proceso debe esperar
            action.set_waiting()
            
            # Intentar adquirir el recurso (esto pondrá al proceso en la cola)
            resource.acquire(process)
            
            return False
    
    def execute_cycle(self):
        """
        Ejecuta un ciclo de la simulación para Semáforo.
        
        Returns:
            dict: Estado del ciclo actual
        """
        cycle_result = super().execute_cycle()
        
        # Intentar ejecutar acciones que estaban esperando
        waiting_actions = [action for action in self.pending_actions 
                          if action.state == "WAITING"]
        
        if waiting_actions:
            for action in waiting_actions:
                success = self.process_action(action)
                if success:
                    # Si la acción se completó, moverla a la lista de completadas
                    if action in self.pending_actions:
                        self.pending_actions.remove(action)
                    if action not in self.completed_actions:
                        self.completed_actions.append(action)
        
        return cycle_result
