#Módulo que contiene la clase base para los mecanismos de sincronización

class BaseSynchronization:
    #Clase base que define la interfaz común para los mecanismos de sincronización.
    
    def __init__(self, name):
        #Inicializa un nuevo mecanismo de sincronización.
        self.name = name
        self.processes = {}  # Procesos por PID
        self.resources = {}  # Recursos por nombre
        self.actions = []    # Todas las acciones
        self.current_time = 0
        self.execution_history = []
        self.completed_actions = []
        self.pending_actions = []
        
    def load_processes(self, processes):
        #Carga una lista de procesos.
        self.processes = {process.pid: process for process in processes}
    
    def load_resources(self, resources):
        #Carga una lista de recursos.
        self.resources = {resource.name: resource for resource in resources}
    
    def load_actions(self, actions):
        #Carga una lista de acciones.
        self.actions = sorted(actions, key=lambda a: a.cycle)
        self.pending_actions = self.actions.copy()
    
    def get_due_actions(self):
        #Obtiene las acciones que deben ejecutarse en el ciclo actual.
        due_actions = []
        for action in self.pending_actions[:]:
            if action.is_due(self.current_time):
                due_actions.append(action)
        
        return due_actions
    
    def process_action(self, action):
        #Procesa una acción según el mecanismo de sincronización.
        raise NotImplementedError("Las clases hijas deben implementar este método")
    
    def execute_cycle(self):
        #Ejecuta un ciclo de la simulación.
        # Obtener acciones a ejecutar en este ciclo
        due_actions = self.get_due_actions()
        
        # Acciones ejecutadas en este ciclo
        cycle_actions = []
        
        # Procesar cada acción
        for action in due_actions:
            success = self.process_action(action)
            
            # Registrar el resultado
            cycle_actions.append({
                'action': action,
                'success': success,
                'time': self.current_time
            })
            
            # Si la acción se completó, moverla a la lista de completadas
            if action.state == "COMPLETED":
                if action in self.pending_actions:
                    self.pending_actions.remove(action)
                if action not in self.completed_actions:
                    self.completed_actions.append(action)
        
        # Guardar el historial de este ciclo
        self.execution_history.append({
            'cycle': self.current_time,
            'actions': cycle_actions
        })
        
        # Avanzar el tiempo
        self.current_time += 1
        
        return {
            'cycle': self.current_time - 1,
            'actions': cycle_actions,
            'remaining': len(self.pending_actions)
        }
    
    def run_simulation(self, max_cycles=100):
        #Ejecuta la simulación completa.
        self.reset()
        
        # Ejecutar la simulación hasta que termine o se alcance el máximo de ciclos
        cycles = 0
        while self.pending_actions and cycles < max_cycles:
            self.execute_cycle()
            cycles += 1
        
        return self.get_results()
    
    def get_results(self):
        #Obtiene los resultados de la simulación.
        return {
            'mechanism': self.name,
            'total_time': self.current_time,
            'execution_history': self.execution_history,
            'completed_actions': len(self.completed_actions),
            'total_actions': len(self.actions)
        }
    
    def reset(self):
        #Reinicia la simulación.
        self.current_time = 0
        self.execution_history = []
        self.completed_actions = []
        self.pending_actions = self.actions.copy()
        
        # Reiniciar todos los recursos
        for resource in self.resources.values():
            resource.reset()
        
        # Reiniciar el estado de todas las acciones
        for action in self.actions:
            action.state = "PENDING"
