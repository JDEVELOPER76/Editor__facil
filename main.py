import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import shutil
import sys

# Agregar el directorio actual al path para poder importar core
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# ========== IMPORTAR FUNCIONES DEL MÓDULO ==========
from core.editor_func import abrir_archivo, guardar_archivo
from core.editor_func import BuscarReemplazar, configurar_fuente
from core import plugin_mananger as pm


class EditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Archivos")
        self.root.state("zoomed")
        
        # Centrar la ventana
        self.centrar_ventana(root)
        
        # Variable para guardar la ruta del archivo actual
        self.archivo_actual = None
        
        # ========== CARGAR ICONO DE LA VENTANA ==========
        self.cargar_icono()
        
        # ========== CREAR MENÚ (barra de herramientas, sin cascade) ==========
        self.crear_menu()
        
        # ========== CREAR BARRA DE ESTADO ==========
        self.crear_barra_estado()
        
        # ========== CREAR ÁREA DE TEXTO ==========
        self.scroll = tk.Scrollbar(root)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.plano_texto = tk.Text(
            root, wrap=tk.WORD, yscrollcommand=self.scroll.set,
            undo=True, autoseparators=True, maxundo=-1
        )
        self.plano_texto.pack(fill=tk.BOTH, expand=True)
        self.scroll.config(command=self.plano_texto.yview)
        
        # ========== INICIALIZAR SISTEMA DE PLUGINS ==========
        self.plugin_manager = pm.PluginManager(self)
        
        # Crear carpeta plugins si no existe
        if not os.path.exists("plugins"):
            os.makedirs("plugins")
        
        # Descubrir y cargar plugins
        self.plugin_manager.discover_plugins()
        
        # ========== ATAJOS DE TECLADO ==========
        self.root.bind_all("<Control-n>", lambda e: self.nuevo_archivo())
        self.root.bind_all("<Control-o>", lambda e: self.abrir_archivo())
        self.root.bind_all("<Control-s>", lambda e: self.guardar_archivo())
        self.root.bind_all("<Control-h>", lambda e: self.mostrar_buscar())
        self.root.bind_all("<Control-q>", lambda e: self.root.quit())
        self.root.bind_all("<Control-z>", self.deshacer)
        self.root.bind_all("<Control-y>", self.rehacer)
        
        # ========== ACTUALIZAR TÍTULO ==========
        self.actualizar_titulo()
        
        # ========== VINCULAR EVENTOS ==========
        self.plano_texto.bind('<KeyRelease>', self.actualizar_posicion)
        self.plano_texto.bind('<ButtonRelease>', self.actualizar_posicion)
    
    def cargar_icono(self):
        """Carga 'icono.ico' como icono de la ventana si el archivo existe"""
        try:
            # Buscar el icono en múltiples ubicaciones
            icono_path = self._encontrar_icono()
            if icono_path and os.path.exists(icono_path):
                self.root.iconbitmap(icono_path)
        except Exception:
            pass
    
    def _encontrar_icono(self):
        """Busca el icono en múltiples ubicaciones posibles (prioriza core/)"""
        # Lista de rutas a probar en orden de prioridad
        rutas = []
        
        # 1. Si está empaquetado con PyInstaller
        if hasattr(sys, '_MEIPASS'):
            rutas.append(os.path.join(sys._MEIPASS, "core", "icono.ico"))
            rutas.append(os.path.join(sys._MEIPASS, "icono.ico"))  # Fallback
        
        # 2. Si está compilado con Nuitka
        if "__compiled__" in globals() or "__nuitka__" in globals():
            rutas.append(os.path.join(os.path.dirname(sys.argv[0]), "core", "icono.ico"))
            rutas.append(os.path.join(os.path.dirname(sys.argv[0]), "icono.ico"))
        
        # 3. Si es un ejecutable congelado (frozen)
        if getattr(sys, 'frozen', False):
            rutas.append(os.path.join(os.path.dirname(sys.executable), "core", "icono.ico"))
            rutas.append(os.path.join(os.path.dirname(sys.executable), "icono.ico"))
        
        # 4. En el directorio del script (archivo fuente)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        rutas.append(os.path.join(script_dir, "core", "icono.ico"))
        rutas.append(os.path.join(script_dir, "icono.ico"))
        
        # 5. En el directorio base del plugin manager
        base_dir = pm._base_dir() if hasattr(pm, '_base_dir') else os.getcwd()
        rutas.append(os.path.join(base_dir, "core", "icono.ico"))
        rutas.append(os.path.join(base_dir, "icono.ico"))
        
        # 6. En el directorio de trabajo actual
        rutas.append(os.path.join(os.getcwd(), "core", "icono.ico"))
        rutas.append(os.path.join(os.getcwd(), "icono.ico"))
        
        # 7. En el directorio raíz del proyecto (un nivel arriba)
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        rutas.append(os.path.join(parent_dir, "core", "icono.ico"))
        rutas.append(os.path.join(parent_dir, "icono.ico"))
        
        # Probar cada ruta
        for ruta in rutas:
            if os.path.exists(ruta):
                return ruta
        
        return None
    
    def centrar_ventana(self, ventana, width=None, height=None):
        """Centra una ventana en la pantalla"""
        ventana.update_idletasks()
        if width is None:
            width = ventana.winfo_width()
        if height is None:
            height = ventana.winfo_height()
        
        # Obtener dimensiones de la pantalla
        screen_width = ventana.winfo_screenwidth()
        screen_height = ventana.winfo_screenheight()
        
        # Calcular posición
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        ventana.geometry(f"{width}x{height}+{x}+{y}")
    
    def centrar_toplevel(self, toplevel, parent=None):
        """Centra una ventana Toplevel con respecto a su padre"""
        if parent is None:
            parent = self.root
        
        toplevel.update_idletasks()
        width = toplevel.winfo_width()
        height = toplevel.winfo_height()
        
        # Obtener posición del padre
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Calcular posición
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        toplevel.geometry(f"{width}x{height}+{x}+{y}")
    
    def crear_barra_estado(self):
        """Crea la barra de estado en la parte inferior"""
        self.status_bar = tk.Frame(self.root, relief=tk.SUNKEN, bd=1)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Label para información de archivo
        self.status_info = tk.Label(
            self.status_bar, 
            text="Archivo: Nuevo",
            relief=tk.SUNKEN,
            padx=5
        )
        self.status_info.pack(side=tk.LEFT)
        
        # Label para posición del cursor
        self.status_pos = tk.Label(
            self.status_bar,
            text="Línea: 1, Col: 1",
            relief=tk.SUNKEN,
            padx=5
        )
        self.status_pos.pack(side=tk.RIGHT)
    
    def crear_menu(self):
        # Crear la barra de menú principal
        menubar = tk.Menu(self.root)
        self.root.configure(menu=menubar)
        
        # ---------- MENÚ ARCHIVO ----------
        archivo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        
        archivo_menu.add_command(label="Nuevo", command=self.nuevo_archivo, accelerator="Ctrl+N")
        archivo_menu.add_command(label="Abrir...", command=self.abrir_archivo, accelerator="Ctrl+O")
        archivo_menu.add_command(label="Guardar", command=self.guardar_archivo, accelerator="Ctrl+S")
        archivo_menu.add_command(label="Guardar Como...", command=self.guardar_como)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.root.quit, accelerator="Ctrl+Q")
        
        # ---------- MENÚ EDITAR ----------
        editar_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=editar_menu)
        
        editar_menu.add_command(label="Deshacer", command=self.deshacer, accelerator="Ctrl+Z")
        editar_menu.add_command(label="Rehacer", command=self.rehacer, accelerator="Ctrl+Y")
        editar_menu.add_separator()
        editar_menu.add_command(label="Cortar", command=self.cortar, accelerator="Ctrl+X")
        editar_menu.add_command(label="Copiar", command=self.copiar, accelerator="Ctrl+C")
        editar_menu.add_command(label="Pegar", command=self.pegar, accelerator="Ctrl+V")
        editar_menu.add_separator()
        editar_menu.add_command(label="Seleccionar Todo", command=self.seleccionar_todo, accelerator="Ctrl+A")
        editar_menu.add_separator()
        editar_menu.add_command(label="Buscar y Reemplazar", command=self.mostrar_buscar, accelerator="Ctrl+H")
        editar_menu.add_command(label="Configurar Fuente", command=self.mostrar_fuente, accelerator="Ctrl+F")
        
        # ---------- MENÚ VER ----------
        ver_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=ver_menu)
        
        self.mostrar_barra = tk.BooleanVar(value=True)
        ver_menu.add_checkbutton(label="Barra de Estado", variable=self.mostrar_barra, command=self.toggle_barra)
        
        # ---------- MENÚ EXTENSIONES ----------
        extensiones_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Extensiones", menu=extensiones_menu)
        
        extensiones_menu.add_command(label="Ver Extensiones", command=self.mostrar_extensiones)
        extensiones_menu.add_command(label="Instalar Extensión", command=self.instalar_extension)
        extensiones_menu.add_separator()
        extensiones_menu.add_command(label="Recargar Extensiones", command=self.recargar_extensiones)
        
        # ---------- MENÚ AYUDA ----------
        ayuda_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)
        
        ayuda_menu.add_command(label="Acerca de...", command=self.acerca_de)
    
    # ========== FUNCIONES DEL MENÚ EXTENSIONES ==========
    def mostrar_extensiones(self):
        """Muestra una ventana con todas las extensiones cargadas"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Extensiones Cargadas")
        ventana.geometry("500x400")
        self.centrar_toplevel(ventana)
        ventana.transient(self.root)
        ventana.grab_set()
        
        # Título
        tk.Label(ventana, text="Extensiones Cargadas", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Marco para la lista
        frame = tk.Frame(ventana)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scroll = tk.Scrollbar(frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox para mostrar las extensiones
        listbox = tk.Listbox(frame, yscrollcommand=scroll.set, font=("Consolas", 10))
        listbox.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=listbox.yview)
        
        # Cargar información de las extensiones
        plugins = self.plugin_manager.list_plugins()
        if plugins:
            for nombre in plugins:
                plugin = self.plugin_manager.get_plugin(nombre)
                if plugin:
                    try:
                        if hasattr(plugin, 'get_info'):
                            info = plugin.get_info()
                        else:
                            info = {
                                "name": getattr(plugin, 'name', nombre),
                                "version": getattr(plugin, 'version', '1.0'),
                                "author": getattr(plugin, 'author', 'Desconocido'),
                                "description": getattr(plugin, 'description', 'Sin descripción')
                            }
                        listbox.insert(tk.END, f"📦 {info['name']} v{info['version']}")
                        listbox.insert(tk.END, f"   Autor: {info['author']}")
                        listbox.insert(tk.END, f"   Descripción: {info['description']}")
                        listbox.insert(tk.END, "-" * 40)
                    except Exception as e:
                        listbox.insert(tk.END, f"⚠️ Error al cargar: {nombre}")
                        listbox.insert(tk.END, "-" * 40)
        else:
            listbox.insert(tk.END, "No hay extensiones cargadas")
            listbox.insert(tk.END, "")
            listbox.insert(tk.END, "Para instalar una extensión:")
            listbox.insert(tk.END, "1. Copia un archivo .py a la carpeta 'plugins'")
            listbox.insert(tk.END, "2. Ve a Extensiones > Recargar Extensiones")
        
        # Botón cerrar
        tk.Button(ventana, text="Cerrar", command=ventana.destroy, width=15).pack(pady=10)
    
    def instalar_extension(self):
        """Permite instalar una extensión desde un archivo .py"""
        # Seleccionar archivo
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de extensión",
            filetypes=[("Archivos Python", "*.py"), ("Todos los archivos", "*.*")]
        )
        
        if not archivo:
            return
        
        # Directorio de plugins (el mismo que usa el manager para descubrirlos,
        # así no terminan creándose dos carpetas distintas)
        plugin_dir = self.plugin_manager.get_plugins_dir()
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
        
        # Copiar el archivo al directorio de plugins
        nombre_archivo = os.path.basename(archivo)
        destino = os.path.join(plugin_dir, nombre_archivo)
        
        try:
            # Verificar si ya existe
            if os.path.exists(destino):
                respuesta = messagebox.askyesno(
                    "Extensión existente",
                    f"La extensión '{nombre_archivo}' ya existe. ¿Quieres sobrescribirla?"
                )
                if not respuesta:
                    return
            
            # Copiar archivo
            shutil.copy2(archivo, destino)
            messagebox.showinfo("Éxito", f"Extensión '{nombre_archivo}' instalada correctamente")
            
            # Recargar plugins
            self.recargar_extensiones()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo instalar la extensión:\n{e}")
    
    def recargar_extensiones(self):
        """Recarga todas las extensiones"""
        try:
            self.plugin_manager.reload_plugins()
            messagebox.showinfo("Éxito", "Extensiones recargadas correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron recargar las extensiones:\n{e}")
    
    # ========== FUNCIONES DEL MENÚ ARCHIVO ==========
    def nuevo_archivo(self):
        if self.preguntar_guardar():
            self.plano_texto.delete(1.0, tk.END)
            self.archivo_actual = None
            self.actualizar_titulo()
            self.actualizar_posicion()
    
    def abrir_archivo(self):
        if not self.preguntar_guardar():
            return
        
        # Diálogo para seleccionar archivo - ACEPTA CUALQUIER ARCHIVO
        ruta = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[
                ("Todos los archivos", "*.*"),
                ("Archivos de texto", "*.txt"),
                ("Archivos Python", "*.py"),
                ("Archivos Markdown", "*.md"),
                ("Archivos JSON", "*.json"),
                ("Archivos XML", "*.xml"),
                ("Archivos HTML", "*.html;*.htm"),
                ("Archivos CSS", "*.css"),
                ("Archivos JavaScript", "*.js"),
                ("Archivos de configuración", "*.ini;*.cfg;*.conf"),
                ("Archivos de log", "*.log"),
                ("Archivos CSV", "*.csv"),
                ("Archivos de código", "*.c;*.cpp;*.h;*.java;*.go;*.rs;*.php;*.rb;*.pl"),
                ("Archivos de script", "*.sh;*.bash;*.bat;*.cmd"),
            ]
        )
        
        if ruta:
            try:
                # Intentar detectar la codificación automáticamente
                contenido = self._abrir_archivo_con_encoding(ruta)
                self.plano_texto.delete(1.0, tk.END)
                self.plano_texto.insert(1.0, contenido)
                self.archivo_actual = ruta
                self.actualizar_titulo()
                self.actualizar_posicion()
                
                # Mostrar información del archivo
                tamaño = os.path.getsize(ruta)
                tamaño_legible = self._formatear_tamaño(tamaño)
                messagebox.showinfo(
                    "Éxito", 
                    f"Archivo abierto: {os.path.basename(ruta)}\n"
                    f"Tamaño: {tamaño_legible}"
                )
            except UnicodeDecodeError:
                # Error de codificación - ofrecer opciones
                self._manejar_error_codificacion(ruta)
            except MemoryError:
                messagebox.showerror(
                    "Error", 
                    "El archivo es demasiado grande para abrirlo.\n"
                    "Tamaño: " + self._formatear_tamaño(os.path.getsize(ruta))
                )
            except PermissionError:
                messagebox.showerror(
                    "Error", 
                    f"No tienes permisos para leer el archivo:\n{os.path.basename(ruta)}"
                )
            except IsADirectoryError:
                messagebox.showerror(
                    "Error", 
                    f"'{os.path.basename(ruta)}' es un directorio, no un archivo."
                )
            except Exception as e:
                messagebox.showerror(
                    "Error", 
                    f"No se pudo abrir el archivo:\n{str(e)}"
                )
    
    def _abrir_archivo_con_encoding(self, ruta):
        """Intenta abrir un archivo con diferentes codificaciones"""
        # Lista de codificaciones a probar (ordenadas por probabilidad)
        codificaciones = [
            'utf-8',
            'utf-8-sig',  # UTF-8 con BOM
            'latin-1',    # ISO-8859-1
            'cp1252',     # Windows-1252
            'cp850',      # DOS Latin-1
            'iso-8859-15',
            'ascii',
            'mac_roman'
        ]
        
        # Primero intentar con utf-8 (la más común)
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            pass
        
        # Probar con otras codificaciones
        for encoding in codificaciones[1:]:  # Saltamos utf-8 que ya probamos
            try:
                with open(ruta, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception:
                continue
        
        # Si ninguna funciona, leer en modo binario y mostrar advertencia
        try:
            with open(ruta, 'rb') as f:
                datos = f.read()
                # Intentar decodificar ignorando errores
                return datos.decode('utf-8', errors='replace')
        except Exception:
            # Último recurso: leer como texto con reemplazo de errores
            with open(ruta, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
    
    def _manejar_error_codificacion(self, ruta):
        """Maneja errores de codificación ofreciendo opciones al usuario"""
        respuesta = messagebox.askyesnocancel(
            "Error de codificación",
            f"No se pudo determinar la codificación del archivo:\n{os.path.basename(ruta)}\n\n"
            "¿Deseas abrirlo como archivo binario (mostrará caracteres extraños)?\n"
            "Sí: Abrir como binario\n"
            "No: Intentar con otra codificación\n"
            "Cancelar: No abrir el archivo"
        )
        
        if respuesta is None:  # Cancelar
            return
        elif respuesta:  # Sí - Abrir como binario
            try:
                with open(ruta, 'rb') as f:
                    datos = f.read()
                    # Mostrar como texto con caracteres escapados
                    contenido = datos.decode('utf-8', errors='replace')
                    self.plano_texto.delete(1.0, tk.END)
                    self.plano_texto.insert(1.0, contenido)
                    self.archivo_actual = ruta
                    self.actualizar_titulo()
                    self.actualizar_posicion()
                    messagebox.showinfo(
                        "Información", 
                        "El archivo se abrió en modo binario.\n"
                        "Algunos caracteres pueden mostrarse incorrectamente."
                    )
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")
        else:  # No - Intentar con codificación manual
            self._abrir_con_codificacion_manual(ruta)
    
    def _abrir_con_codificacion_manual(self, ruta):
        """Permite al usuario seleccionar la codificación manualmente"""
        codificaciones = [
            'utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 
            'cp850', 'iso-8859-1', 'iso-8859-15', 'ascii'
        ]
        
        # Crear ventana para seleccionar codificación
        ventana = tk.Toplevel(self.root)
        ventana.title("Seleccionar codificación")
        ventana.geometry("400x300")
        self.centrar_toplevel(ventana)
        ventana.transient(self.root)
        ventana.grab_set()
        
        tk.Label(ventana, text="Selecciona la codificación del archivo:", 
                 font=("Arial", 11)).pack(pady=15)
        
        # Frame para el listbox
        frame = tk.Frame(ventana)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scroll = tk.Scrollbar(frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(frame, yscrollcommand=scroll.set, height=6, font=("Consolas", 10))
        listbox.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=listbox.yview)
        
        for enc in codificaciones:
            listbox.insert(tk.END, enc)
        listbox.selection_set(0)
        
        def intentar_abrir():
            try:
                seleccion = listbox.curselection()
                if seleccion:
                    encoding = codificaciones[seleccion[0]]
                    with open(ruta, 'r', encoding=encoding) as f:
                        contenido = f.read()
                        self.plano_texto.delete(1.0, tk.END)
                        self.plano_texto.insert(1.0, contenido)
                        self.archivo_actual = ruta
                        self.actualizar_titulo()
                        self.actualizar_posicion()
                        ventana.destroy()
                        messagebox.showinfo(
                            "Éxito", 
                            f"Archivo abierto con codificación: {encoding}"
                        )
            except UnicodeDecodeError:
                messagebox.showerror(
                    "Error", 
                    f"No se pudo abrir con la codificación seleccionada.\n"
                    "Intenta con otra."
                )
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")
        
        # Botones
        frame_botones = tk.Frame(ventana)
        frame_botones.pack(pady=15)
        
        tk.Button(frame_botones, text="Abrir", command=intentar_abrir, 
                  width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botones, text="Cancelar", command=ventana.destroy, 
                  width=10).pack(side=tk.LEFT, padx=10)
    
    def _formatear_tamaño(self, bytes):
        """Formatea el tamaño de un archivo en unidades legibles"""
        for unidad in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unidad}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"
    
    def guardar_archivo(self):
        if self.archivo_actual:
            try:
                contenido = self.plano_texto.get(1.0, tk.END)
                # Intentar guardar con UTF-8
                try:
                    with open(self.archivo_actual, 'w', encoding='utf-8') as f:
                        f.write(contenido)
                except UnicodeEncodeError:
                    # Si falla UTF-8, usar latin-1
                    with open(self.archivo_actual, 'w', encoding='latin-1') as f:
                        f.write(contenido)
                    messagebox.showwarning(
                        "Advertencia",
                        "El archivo se guardó con codificación latin-1 porque contenía "
                        "caracteres no compatibles con UTF-8."
                    )
                else:
                    messagebox.showinfo("Éxito", "Archivo guardado correctamente")
            except PermissionError:
                messagebox.showerror(
                    "Error",
                    f"No tienes permisos para guardar en:\n{os.path.basename(self.archivo_actual)}"
                )
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")
        else:
            self.guardar_como()
    
    def guardar_como(self):
        ruta = filedialog.asksaveasfilename(
            title="Guardar archivo",
            defaultextension=".txt",
            filetypes=[
                ("Todos los archivos", "*.*"),
                ("Archivos de texto", "*.txt"),
                ("Archivos Python", "*.py"),
                ("Archivos Markdown", "*.md"),
                ("Archivos JSON", "*.json"),
                ("Archivos XML", "*.xml"),
                ("Archivos HTML", "*.html;*.htm"),
                ("Archivos CSS", "*.css"),
                ("Archivos JavaScript", "*.js"),
                ("Archivos de configuración", "*.ini;*.cfg;*.conf"),
                ("Archivos de log", "*.log"),
                ("Archivos CSV", "*.csv"),
            ]
        )
        
        if ruta:
            try:
                contenido = self.plano_texto.get(1.0, tk.END)
                
                # Si el archivo tiene extensión .py, eliminar caracteres BOM si existen
                if ruta.endswith('.py'):
                    contenido = contenido.replace('\ufeff', '')
                
                # Intentar guardar con UTF-8
                try:
                    with open(ruta, 'w', encoding='utf-8') as f:
                        f.write(contenido)
                except UnicodeEncodeError:
                    # Si falla UTF-8, usar latin-1
                    with open(ruta, 'w', encoding='latin-1') as f:
                        f.write(contenido)
                    messagebox.showwarning(
                        "Advertencia",
                        "El archivo se guardó con codificación latin-1 porque contenía "
                        "caracteres no compatibles con UTF-8."
                    )
                else:
                    messagebox.showinfo("Éxito", "Archivo guardado correctamente")
                
                self.archivo_actual = ruta
                self.actualizar_titulo()
                
            except PermissionError:
                messagebox.showerror(
                    "Error",
                    f"No tienes permisos para guardar en:\n{os.path.basename(ruta)}"
                )
            except IsADirectoryError:
                messagebox.showerror(
                    "Error",
                    f"No se puede guardar porque '{os.path.basename(ruta)}' es un directorio."
                )
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"No se pudo guardar el archivo:\n{str(e)}"
                )
    
    # ========== FUNCIONES DEL MENÚ EDITAR ==========
    def deshacer(self, event=None):
        """Deshace la última acción en el área de texto"""
        try:
            self.plano_texto.edit_undo()
        except tk.TclError:
            pass
        return "break"
    
    def rehacer(self, event=None):
        """Rehace la última acción deshecha en el área de texto"""
        try:
            self.plano_texto.edit_redo()
        except tk.TclError:
            pass
        return "break"
    
    def cortar(self):
        self.plano_texto.event_generate("<<Cut>>")
    
    def copiar(self):
        self.plano_texto.event_generate("<<Copy>>")
    
    def pegar(self):
        self.plano_texto.event_generate("<<Paste>>")
    
    def seleccionar_todo(self):
        self.plano_texto.tag_add(tk.SEL, "1.0", tk.END)
        self.plano_texto.mark_set(tk.INSERT, "1.0")
        self.plano_texto.see(tk.INSERT)
    
    def mostrar_buscar(self):
        """Muestra la ventana de buscar y reemplazar"""
        buscar = BuscarReemplazar(self)
        buscar.mostrar()
    
    def mostrar_fuente(self):
        """Muestra la ventana de configuración de fuente"""
        configurar_fuente(self)
    
    # ========== FUNCIONES DEL MENÚ VER ==========
    def toggle_barra(self):
        """Muestra u oculta la barra de estado"""
        if self.mostrar_barra.get():
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            self.status_bar.pack_forget()
    
    # ========== FUNCIONES DEL MENÚ AYUDA ==========
    def acerca_de(self):
        messagebox.showinfo(
            "Acerca de Editor de Archivos",
            "Editor de Archivos v2.0\n\n"
            "Un editor de texto avanzado creado con Python y Tkinter.\n"
            "Funcionalidades:\n"
            "• Abrir y guardar archivos\n"
            "• Atajos de teclado\n"
            "• Menú completo\n"
            "• Buscar y reemplazar\n"
            "• Configuración de fuentes\n"
            "• Barra de estado\n"
            "• Sistema de plugins\n\n"
            "Creado por: Engine dvp"
        )
    
    # ========== FUNCIONES AUXILIARES ==========
    def actualizar_posicion(self, event=None):
        """Actualiza la posición del cursor en la barra de estado"""
        try:
            pos = self.plano_texto.index(tk.INSERT)
            linea, col = pos.split('.')
            self.status_pos.config(text=f"Línea: {linea}, Col: {int(col)+1}")
        except:
            pass
    
    def preguntar_guardar(self):
        """Pregunta si guardar cambios antes de cerrar/nuevo/abrir"""
        if self.plano_texto.get(1.0, tk.END).strip():
            respuesta = messagebox.askyesnocancel(
                "Guardar cambios",
                "¿Quieres guardar los cambios antes de continuar?"
            )
            if respuesta is None:  # Cancelar
                return False
            elif respuesta:  # Sí
                self.guardar_archivo()
                return True
            else:  # No
                return True
        return True
    
    def actualizar_titulo(self):
        """Actualiza el título de la ventana con el nombre del archivo"""
        if self.archivo_actual:
            nombre = os.path.basename(self.archivo_actual)
            self.root.title(f"Editor de Archivos - {nombre}")
            self.status_info.config(text=f"Archivo: {nombre}")
        else:
            self.root.title("Editor de Archivos - Nuevo archivo")
            self.status_info.config(text="Archivo: Nuevo")

# ========== EJECUTAR ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = EditorApp(root)
    root.mainloop()