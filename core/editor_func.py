from __future__ import annotations
import tkinter as tk
from tkinter import messagebox

# ========== FUNCIONES BÁSICAS DE ARCHIVOS ==========
def abrir_archivo(ruta):
    """
    Abre un archivo y devuelve su contenido como string.
    
    Args:
        ruta (str): Ruta del archivo a abrir
        
    Returns:
        str: Contenido del archivo
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        PermissionError: Si no hay permisos
    """
    try:
        with open(ruta, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
        return contenido
    except FileNotFoundError:
        raise FileNotFoundError(f"El archivo '{ruta}' no existe")
    except PermissionError:
        raise PermissionError(f"No tienes permisos para leer '{ruta}'")
    except Exception as e:
        raise Exception(f"Error inesperado al leer '{ruta}': {e}")

def guardar_archivo(ruta, contenido):
    """
    Guarda contenido en un archivo.
    
    Args:
        ruta (str): Ruta donde guardar el archivo
        contenido (str): Contenido a guardar
        
    Raises:
        PermissionError: Si no hay permisos
        IsADirectoryError: Si la ruta es un directorio
    """
    try:
        with open(ruta, 'w', encoding='utf-8') as archivo:
            archivo.write(contenido)
    except PermissionError:
        raise PermissionError(f"No tienes permisos para escribir en '{ruta}'")
    except IsADirectoryError:
        raise IsADirectoryError(f"'{ruta}' es un directorio, no un archivo")
    except Exception as e:
        raise Exception(f"Error inesperado al guardar '{ruta}': {e}")

# ========== FUNCIONES ADICIONALES ÚTILES ==========
def contar_palabras(texto):
    """Cuenta el número de palabras en un texto"""
    return len(texto.split())

def contar_lineas(texto):
    """Cuenta el número de líneas en un texto"""
    return len(texto.splitlines())

def obtener_extension(ruta):
    """Obtiene la extensión de un archivo"""
    import os
    return os.path.splitext(ruta)[1].lower()

# ========== FUNCIONES PARA EL EDITOR (si quieres usarlas) ==========
def nuevo_archivo():
    """Función placeholder para nuevo archivo (ya no se usa directamente)"""
    messagebox.showinfo("Nuevo", "Función reemplazada por la clase principal")

def abrir_archivo_gui():
    """Función placeholder para abrir (ya no se usa directamente)"""
    messagebox.showinfo("Abrir", "Función reemplazada por la clase principal")

def guardar_archivo_gui():
    """Función placeholder para guardar (ya no se usa directamente)"""
    messagebox.showinfo("Guardar", "Función reemplazada por la clase principal")


import tkinter as tk
from tkinter import ttk

class BuscarReemplazar:
    def __init__(self, app):
        self.app = app
        self.ventana = None
    
    def mostrar(self):
        """Muestra la ventana de buscar y reemplazar"""
        if self.ventana and self.ventana.winfo_exists():
            self.ventana.lift()
            return

        def centrar():
            self.ventana.update_idletasks()
            ancho_ventana = self.ventana.winfo_width()
            alto_ventana = self.ventana.winfo_height()
            ancho_pantalla = self.ventana.winfo_screenwidth()
            alto_pantalla = self.ventana.winfo_screenheight()
            x = (ancho_pantalla // 2) - (ancho_ventana // 2)
            y = (alto_pantalla // 2) - (alto_ventana // 2)
            self.ventana.geometry(f"+{x}+{y}")
        
        self.ventana = tk.Toplevel(self.app.root)
        self.ventana.title("Buscar y Reemplazar")
        self.ventana.geometry("400x200")
        centrar()
        self.ventana.transient(self.app.root)
        self.ventana.grab_set()
        
        # Buscar
        tk.Label(self.ventana, text="Buscar:").grid(row=0, column=0, padx=5, pady=5)
        self.buscar_entry = tk.Entry(self.ventana, width=30)
        self.buscar_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Reemplazar con
        tk.Label(self.ventana, text="Reemplazar con:").grid(row=1, column=0, padx=5, pady=5)
        self.reemplazar_entry = tk.Entry(self.ventana, width=30)
        self.reemplazar_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Botones
        btn_frame = tk.Frame(self.ventana)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text="Buscar", command=self.buscar).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Reemplazar", command=self.reemplazar).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Reemplazar Todo", command=self.reemplazar_todo).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cerrar", command=self.ventana.destroy).pack(side=tk.LEFT, padx=5)
        
        self.buscar_entry.focus()
    
    def buscar(self):
        """Busca el texto en el área de texto"""
        texto_buscar = self.buscar_entry.get()
        if not texto_buscar:
            return
        
        contenido = self.app.plano_texto.get(1.0, tk.END)
        if texto_buscar in contenido:
            # Buscar y seleccionar
            start = "1.0"
            while True:
                start = self.app.plano_texto.search(texto_buscar, start, stopindex=tk.END)
                if not start:
                    break
                end = f"{start}+{len(texto_buscar)}c"
                self.app.plano_texto.tag_add("sel", start, end)
                self.app.plano_texto.see(start)
                break
        else:
            tk.messagebox.showinfo("Buscar", "Texto no encontrado")
    
    def reemplazar(self):
        """Reemplaza el texto seleccionado"""
        texto_buscar = self.buscar_entry.get()
        texto_reemplazar = self.reemplazar_entry.get()
        
        if not texto_buscar:
            return
        
        try:
            sel = self.app.plano_texto.tag_ranges("sel")
            if sel:
                start, end = sel[0], sel[1]
                selected_text = self.app.plano_texto.get(start, end)
                if selected_text == texto_buscar:
                    self.app.plano_texto.delete(start, end)
                    self.app.plano_texto.insert(start, texto_reemplazar)
                    # Buscar siguiente
                    self.buscar()
        except:
            pass
    
    def reemplazar_todo(self):
        """Reemplaza todas las ocurrencias"""
        texto_buscar = self.buscar_entry.get()
        texto_reemplazar = self.reemplazar_entry.get()
        
        if not texto_buscar:
            return
        
        contenido = self.app.plano_texto.get(1.0, tk.END)
        if texto_buscar in contenido:
            nuevo_contenido = contenido.replace(texto_buscar, texto_reemplazar)
            self.app.plano_texto.delete(1.0, tk.END)
            self.app.plano_texto.insert(1.0, nuevo_contenido)
            tk.messagebox.showinfo("Reemplazar", "Reemplazo completado")


def configurar_fuente(app):
    """Permite configurar la fuente del editor"""
    from tkinter import font
    import tkinter.ttk as ttk

    def centrar():
        ventana.update_idletasks()
        ancho_ventana = ventana.winfo_width()
        alto_ventana = ventana.winfo_height()
        ancho_pantalla = ventana.winfo_screenwidth()
        alto_pantalla = ventana.winfo_screenheight()
        x = (ancho_pantalla // 2) - (ancho_ventana // 2)
        y = (alto_pantalla // 2) - (alto_ventana // 2)
        ventana.geometry(f"+{x}+{y}")
    
    ventana = tk.Toplevel(app.root)
    ventana.title("Configurar Fuente")
    ventana.geometry("350x250")
    centrar()
    ventana.transient(app.root)
    ventana.grab_set()
    
    # Obtener fuentes disponibles
    fuentes = list(font.families())
    fuente_actual = font.Font(font=app.plano_texto['font'])
    
    # Selector de fuente
    tk.Label(ventana, text="Fuente:").pack(pady=(10,5))
    fuente_var = tk.StringVar(value=fuente_actual.actual()['family'])
    fuente_combo = ttk.Combobox(ventana, textvariable=fuente_var, values=fuentes, width=35,state='readonly')
    fuente_combo.pack(pady=5)
    
    # Tamaño
    tk.Label(ventana, text="Tamaño:").pack(pady=(10,5))
    tamaño_var = tk.IntVar(value=fuente_actual.actual()['size'])
    tamaño_spin = tk.Spinbox(ventana, from_=8, to=72, textvariable=tamaño_var, width=10)
    tamaño_spin.pack(pady=5)
    
    def aplicar():
        nueva_fuente = (fuente_var.get(), tamaño_var.get())
        app.plano_texto.config(font=nueva_fuente)
        ventana.destroy()
    
    btn_frame = tk.Frame(ventana)
    btn_frame.pack(pady=15)
    tk.Button(btn_frame, text="Aplicar", command=aplicar, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Cancelar", command=ventana.destroy, width=10).pack(side=tk.LEFT, padx=5)