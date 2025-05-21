"""
Módulo con funciones para cargar archivos de procesos, recursos y acciones
"""

import os
from src.models.process import Process
from src.models.resource import Resource
from src.models.action import Action

def load_processes_file(file_path):
    """
    Carga procesos desde un archivo de texto.
    
    Args:
        file_path (str): Ruta al archivo de procesos
        
    Returns:
        list: Lista de objetos Process
    """
    processes = []
    
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        process = Process.from_line(line)
                        processes.append(process)
                    except Exception as e:
                        print(f"Error al procesar línea: {line}. Error: {e}")
    except FileNotFoundError:
        print(f"No se encontró el archivo: {file_path}")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
    
    return processes

def load_resources_file(file_path):
    """
    Carga recursos desde un archivo de texto.
    
    Args:
        file_path (str): Ruta al archivo de recursos
        
    Returns:
        list: Lista de objetos Resource
    """
    resources = []
    
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        resource = Resource.from_line(line)
                        resources.append(resource)
                    except Exception as e:
                        print(f"Error al procesar línea: {line}. Error: {e}")
    except FileNotFoundError:
        print(f"No se encontró el archivo: {file_path}")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
    
    return resources

def load_actions_file(file_path):
    """
    Carga acciones desde un archivo de texto.
    
    Args:
        file_path (str): Ruta al archivo de acciones
        
    Returns:
        list: Lista de objetos Action
    """
    actions = []
    
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        action = Action.from_line(line)
                        actions.append(action)
                    except Exception as e:
                        print(f"Error al procesar línea: {line}. Error: {e}")
    except FileNotFoundError:
        print(f"No se encontró el archivo: {file_path}")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
    
    return actions

def create_sample_files(directory):
    """
    Crea archivos de ejemplo para procesos, recursos y acciones.
    
    Args:
        directory (str): Directorio donde se crearán los archivos
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Archivo de procesos de ejemplo
    process_file = os.path.join(directory, "procesos_ejemplo.txt")
    with open(process_file, 'w') as file:
        file.write("# Formato: <PID>, <BT>, <AT>, <Priority>\n")
        file.write("P1, 8, 0, 1\n")
        file.write("P2, 4, 1, 2\n")
        file.write("P3, 9, 2, 1\n")
        file.write("P4, 5, 3, 3\n")
        file.write("P5, 2, 4, 2\n")
    
    # Archivo de recursos de ejemplo
    resource_file = os.path.join(directory, "recursos_ejemplo.txt")
    with open(resource_file, 'w') as file:
        file.write("# Formato: <NOMBRE RECURSO>, <CONTADOR>\n")
        file.write("R1, 1\n")
        file.write("R2, 2\n")
        file.write("R3, 3\n")
    
    # Archivo de acciones de ejemplo
    action_file = os.path.join(directory, "acciones_ejemplo.txt")
    with open(action_file, 'w') as file:
        file.write("# Formato: <PID>, <ACCION>, <RECURSO>, <CICLO>\n")
        file.write("P1, READ, R1, 0\n")
        file.write("P2, WRITE, R1, 2\n")
        file.write("P3, READ, R2, 3\n")
        file.write("P4, READ, R2, 4\n")
        file.write("P5, WRITE, R3, 5\n")
        file.write("P1, WRITE, R3, 6\n")
    
    return {
        "processes": process_file,
        "resources": resource_file,
        "actions": action_file
    }
