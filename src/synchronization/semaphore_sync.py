#Módulo que contiene la implementación del mecanismo de sincronización Semáforo

from src.synchronization.base_sync import BaseSynchronization

class SemaphoreSynchronization(BaseSynchronization):
    #Implementación del mecanismo de sincronización Semáforo.
    
    def __init__(self):
        #Inicializa un nuevo mecanismo de sincronización Semáforo.
        super().__init__("Semáforo")
    
    def process_action(self, action):
        #Procesa una acción según el mecanismo de sincronización Semáforo.
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
        
        # Verificar si el recurso está disponible para este tipo de acción (READ permite múltiples lectores)
        if resource.is_available_for(action.action_type) or process in resource.using_processes:
            # Adquirir el recurso para el proceso (si aún no lo tiene)
            if process not in resource.using_processes:
                resource.acquire(process, action.action_type)
            
            # Marcar la acción como ejecutada y completada
            action.set_running()
            action.set_completed()
            
            # Liberar el recurso después de usarlo (una acción dura un ciclo)
            released_processes = resource.release(process)
            
            # Verificar si algún proceso liberado estaba en la lista de pendientes
            for released_process in released_processes:
                # Buscar acciones pendientes de este proceso
                for pending_action in self.pending_actions[:]:
                    if pending_action.pid == released_process.pid and pending_action.state == "WAITING":
                        # Marcarla como completada y quitarla de pendientes
                        pending_action.set_completed()
                        if pending_action in self.pending_actions:
                            self.pending_actions.remove(pending_action)
                        if pending_action not in self.completed_actions:
                            self.completed_actions.append(pending_action)
            
            return True
        else:
            # El recurso no está disponible para este tipo de acción, el proceso debe esperar
            action.set_waiting()
            
            # Intentar adquirir el recurso (esto pondrá al proceso en la cola)
            resource.acquire(process, action.action_type)
            
            return False
    
    def execute_cycle(self):
        #Ejecuta un ciclo de la simulación para Semáforo.
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
        
        # Luego, procesar acciones que estaban esperando (por tipo de operación)
        processed_resources = {}
        
        waiting_actions = [action for action in self.pending_actions 
                          if action.state == "WAITING"]
        
        # Ordenar las acciones en espera por tiempo de ciclo (las más antiguas primero)
        waiting_actions.sort(key=lambda a: a.cycle)
        
        # Primero procesar lecturas (pueden ser múltiples por recurso)
        read_actions = [a for a in waiting_actions if a.action_type == "READ"]
        for action in read_actions:
            resource_name = action.resource_name
            resource = self.resources.get(resource_name)
            
            # Verificar si el recurso existe y si ya procesamos este recurso para WRITE
            if not resource or resource_name in processed_resources and processed_resources[resource_name] == "WRITE":
                continue
                
            # Verificar disponibilidad para lectura
            if resource.is_available_for("READ"):
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
                
                # Marcar este recurso como procesado para READ
                if resource_name not in processed_resources:
                    processed_resources[resource_name] = "READ"
        
        # Luego procesar escrituras (una por recurso)
        write_actions = [a for a in waiting_actions if a.action_type == "WRITE"]
        for action in write_actions:
            resource_name = action.resource_name
            
            # Saltar si ya procesamos este recurso
            if resource_name in processed_resources:
                continue
                
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
            
            # Marcar este recurso como procesado para WRITE
            processed_resources[resource_name] = "WRITE"
        
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
