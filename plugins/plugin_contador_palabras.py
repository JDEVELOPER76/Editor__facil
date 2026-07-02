"""
Plugin que muestra un contador de palabras en la barra de estado
"""
import tkinter as tk
from core.plugin_base import PluginBase

class ContadorPalabrasPlugin(PluginBase):
    """Plugin que agrega un contador de palabras en tiempo real"""
    
    def __init__(self, app):
        super().__init__(app)
        self.name = "Contador de Palabras"
        self.version = "1.0"
        self.author = "Engine dvp"
        self.description = "Muestra el número de palabras en el texto"
        
        # Variable para almacenar el label de la barra de estado
        self.status_label = None
    
    def initialize(self):
        """Agrega el contador a la barra de estado"""
        # Crear un label en la barra de estado (se destruye solo en cleanup())
        self.status_label = self.crear_widget(tk.Label(
            self.app.status_bar, 
            text="Palabras: 0",
            relief=tk.SUNKEN,
            padx=5
        ))
        self.status_label.pack(side=tk.RIGHT)
        
        # Vincular evento de cambio de texto (se desvincula solo en cleanup())
        self.vincular(self.app.plano_texto, '<KeyRelease>', self.actualizar_contador)
        
        # Actualizar inicialmente
        self.actualizar_contador()
    
    def actualizar_contador(self, event=None):
        """Actualiza el contador de palabras"""
        texto = self.app.plano_texto.get(1.0, tk.END)
        palabras = len(texto.split())
        self.status_label.config(text=f"Palabras: {palabras}")