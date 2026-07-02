"""
Plugin para exportar el texto a HTML
"""
import tkinter as tk
from tkinter import messagebox, filedialog
from core.plugin_base import PluginBase
import os

class ExportarHtmlPlugin(PluginBase):
    """Plugin que agrega la funcionalidad de exportar a HTML"""
    
    def __init__(self, app):
        super().__init__(app)
        self.name = "Exportador HTML"
        self.version = "1.0"
        self.author = "Engine dvp"
        self.description = "Exporta el texto a un archivo HTML"
    
    def get_info(self):
        """Devuelve la información del plugin - REQUERIDO"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description
        }
    
    def initialize(self):
        """Agrega opción al menú Archivo"""
        try:
            # Obtener el menú Archivo desde el menubar
            menubar = self.app.root.nametowidget(self.app.root['menu'])
            
            # Buscar el menú Archivo (primer elemento del menubar)
            archivo_menu = None
            for i in range(menubar.index("end") + 1):
                try:
                    label = menubar.entrycget(i, "label")
                    if label == "Archivo":
                        archivo_menu = menubar.winfo_children()[i]
                        break
                except:
                    continue
            
            if archivo_menu:
                # Agregar opción al menú Archivo
                archivo_menu.add_command(
                    label="Exportar a HTML...",
                    command=self.exportar_html
                )
            else:
                # Fallback: agregar al menú Extensiones
                for i in range(menubar.index("end") + 1):
                    try:
                        label = menubar.entrycget(i, "label")
                        if label == "Extensiones":
                            extensiones_menu = menubar.winfo_children()[i]
                            extensiones_menu.add_separator()
                            extensiones_menu.add_command(
                                label="Exportar a HTML...",
                                command=self.exportar_html
                            )
                            break
                    except:
                        continue
        except Exception as e:
            print(f"Error al inicializar plugin: {e}")
    
    def cleanup(self):
        """Limpia el plugin antes de recargar"""
        try:
            menubar = self.app.root.nametowidget(self.app.root['menu'])
            
            for i in range(menubar.index("end") + 1):
                try:
                    label = menubar.entrycget(i, "label")
                    if label == "Archivo":
                        archivo_menu = menubar.winfo_children()[i]
                        # Buscar y eliminar la opción del menú
                        for j in range(archivo_menu.index("end") + 1):
                            try:
                                item_label = archivo_menu.entrycget(j, "label")
                                if item_label == "Exportar a HTML...":
                                    archivo_menu.delete(j)
                                    break
                            except:
                                continue
                        break
                except:
                    continue
        except:
            pass
    
    def exportar_html(self):
        """Exporta el contenido actual a HTML"""
        texto = self.app.plano_texto.get(1.0, tk.END)
        
        if not texto.strip():
            messagebox.showwarning("Advertencia", "No hay texto para exportar")
            return
        
        # Solicitar ubicación
        ruta = filedialog.asksaveasfilename(
            title="Exportar a HTML",
            defaultextension=".html",
            filetypes=[("Archivos HTML", "*.html"), ("Todos los archivos", "*.*")]
        )
        
        if not ruta:
            return
        
        # Generar HTML
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documento Exportado</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            background-color: #ffffff;
        }}
        pre {{
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: Consolas, monospace;
            font-size: 14px;
            max-width: 800px;
            width: 100%;
            padding: 0;
            margin: 0;
            background: none;
            border: none;
        }}
    </style>
</head>
<body>
    <pre>{texto}</pre>
</body>
</html>"""
        
        try:
            with open(ruta, 'w', encoding='utf-8') as f:
                f.write(html_content)
            messagebox.showinfo("Éxito", f"Archivo exportado correctamente:\n{os.path.basename(ruta)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")
    
    def _get_fecha(self):
        """Obtiene la fecha actual formateada"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")