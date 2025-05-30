#Módulo que contiene la implementación del mecanismo de sincronización Mutex

from src.synchronization.base_sync import BaseSynchronization

class MutexSynchronization(BaseSynchronization):
    #Implementación del mecanismo de sincronización Mutex.
    
    def __init__(self):
        #Inicializa un nuevo mecanismo de sincronización Mutex.
        super().__init__("Mutex")
    
    def process_action(self, action):
        #Procesa una acción según el mecanismo de sincronización Mutex.
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
        
        # Verificar si el recurso está disponible para este tipo de acción
        if resource.is_available_for(action.action_type) or process in resource.using_processes:
            # Adquirir el recurso para el proceso (si aún no lo tiene)
            if process not in resource.using_processes:
                resource.acquire(process, action.action_type)
            
            # Marcar la acción como ejecutada y completada
            action.set_running()
            action.set_completed()
            
            # Liberar el recurso después de usarlo (una acción dura un ciclo)
            released_processes = resource.release(process)
            
            # Los procesos liberados ya han sido actualizados por el recurso
            # No necesitamos hacer nada más con ellos en el contexto de Mutex
            
            return True
        else:
            # El recurso no está disponible, el proceso debe esperar
            action.set_waiting()
            
            # Intentar adquirir el recurso (esto pondrá al proceso en la cola)
            resource.acquire(process, action.action_type)
            
            return False
    
    def execute_cycle(self):
        #Ejecuta un ciclo de la simulación para Mutex.
        # Registrar el estado antes de ejecutar el ciclo para visualización
        cycle_actions = []
        
        # Obtener acciones que deben ejecutarse en este ciclo
        due_actions = self.get_due_actions()
        
        # Primero, procesar todas las acciones con tiempo de inicio igual al ciclo actual
        for action in due_actions:
            success = self.process_action(action)
            
            # Registrar el estado de la acción para visualización
            cycle_actions.append({
                'action': action,
                'success': success
            })
            
            # Si la acción se completó, moverla a la lista de completadas
            if success and action.state == "COMPLETED":
                if action in self.pending_actions:
                    self.pending_actions.remove(action)
                if action not in self.completed_actions:
                    self.completed_actions.append(action)
        
        # Luego, procesar acciones que estaban esperando (una por recurso)
        processed_resources = set()  # Para rastrear qué recursos ya han sido procesados
        
        waiting_actions = [action for action in self.pending_actions 
                          if action.state == "WAITING"]
        
        # Ordenar las acciones en espera por tiempo de ciclo (las más antiguas primero)
        waiting_actions.sort(key=lambda a: a.cycle)
        
        for action in waiting_actions:
            # Solo procesar una acción por recurso en cada ciclo
            if action.resource_name not in processed_resources:
                success = self.process_action(action)
                
                # Registrar el estado de la acción para visualización
                cycle_actions.append({
                    'action': action,
                    'success': success
                })
                
                # Si la acción se completó, moverla a la lista de completadas
                if success and action.state == "COMPLETED":
                    if action in self.pending_actions:
                        self.pending_actions.remove(action)
                    if action not in self.completed_actions:
                        self.completed_actions.append(action)
                
                # Marcar este recurso como procesado para este ciclo
                processed_resources.add(action.resource_name)
        
        # Guardar el historial de este ciclo (importante para visualización)
        self.execution_history.append({
            'cycle': self.current_time,
            'actions': cycle_actions
        })
        
        # Avanzar el tiempo
        self.current_time += 1
        
        cycle_result = {
            'cycle': self.current_time - 1,
            'actions': cycle_actions,
            'remaining': len(self.pending_actions)
        }
        
        return cycle_result
