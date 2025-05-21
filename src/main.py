#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicación principal del simulador Calendar & Sync
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

# Añadir el directorio raíz al path para importaciones relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importaciones locales
from src.gui.scheduler_tab import SchedulerTab
from src.gui.sync_tab import SyncTab
from src.utils.file_loader import create_sample_files

class CalendarSyncApp:
    """Clase principal de la aplicación Calendar & Sync"""
    
    def __init__(self, root):
        """Inicializa la aplicación
        
        Args:
            root: Ventana principal de tkinter
        """
        self.root = root
        self.root.title("Calendar & Sync - Simulador")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        
        # Configurar el tema
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')  # Usar un tema moderno
        except tk.TclError:
            pass  # Ignorar si el tema no está disponible
        
        # Crear frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Añadir pestañas para los diferentes simuladores
        self.tabs = ttk.Notebook(self.main_frame)
        self.tabs.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña para simulador de calendarización
        self.scheduler_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.scheduler_tab, text="Calendarización")
        
        # Pestaña para simulador de sincronización
        self.sync_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.sync_tab, text="Sincronización")
        
        # Inicializar componentes de la interfaz
        self.scheduler_handler = SchedulerTab(self.scheduler_tab)
        self.sync_handler = SyncTab(self.sync_tab)
        
        # Crear directorio de datos para archivos de ejemplo si no existe
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Crea el directorio de datos si no existe."""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

def main():
    """Función principal que inicia la aplicación"""
    root = tk.Tk()
    app = CalendarSyncApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
