import tkinter as tk


class PluginBase:
    """
    Clase base para todos los plugins.

    Provee helpers (crear_menu, agregar_a_menu, crear_widget, vincular) que
    registran automáticamente lo que el plugin agrega a la interfaz, para
    poder deshacerlo solo en cleanup() y evitar que al recargar (Extensiones
    → Recargar Extensiones) los menús/widgets se dupliquen.

    Si tu plugin sobreescribe cleanup(), debe llamar a super().cleanup()
    (al inicio o al final) para no perder esta limpieza automática.
    """

    def __init__(self, app):
        self.app = app
        self.name = "Plugin Base"
        self.version = "1.0"
        self.author = "Desconocido"
        self.description = "Plugin base"

        # Registro interno de lo que el plugin va agregando a la UI
        self._menus_creados = []     # [(label, menu_widget), ...] cascades propios
        self._items_creados = []     # [(menu_padre, label), ...] agregados a un menú existente
        self._widgets_creados = []   # widgets propios (labels, frames, etc.)
        self._bindings_creados = []  # [(widget, evento, funcid), ...]

    # ---------- Helpers para que los plugins se "limpien" solos ----------

    def crear_menu(self, label: str) -> tk.Menu:
        """Crea un menú propio como botón desplegable en la barra de herramientas."""
        menu = tk.Menu(self.app.menu_bar, tearoff=0)
        boton = tk.Menubutton(self.app.menu_bar, text=label, menu=menu, relief=tk.FLAT)
        boton.pack(side=tk.LEFT, padx=2)
        self._menus_creados.append(boton)
        return menu

    def agregar_a_menu(self, menu_padre: tk.Menu, label: str, **kwargs):
        """Agrega un comando a un menú ya existente (ej. archivo_menu)."""
        menu_padre.add_command(label=label, **kwargs)
        self._items_creados.append((menu_padre, label))

    def crear_widget(self, widget):
        """Registra un widget propio para destruirlo en cleanup()."""
        self._widgets_creados.append(widget)
        return widget

    def vincular(self, widget, evento: str, callback, add='+'):
        """Vincula un evento y lo registra para desvincularlo en cleanup()."""
        funcid = widget.bind(evento, callback, add)
        self._bindings_creados.append((widget, evento, funcid))
        return funcid

    # ---------- Ciclo de vida ----------

    def initialize(self):
        """Método llamado cuando se carga el plugin"""
        pass

    def cleanup(self):
        """
        Método llamado cuando se descarga/recarga el plugin.
        Deshace automáticamente todo lo creado con los helpers de arriba.
        """
        for boton in self._menus_creados:
            try:
                boton.destroy()
            except Exception:
                pass
        self._menus_creados.clear()

        for menu_padre, label in self._items_creados:
            try:
                menu_padre.delete(label)
            except Exception:
                pass
        self._items_creados.clear()

        for widget in self._widgets_creados:
            try:
                widget.destroy()
            except Exception:
                pass
        self._widgets_creados.clear()

        for widget, evento, funcid in self._bindings_creados:
            try:
                widget.unbind(evento, funcid)
            except Exception:
                pass
        self._bindings_creados.clear()

    def get_info(self) -> dict:
        """Retorna información del plugin"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description
        }