import os
import sys
import importlib
import importlib.util
import inspect
from typing import Dict, List, Any


def _base_dir() -> str:
    """
    Devuelve la carpeta base de la aplicación, sin depender del
    directorio de trabajo actual (cwd).

    - Si el programa corre "congelado" (ej. compilado con Nuitka/PyInstaller),
      usa la carpeta donde está el ejecutable.
    - Si corre como script normal, usa la carpeta donde está este archivo.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    if "__compiled__" in globals():  # Nuitka standalone
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.dirname(os.path.abspath(__file__))



class PluginManager:
    """Gestor de plugins/extensiones para el editor"""
    
    def __init__(self, app):
        self.app = app
        self.plugins: Dict[str, Any] = {}
        self.plugin_paths: List[str] = []
        self.loaded_modules = set()
        self.plugin_dir: str = None  # ruta absoluta resuelta, ver get_plugins_dir()
    
    def get_plugins_dir(self) -> str:
        """
        Ruta absoluta de la carpeta de plugins que está usando el manager.
        Cualquier otra parte del código (ej. instalar_extension en main.py)
        debe usar este método en vez de escribir "plugins" a mano, para que
        nunca queden dos carpetas distintas apuntando a cosas distintas.
        """
        if self.plugin_dir is None:
            self.plugin_dir = os.path.join(_base_dir(), "plugins")
        return self.plugin_dir
    
    def discover_plugins(self, plugin_dir: str = "plugins"):
        """Descubre y carga todos los plugins en un directorio"""
        # Anclar la ruta a la carpeta de la app, no al cwd (que cambia
        # según cómo se lance el programa: IDE, doble clic, .exe, etc.)
        if not os.path.isabs(plugin_dir):
            plugin_dir = os.path.join(_base_dir(), plugin_dir)

        self.plugin_dir = plugin_dir  # quedar registrado para get_plugins_dir()

        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
            self._create_example_plugin(plugin_dir)
            return
        
        if plugin_dir not in sys.path:
            sys.path.insert(0, os.path.abspath(plugin_dir))
        
        for filename in os.listdir(plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                plugin_name = filename[:-3]
                if plugin_name not in self.loaded_modules:
                    self._load_plugin(plugin_name, plugin_dir)
                    self.loaded_modules.add(plugin_name)
    
    def _load_plugin(self, plugin_name: str, plugin_dir: str = "plugins"):
        """Carga un plugin específico usando importlib"""
        try:
            plugin_path = os.path.join(plugin_dir, f"{plugin_name}.py")
            
            # Usar importlib.util para cargar el módulo
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None:
                return
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Buscar la clase del plugin
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    name != 'PluginBase' and
                    hasattr(obj, '__bases__')):
                    for base in obj.__bases__:
                        if base.__name__ == 'PluginBase':
                            plugin_class = obj
                            break
                    if plugin_class:
                        break
            
            if plugin_class:
                plugin_instance = plugin_class(self.app)
                self.plugins[plugin_name] = plugin_instance
                
                if hasattr(plugin_instance, 'initialize'):
                    plugin_instance.initialize()

        except Exception:
            pass
    
    def _create_example_plugin(self, plugin_dir: str):
        """Crea un plugin de ejemplo"""
        example_content = '''"""
Plugin de ejemplo para el editor de texto
"""
import tkinter as tk
from tkinter import messagebox
from core.plugin_base import PluginBase

class EjemploPlugin(PluginBase):
    """Plugin de ejemplo que agrega un menú de prueba"""
    
    def __init__(self, app):
        super().__init__(app)
        self.name = "Ejemplo"
        self.version = "1.0"
        self.author = "Sistema"
        self.description = "Plugin de ejemplo"
    
    def initialize(self):
        """Inicializa el plugin"""
        menu = self.crear_menu("Ejemplo")
        
        menu.add_command(label="Saludar", command=self.saludar)
        menu.add_command(label="Contar palabras", command=self.contar_palabras)
    
    def saludar(self):
        messagebox.showinfo("Plugin Ejemplo", "¡Hola desde el plugin de ejemplo!")
    
    def contar_palabras(self):
        texto = self.app.plano_texto.get(1.0, tk.END)
        palabras = len(texto.split())
        messagebox.showinfo("Contador", f"El texto tiene {palabras} palabras")
'''
        with open(os.path.join(plugin_dir, 'ejemplo_plugin.py'), 'w', encoding='utf-8') as f:
            f.write(example_content)
    
    def get_plugin(self, name: str) -> Any:
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())
    
    def reload_plugins(self):
        """Recarga todos los plugins (cualquier cantidad, sin nombres fijos)"""
        # Limpiar plugins activos
        for name in list(self.plugins.keys()):
            try:
                plugin = self.plugins[name]
                if hasattr(plugin, 'cleanup'):
                    plugin.cleanup()
            except Exception:
                pass

        # Eliminar del caché de módulos SOLO los plugins que nosotros cargamos
        # (self.loaded_modules ya tiene los nombres reales, sin importar
        # cuántos sean ni cómo se llamen)
        for module_name in self.loaded_modules:
            sys.modules.pop(module_name, None)

        self.plugins.clear()
        self.loaded_modules.clear()

        self.discover_plugins()