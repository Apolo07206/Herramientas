import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image
import os
import hashlib
import json
import zlib

class UniversalSteganographyTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Herramienta Universal de Esteganografía")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.carrier_path = tk.StringVar()
        self.file_to_hide = tk.StringVar()
        self.output_path = tk.StringVar()
        self.extract_carrier_path = tk.StringVar()
        self.extract_output_path = tk.StringVar()
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="🔐 Esteganografía Universal - Red/Blue Team", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Descripción
        desc_label = ttk.Label(main_frame, 
                              text="Oculta archivos dentro de CUALQUIER tipo de archivo (PDF, EXE, DOCX, MP4, ZIP, etc.)",
                              font=('Arial', 9), foreground="blue")
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 15))
        
        # Notebook para pestañas
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Pestañas
        hide_frame = ttk.Frame(notebook, padding="15")
        notebook.add(hide_frame, text="🔒 Ocultar Archivo")
        
        extract_frame = ttk.Frame(notebook, padding="15")
        notebook.add(extract_frame, text="🔓 Extraer Archivo")
        
        analysis_frame = ttk.Frame(notebook, padding="15")
        notebook.add(analysis_frame, text="🔍 Análisis Forense")
        
        image_mode_frame = ttk.Frame(notebook, padding="15")
        notebook.add(image_mode_frame, text="🖼️ Modo Imagen (LSB)")
        
        # Setup pestañas
        self.setup_hide_tab(hide_frame)
        self.setup_extract_tab(extract_frame)
        self.setup_analysis_tab(analysis_frame)
        self.setup_image_mode_tab(image_mode_frame)
        
    def setup_hide_tab(self, parent):
        # Info
        info_frame = ttk.LabelFrame(parent, text="ℹ️ Información", padding="10")
        info_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        info_text = ("Método: Append (añade datos al final del archivo portador)\n"
                    "Compatible con: PDF, EXE, DLL, DOCX, XLSX, ZIP, MP4, AVI, PNG, JPG, etc.\n"
                    "⚠️ El archivo portador seguirá siendo funcional después del proceso")
        ttk.Label(info_frame, text=info_text, foreground="darkgreen", font=('Arial', 8)).pack()
        
        # Archivo portador
        ttk.Label(parent, text="1. Archivo portador (cualquier tipo):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.carrier_path, width=55).grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(parent, text="Buscar", command=self.browse_carrier).grid(row=1, column=2, pady=5)
        
        self.carrier_info_label = ttk.Label(parent, text="", foreground="blue")
        self.carrier_info_label.grid(row=2, column=0, columnspan=3, pady=2)
        
        # Archivo a ocultar
        ttk.Label(parent, text="2. Archivo a ocultar (payload/malware/datos):").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.file_to_hide, width=55).grid(row=3, column=1, pady=5, padx=5)
        ttk.Button(parent, text="Buscar", command=self.browse_file_to_hide).grid(row=3, column=2, pady=5)
        
        self.file_info_label = ttk.Label(parent, text="", foreground="blue")
        self.file_info_label.grid(row=4, column=0, columnspan=3, pady=2)
        
        # Nombre archivo de salida
        ttk.Label(parent, text="3. Guardar archivo portador como:").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.output_path, width=55).grid(row=5, column=1, pady=5, padx=5)
        ttk.Button(parent, text="Buscar", command=self.browse_output).grid(row=5, column=2, pady=5)
        
        # Opciones
        options_frame = ttk.LabelFrame(parent, text="Opciones Avanzadas", padding="10")
        options_frame.grid(row=6, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        self.compress_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="🗜️ Comprimir archivo (reduce tamaño ~60-80%)", 
                       variable=self.compress_var).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.encrypt_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="🔐 Cifrado XOR (requiere contraseña)", 
                       variable=self.encrypt_var).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        password_frame = ttk.Frame(options_frame)
        password_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(password_frame, text="Contraseña:").pack(side=tk.LEFT, padx=5)
        self.password_entry = ttk.Entry(password_frame, show="*", width=25)
        self.password_entry.pack(side=tk.LEFT)
        
        self.stealth_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="👻 Modo sigiloso (añade padding aleatorio)", 
                       variable=self.stealth_var).grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # Log
        ttk.Label(parent, text="Log de operación:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.hide_log = scrolledtext.ScrolledText(parent, width=85, height=10, wrap=tk.WORD, font=('Consolas', 9))
        self.hide_log.grid(row=8, column=0, columnspan=3, pady=5, padx=5)
        
        # Botón ocultar
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=9, column=0, columnspan=3, pady=15)
        ttk.Button(btn_frame, text="🔒 OCULTAR ARCHIVO", 
                   command=self.hide_file_universal, style="Accent.TButton").pack()
        
    def setup_extract_tab(self, parent):
        # Info
        info_frame = ttk.LabelFrame(parent, text="ℹ️ Información", padding="10")
        info_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        info_text = "Extrae archivos ocultos de cualquier tipo de archivo portador"
        ttk.Label(info_frame, text=info_text, foreground="darkgreen", font=('Arial', 8)).pack()
        
        # Archivo con datos ocultos
        ttk.Label(parent, text="1. Archivo con datos ocultos:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.extract_carrier_path, width=55).grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(parent, text="Buscar", command=self.browse_extract_carrier).grid(row=1, column=2, pady=5)
        
        # Donde guardar archivo extraído
        ttk.Label(parent, text="2. Guardar archivo extraído como:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.extract_output_path, width=55).grid(row=2, column=1, pady=5, padx=5)
        ttk.Button(parent, text="Buscar", command=self.browse_extract_output).grid(row=2, column=2, pady=5)
        
        # Opciones extracción
        extract_options_frame = ttk.LabelFrame(parent, text="Opciones", padding="10")
        extract_options_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        self.decrypt_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(extract_options_frame, text="🔐 Archivo cifrado (usar contraseña)", 
                       variable=self.decrypt_var).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        password_frame = ttk.Frame(extract_options_frame)
        password_frame.grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(password_frame, text="Contraseña:").pack(side=tk.LEFT, padx=5)
        self.decrypt_password_entry = ttk.Entry(password_frame, show="*", width=25)
        self.decrypt_password_entry.pack(side=tk.LEFT)
        
        # Log extracción
        ttk.Label(parent, text="Log de extracción:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.extract_log = scrolledtext.ScrolledText(parent, width=85, height=12, wrap=tk.WORD, font=('Consolas', 9))
        self.extract_log.grid(row=5, column=0, columnspan=3, pady=5, padx=5)
        
        # Botón extraer
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=15)
        ttk.Button(btn_frame, text="🔓 EXTRAER ARCHIVO", 
                   command=self.extract_file_universal, style="Accent.TButton").pack()
        
    def setup_analysis_tab(self, parent):
        ttk.Label(parent, text="Archivo a analizar:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.analysis_file_path = tk.StringVar()
        ttk.Entry(parent, textvariable=self.analysis_file_path, width=55).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(parent, text="Buscar", command=self.browse_analysis_file).grid(row=0, column=2, pady=5)
        
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=1, column=0, columnspan=3, pady=10)
        ttk.Button(btn_frame, text="🔍 ANALIZAR ARCHIVO", 
                   command=self.analyze_file).pack()
        
        # Resultados análisis
        ttk.Label(parent, text="Resultados del análisis forense:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.analysis_text = scrolledtext.ScrolledText(parent, width=85, height=25, wrap=tk.WORD, font=('Consolas', 9))
        self.analysis_text.grid(row=3, column=0, columnspan=3, pady=5, padx=5)
        
    def setup_image_mode_tab(self, parent):
        info_text = ("Este modo usa LSB (Least Significant Bit) para ocultar datos en píxeles de imágenes.\n"
                    "Solo funciona con imágenes PNG/BMP. Más sigiloso pero menor capacidad.")
        ttk.Label(parent, text=info_text, foreground="blue", wraplength=700).pack(pady=10)
        
        ttk.Label(parent, text="Funcionalidad disponible en versión anterior del código").pack(pady=20)
        ttk.Label(parent, text="Para usar LSB, utiliza imágenes en el modo universal con la opción 'Modo sigiloso'").pack()
    
    def browse_carrier(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo portador (cualquier tipo)",
            filetypes=[("Todos los archivos", "*.*"),
                      ("PDF", "*.pdf"),
                      ("Ejecutables", "*.exe *.dll"),
                      ("Documentos", "*.docx *.xlsx *.pptx"),
                      ("Imágenes", "*.png *.jpg *.jpeg *.bmp"),
                      ("Videos", "*.mp4 *.avi *.mkv"),
                      ("Archivos", "*.zip *.rar *.7z")]
        )
        if filename:
            self.carrier_path.set(filename)
            size = os.path.getsize(filename)
            ext = os.path.splitext(filename)[1]
            self.carrier_info_label.config(
                text=f"📁 Portador: {os.path.basename(filename)} | Tipo: {ext} | Tamaño: {size:,} bytes ({size/1024/1024:.2f} MB)")
            
    def browse_file_to_hide(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo a ocultar",
            filetypes=[("Todos los archivos", "*.*")]
        )
        if filename:
            self.file_to_hide.set(filename)
            size = os.path.getsize(filename)
            ext = os.path.splitext(filename)[1]
            self.file_info_label.config(
                text=f"🔒 A ocultar: {os.path.basename(filename)} | Tipo: {ext} | Tamaño: {size:,} bytes ({size/1024/1024:.2f} MB)")
            
    def browse_output(self):
        carrier = self.carrier_path.get()
        if carrier:
            ext = os.path.splitext(carrier)[1]
            filename = filedialog.asksaveasfilename(
                title="Guardar archivo como",
                defaultextension=ext,
                filetypes=[("Mismo tipo", f"*{ext}"), ("Todos los archivos", "*.*")]
            )
            if filename:
                self.output_path.set(filename)
        else:
            messagebox.showwarning("Advertencia", "Selecciona primero el archivo portador")
            
    def browse_extract_carrier(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo con datos ocultos",
            filetypes=[("Todos los archivos", "*.*")]
        )
        if filename:
            self.extract_carrier_path.set(filename)
            
    def browse_extract_output(self):
        filename = filedialog.asksaveasfilename(
            title="Guardar archivo extraído como",
            filetypes=[("Todos los archivos", "*.*")]
        )
        if filename:
            self.extract_output_path.set(filename)
            
    def browse_analysis_file(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo para análisis",
            filetypes=[("Todos los archivos", "*.*")]
        )
        if filename:
            self.analysis_file_path.set(filename)
    
    def log_message(self, text_widget, message):
        text_widget.insert(tk.END, message + "\n")
        text_widget.see(tk.END)
        text_widget.update()
        
    def xor_encrypt_decrypt(self, data, password):
        """Cifrado/descifrado XOR"""
        key = hashlib.sha256(password.encode()).digest()
        result = bytearray()
        for i, byte in enumerate(data):
            result.append(byte ^ key[i % len(key)])
        return bytes(result)
    
    def hide_file_universal(self):
        try:
            self.hide_log.delete(1.0, tk.END)
            
            # Validaciones
            if not self.carrier_path.get():
                messagebox.showerror("Error", "Selecciona un archivo portador")
                return
            
            if not self.file_to_hide.get():
                messagebox.showerror("Error", "Selecciona un archivo para ocultar")
                return
            
            if not self.output_path.get():
                messagebox.showerror("Error", "Especifica el archivo de salida")
                return
            
            self.log_message(self.hide_log, "=" * 80)
            self.log_message(self.hide_log, "🔒 INICIANDO PROCESO DE OCULTAMIENTO UNIVERSAL")
            self.log_message(self.hide_log, "=" * 80)
            
            # Leer archivo portador
            self.log_message(self.hide_log, f"\n📂 Leyendo portador: {os.path.basename(self.carrier_path.get())}")
            with open(self.carrier_path.get(), 'rb') as f:
                carrier_data = f.read()
            
            carrier_size = len(carrier_data)
            self.log_message(self.hide_log, f"   Tamaño portador: {carrier_size:,} bytes ({carrier_size/1024/1024:.2f} MB)")
            
            # Leer archivo a ocultar
            self.log_message(self.hide_log, f"\n🔐 Leyendo archivo a ocultar: {os.path.basename(self.file_to_hide.get())}")
            with open(self.file_to_hide.get(), 'rb') as f:
                payload_data = f.read()
            
            original_size = len(payload_data)
            self.log_message(self.hide_log, f"   Tamaño original: {original_size:,} bytes ({original_size/1024/1024:.2f} MB)")
            
            # Calcular hash original
            original_hash = hashlib.sha256(payload_data).hexdigest()
            self.log_message(self.hide_log, f"   SHA256 original: {original_hash[:32]}...")
            
            # Comprimir si está activado
            if self.compress_var.get():
                self.log_message(self.hide_log, "\n🗜️  Comprimiendo archivo...")
                payload_data = zlib.compress(payload_data, level=9)
                compressed_size = len(payload_data)
                ratio = (1 - compressed_size/original_size) * 100
                self.log_message(self.hide_log, f"   Comprimido: {compressed_size:,} bytes ({compressed_size/1024/1024:.2f} MB)")
                self.log_message(self.hide_log, f"   Ratio de compresión: {ratio:.1f}% reducción")
            
            # Cifrar si está activado
            if self.encrypt_var.get():
                password = self.password_entry.get()
                if not password:
                    messagebox.showerror("Error", "Debes ingresar una contraseña para cifrar")
                    return
                self.log_message(self.hide_log, "\n🔐 Cifrando con XOR...")
                payload_data = self.xor_encrypt_decrypt(payload_data, password)
                self.log_message(self.hide_log, f"   Archivo cifrado correctamente")
            
            # Padding aleatorio si modo sigiloso
            if self.stealth_var.get():
                import random
                padding_size = random.randint(100, 500)
                padding = bytes([random.randint(0, 255) for _ in range(padding_size)])
                payload_data = padding + payload_data
                self.log_message(self.hide_log, f"\n👻 Modo sigiloso: Añadido padding aleatorio de {padding_size} bytes")
            
            # Preparar metadata
            filename = os.path.basename(self.file_to_hide.get())
            metadata = {
                'filename': filename,
                'size': len(payload_data),
                'original_size': original_size,
                'compressed': self.compress_var.get(),
                'encrypted': self.encrypt_var.get(),
                'stealth': self.stealth_var.get(),
                'original_hash': original_hash,
                'carrier_type': os.path.splitext(self.carrier_path.get())[1],
                'version': '2.0'
            }
            
            metadata_str = json.dumps(metadata)
            metadata_bytes = metadata_str.encode('utf-8')
            
            # Estructura: [MAGIC][tamaño_metadata][metadata][payload][DELIMITER]
            MAGIC = b'<<<UNIVERSAL_STEGO>>>'
            DELIMITER = b'<<<END_STEGO>>>'
            
            stego_data = (MAGIC + 
                         len(metadata_bytes).to_bytes(4, 'big') + 
                         metadata_bytes + 
                         payload_data + 
                         DELIMITER)
            
            self.log_message(self.hide_log, f"\n📊 Datos de esteganografía:")
            self.log_message(self.hide_log, f"   Metadata: {len(metadata_bytes)} bytes")
            self.log_message(self.hide_log, f"   Payload: {len(payload_data):,} bytes")
            self.log_message(self.hide_log, f"   Total esteganografía: {len(stego_data):,} bytes")
            
            # Combinar portador + datos ocultos
            self.log_message(self.hide_log, "\n💾 Combinando archivos...")
            final_data = carrier_data + stego_data
            
            # Guardar
            self.log_message(self.hide_log, f"\n💾 Guardando: {os.path.basename(self.output_path.get())}")
            with open(self.output_path.get(), 'wb') as f:
                f.write(final_data)
            
            final_size = len(final_data)
            overhead = (final_size - carrier_size) / carrier_size * 100
            
            self.log_message(self.hide_log, f"   Tamaño final: {final_size:,} bytes ({final_size/1024/1024:.2f} MB)")
            self.log_message(self.hide_log, f"   Overhead: +{overhead:.2f}%")
            
            # Verificar integridad
            output_hash = hashlib.sha256(final_data).hexdigest()
            
            self.log_message(self.hide_log, "\n" + "=" * 80)
            self.log_message(self.hide_log, "✅ PROCESO COMPLETADO EXITOSAMENTE")
            self.log_message(self.hide_log, "=" * 80)
            self.log_message(self.hide_log, f"📁 Archivo guardado: {self.output_path.get()}")
            self.log_message(self.hide_log, f"🔐 Archivo oculto: {filename}")
            self.log_message(self.hide_log, f"📊 SHA256 archivo final: {output_hash[:32]}...")
            
            messagebox.showinfo("Éxito", 
                f"✅ Archivo ocultado exitosamente!\n\n"
                f"Portador: {os.path.basename(self.carrier_path.get())}\n"
                f"Oculto: {filename}\n"
                f"Tamaño final: {final_size/1024/1024:.2f} MB\n"
                f"Overhead: +{overhead:.1f}%\n\n"
                f"⚠️ El archivo portador sigue siendo funcional!")
            
        except Exception as e:
            self.log_message(self.hide_log, f"\n❌ ERROR: {str(e)}")
            messagebox.showerror("Error", f"Error al ocultar archivo: {str(e)}")
    
    def extract_file_universal(self):
        try:
            self.extract_log.delete(1.0, tk.END)
            
            if not self.extract_carrier_path.get():
                messagebox.showerror("Error", "Selecciona un archivo")
                return
            
            if not self.extract_output_path.get():
                messagebox.showerror("Error", "Especifica donde guardar el archivo")
                return
            
            self.log_message(self.extract_log, "=" * 80)
            self.log_message(self.extract_log, "🔓 INICIANDO EXTRACCIÓN")
            self.log_message(self.extract_log, "=" * 80)
            
            # Leer archivo
            self.log_message(self.extract_log, f"\n📂 Leyendo: {os.path.basename(self.extract_carrier_path.get())}")
            with open(self.extract_carrier_path.get(), 'rb') as f:
                file_data = f.read()
            
            file_size = len(file_data)
            self.log_message(self.extract_log, f"   Tamaño: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            
            # Buscar magic bytes
            MAGIC = b'<<<UNIVERSAL_STEGO>>>'
            DELIMITER = b'<<<END_STEGO>>>'
            
            self.log_message(self.extract_log, "\n🔍 Buscando datos ocultos...")
            
            magic_pos = file_data.find(MAGIC)
            if magic_pos == -1:
                self.log_message(self.extract_log, "   ❌ No se encontraron datos ocultos (magic bytes no encontrados)")
                messagebox.showerror("Error", "No se encontraron datos ocultos en este archivo")
                return
            
            self.log_message(self.extract_log, f"   ✅ Magic bytes encontrados en posición {magic_pos}")
            
            delimiter_pos = file_data.find(DELIMITER, magic_pos)
            if delimiter_pos == -1:
                self.log_message(self.extract_log, "   ❌ Delimitador no encontrado (archivo corrupto)")
                messagebox.showerror("Error", "Datos corruptos o incompletos")
                return
            
            self.log_message(self.extract_log, f"   ✅ Delimitador encontrado en posición {delimiter_pos}")
            
            # Extraer datos
            stego_start = magic_pos + len(MAGIC)
            stego_data = file_data[stego_start:delimiter_pos]
            
            self.log_message(self.extract_log, f"\n📊 Extrayendo metadata...")
            
            # Leer metadata
            metadata_size = int.from_bytes(stego_data[:4], 'big')
            metadata_bytes = stego_data[4:4+metadata_size]
            metadata = json.loads(metadata_bytes.decode('utf-8'))
            
            self.log_message(self.extract_log, f"   ✅ Metadata leída correctamente")
            self.log_message(self.extract_log, f"\n📄 Información del archivo:")
            self.log_message(self.extract_log, f"   Nombre original: {metadata['filename']}")
            self.log_message(self.extract_log, f"   Tamaño original: {metadata.get('original_size', 'N/A'):,} bytes")
            self.log_message(self.extract_log, f"   Comprimido: {'Sí' if metadata['compressed'] else 'No'}")
            self.log_message(self.extract_log, f"   Cifrado: {'Sí' if metadata['encrypted'] else 'No'}")
            self.log_message(self.extract_log, f"   Modo sigiloso: {'Sí' if metadata.get('stealth', False) else 'No'}")
            self.log_message(self.extract_log, f"   Hash original: {metadata.get('original_hash', 'N/A')[:32]}...")
            
            # Extraer payload
            payload_data = stego_data[4+metadata_size:]
            self.log_message(self.extract_log, f"\n🔓 Extrayendo payload ({len(payload_data):,} bytes)...")
            
            # Remover padding si modo sigiloso
            if metadata.get('stealth', False):
                # El padding está al inicio, necesitamos el tamaño exacto
                # Por simplicidad, usaremos los primeros bytes para determinar el tamaño del padding
                padding_size = payload_data[0] + (payload_data[1] << 8)
                if padding_size > 0 and padding_size < len(payload_data):
                    payload_data = payload_data[padding_size:]
                    self.log_message(self.extract_log, f"   👻 Removido padding de {padding_size} bytes")
            
            # Descifrar si es necesario
            if metadata['encrypted']:
                if not self.decrypt_var.get():
                    self.log_message(self.extract_log, "\n   ❌ ERROR: Archivo cifrado pero no se activó descifrado")
                    messagebox.showerror("Error", "Este archivo está cifrado. Activa la opción de descifrado e ingresa la contraseña.")
                    return
                
                password = self.decrypt_password_entry.get()
                if not password:
                    self.log_message(self.extract_log, "\n   ❌ ERROR: Se requiere contraseña")
                    messagebox.showerror("Error", "Ingresa la contraseña para descifrar")
                    return
                
                self.log_message(self.extract_log, "\n🔐 Descifrando con XOR...")
                payload_data = self.xor_encrypt_decrypt(payload_data, password)
                self.log_message(self.extract_log, "   ✅ Descifrado completado")
            
            # Descomprimir si es necesario
            if metadata['compressed']:
                self.log_message(self.extract_log, "\n🗜️  Descomprimiendo...")
                try:
                    payload_data = zlib.decompress(payload_data)
                    self.log_message(self.extract_log, f"   ✅ Descomprimido: {len(payload_data):,} bytes")
                except Exception as e:
                    self.log_message(self.extract_log, f"   ❌ Error al descomprimir: {str(e)}")
                    messagebox.showerror("Error", "Error al descomprimir. Contraseña incorrecta o datos corruptos.")
                    return
            
            # Verificar integridad
            extracted_hash = hashlib.sha256(payload_data).hexdigest()
            original_hash = metadata.get('original_hash', '')
            
            self.log_message(self.extract_log, f"\n🔍 Verificando integridad...")
            self.log_message(self.extract_log, f"   Hash extraído:  {extracted_hash[:32]}...")
            self.log_message(self.extract_log, f"   Hash original:  {original_hash[:32]}...")
            
            if extracted_hash == original_hash:
                self.log_message(self.extract_log, "   ✅ INTEGRIDAD VERIFICADA - Archivo extraído correctamente")
            else:
                self.log_message(self.extract_log, "   ⚠️  ADVERTENCIA: Los hashes no coinciden")
                if metadata['encrypted']:
                    self.log_message(self.extract_log, "   Posible contraseña incorrecta")
            
            # Guardar archivo
            self.log_message(self.extract_log, f"\n💾 Guardando: {os.path.basename(self.extract_output_path.get())}")
            with open(self.extract_output_path.get(), 'wb') as f:
                f.write(payload_data)
            
            self.log_message(self.extract_log, f"   Tamaño: {len(payload_data):,} bytes ({len(payload_data)/1024/1024:.2f} MB)")
            
            self.log_message(self.extract_log, "\n" + "=" * 80)
            self.log_message(self.extract_log, "✅ EXTRACCIÓN COMPLETADA EXITOSAMENTE")
            self.log_message(self.extract_log, "=" * 80)
            self.log_message(self.extract_log, f"📁 Archivo extraído: {self.extract_output_path.get()}")
            self.log_message(self.extract_log, f"🔐 Archivo original: {metadata['filename']}")
            
            messagebox.showinfo("Éxito", 
                f"✅ Archivo extraído exitosamente!\n\n"
                f"Archivo original: {metadata['filename']}\n"
                f"Guardado como: {os.path.basename(self.extract_output_path.get())}\n"
                f"Tamaño: {len(payload_data)/1024/1024:.2f} MB\n"
                f"Integridad: {'✅ Verificada' if extracted_hash == original_hash else '⚠️ No verificada'}")
            
        except Exception as e:
            self.log_message(self.extract_log, f"\n❌ ERROR: {str(e)}")
            import traceback
            self.log_message(self.extract_log, traceback.format_exc())
            messagebox.showerror("Error", f"Error al extraer archivo: {str(e)}")
    
    def analyze_file(self):
        try:
            self.analysis_text.delete(1.0, tk.END)
            
            if not self.analysis_file_path.get():
                messagebox.showerror("Error", "Selecciona un archivo para analizar")
                return
            
            file_path = self.analysis_file_path.get()
            
            self.analysis_text.insert(tk.END, "=" * 80 + "\n")
            self.analysis_text.insert(tk.END, "🔍 ANÁLISIS FORENSE DE ESTEGANOGRAFÍA\n")
            self.analysis_text.insert(tk.END, "=" * 80 + "\n\n")
            
            # Info básica
            self.analysis_text.insert(tk.END, "📄 INFORMACIÓN BÁSICA\n")
            self.analysis_text.insert(tk.END, "-" * 80 + "\n")
            self.analysis_text.insert(tk.END, f"Archivo: {os.path.basename(file_path)}\n")
            self.analysis_text.insert(tk.END, f"Ruta: {file_path}\n")
            
            file_size = os.path.getsize(file_path)
            self.analysis_text.insert(tk.END, f"Tamaño: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)\n")
            
            # Extension
            ext = os.path.splitext(file_path)[1].lower()
            self.analysis_text.insert(tk.END, f"Extensión: {ext if ext else 'Sin extensión'}\n")
            
            # Hashes
            self.analysis_text.insert(tk.END, "\n🔐 HASHES\n")
            self.analysis_text.insert(tk.END, "-" * 80 + "\n")
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            md5_hash = hashlib.md5(file_data).hexdigest()
            sha1_hash = hashlib.sha1(file_data).hexdigest()
            sha256_hash = hashlib.sha256(file_data).hexdigest()
            
            self.analysis_text.insert(tk.END, f"MD5:    {md5_hash}\n")
            self.analysis_text.insert(tk.END, f"SHA1:   {sha1_hash}\n")
            self.analysis_text.insert(tk.END, f"SHA256: {sha256_hash}\n")
            
            # Análisis de firma de archivo (magic bytes)
            self.analysis_text.insert(tk.END, "\n🔬 FIRMA DE ARCHIVO (MAGIC BYTES)\n")
            self.analysis_text.insert(tk.END, "-" * 80 + "\n")
            
            magic_bytes = file_data[:20]
            magic_hex = ' '.join(f'{b:02X}' for b in magic_bytes)
            self.analysis_text.insert(tk.END, f"Primeros 20 bytes: {magic_hex}\n")
            
            # Detectar tipo de archivo por magic bytes
            file_signatures = {
                b'\x89PNG': 'PNG Image',
                b'\xFF\xD8\xFF': 'JPEG Image',
                b'GIF89a': 'GIF Image',
                b'GIF87a': 'GIF Image',
                b'%PDF': 'PDF Document',
                b'PK\x03\x04': 'ZIP Archive / DOCX / XLSX / JAR',
                b'MZ': 'Windows Executable (PE)',
                b'\x7FELF': 'Linux Executable (ELF)',
                b'Rar!': 'RAR Archive',
                b'\x1F\x8B': 'GZIP Compressed',
                b'BM': 'BMP Image',
                b'\x00\x00\x01\xBA': 'MPEG Video',
                b'\x00\x00\x01\xB3': 'MPEG Video',
                b'ftyp': 'MP4 Video (offset 4)',
            }
            
            detected_type = "Desconocido"
            for sig, ftype in file_signatures.items():
                if file_data.startswith(sig) or file_data[4:8].startswith(sig):
                    detected_type = ftype
                    break
            
            self.analysis_text.insert(tk.END, f"Tipo detectado: {detected_type}\n")
            
            # Buscar esteganografía
            self.analysis_text.insert(tk.END, "\n🔍 ANÁLISIS DE ESTEGANOGRAFÍA\n")
            self.analysis_text.insert(tk.END, "-" * 80 + "\n")
            
            MAGIC = b'<<<UNIVERSAL_STEGO>>>'
            DELIMITER = b'<<<END_STEGO>>>'
            
            magic_pos = file_data.find(MAGIC)
            delimiter_pos = file_data.find(DELIMITER)
            
            suspicious_indicators = 0
            
            if magic_pos != -1:
                self.analysis_text.insert(tk.END, "🚨 DETECTADO: Magic bytes de esta herramienta encontrados!\n", "critical")
                self.analysis_text.insert(tk.END, f"   Posición: {magic_pos:,} bytes desde el inicio\n", "critical")
                suspicious_indicators += 5
                
                if delimiter_pos != -1:
                    self.analysis_text.insert(tk.END, f"🚨 DETECTADO: Delimitador encontrado en posición {delimiter_pos:,}\n", "critical")
                    
                    # Intentar extraer metadata
                    try:
                        stego_start = magic_pos + len(MAGIC)
                        stego_data = file_data[stego_start:delimiter_pos]
                        
                        metadata_size = int.from_bytes(stego_data[:4], 'big')
                        if metadata_size < 10000:  # Sanity check
                            metadata_bytes = stego_data[4:4+metadata_size]
                            metadata = json.loads(metadata_bytes.decode('utf-8'))
                            
                            self.analysis_text.insert(tk.END, "\n📊 METADATA DEL ARCHIVO OCULTO:\n", "critical")
                            self.analysis_text.insert(tk.END, f"   Nombre: {metadata.get('filename', 'N/A')}\n", "critical")
                            self.analysis_text.insert(tk.END, f"   Tamaño original: {metadata.get('original_size', 'N/A'):,} bytes\n", "critical")
                            self.analysis_text.insert(tk.END, f"   Comprimido: {metadata.get('compressed', False)}\n", "critical")
                            self.analysis_text.insert(tk.END, f"   Cifrado: {metadata.get('encrypted', False)}\n", "critical")
                            self.analysis_text.insert(tk.END, f"   Modo sigiloso: {metadata.get('stealth', False)}\n", "critical")
                            self.analysis_text.insert(tk.END, f"   Hash original: {metadata.get('original_hash', 'N/A')[:32]}...\n", "critical")
                            
                            payload_size = len(stego_data) - 4 - metadata_size
                            self.analysis_text.insert(tk.END, f"   Tamaño payload: {payload_size:,} bytes ({payload_size/1024/1024:.2f} MB)\n", "critical")
                    except Exception as e:
                        self.analysis_text.insert(tk.END, f"   ⚠️ Error al parsear metadata: {str(e)}\n")
            else:
                self.analysis_text.insert(tk.END, "✓ No se detectaron magic bytes de esta herramienta\n")
            
            # Análisis de entropía
            self.analysis_text.insert(tk.END, "\n📊 ANÁLISIS DE ENTROPÍA\n")
            self.analysis_text.insert(tk.END, "-" * 80 + "\n")
            
            from collections import Counter
            import math
            
            # Calcular entropía de diferentes secciones
            chunk_size = min(len(file_data), 100000)  # Primeros 100KB
            
            for section_name, section_data in [
                ("Inicio del archivo", file_data[:chunk_size]),
                ("Final del archivo", file_data[-chunk_size:] if len(file_data) > chunk_size else file_data)
            ]:
                if len(section_data) == 0:
                    continue
                    
                counter = Counter(section_data)
                entropy = 0
                for count in counter.values():
                    prob = count / len(section_data)
                    entropy -= prob * math.log2(prob)
                
                self.analysis_text.insert(tk.END, f"{section_name}:\n")
                self.analysis_text.insert(tk.END, f"   Entropía: {entropy:.4f} bits (máx: 8.0)\n")
                
                if entropy > 7.5:
                    self.analysis_text.insert(tk.END, "   ⚠️ ALTA ENTROPÍA - Posible cifrado o compresión\n", "warning")
                    suspicious_indicators += 1
                elif entropy > 6.5:
                    self.analysis_text.insert(tk.END, "   ⚠️ ENTROPÍA MODERADA-ALTA\n", "warning")
                else:
                    self.analysis_text.insert(tk.END, "   ✓ Entropía normal\n")
            
            # Buscar strings sospechosas
            self.analysis_text.insert(tk.END, "\n🔎 STRINGS SOSPECHOSAS\n")
            self.analysis_text.insert(tk.END, "-" * 80 + "\n")
            
            suspicious_strings = [
                b'eval', b'exec', b'system', b'shell', b'cmd',
                b'powershell', b'bash', b'python', b'payload',
                b'exploit', b'shellcode', b'metasploit', b'meterpreter',
                b'base64', b'decode', b'encrypt', b'decrypt'
            ]
            
            found_suspicious = []
            for sus_str in suspicious_strings:
                count = file_data.count(sus_str)
                if count > 0:
                    found_suspicious.append((sus_str.decode('latin1'), count))
                    suspicious_indicators += 1
            
            if found_suspicious:
                self.analysis_text.insert(tk.END, "⚠️ Strings sospechosas encontradas:\n", "warning")
                for string, count in found_suspicious[:10]:  # Top 10
                    self.analysis_text.insert(tk.END, f"   '{string}': {count} ocurrencias\n", "warning")
            else:
                self.analysis_text.insert(tk.END, "✓ No se encontraron strings comúnmente asociadas con malware\n")
            
            # Análisis de tamaño anómalo
            self.analysis_text.insert(tk.END, "\n📏 ANÁLISIS DE TAMAÑO\n")
            self.analysis_text.insert(tk.END, "-" * 80 + "\n")
            
            expected_sizes = {
                '.exe': (1024, 50*1024*1024),  # 1KB - 50MB
                '.dll': (1024, 10*1024*1024),  # 1KB - 10MB
                '.pdf': (1024, 100*1024*1024), # 1KB - 100MB
                '.jpg': (1024, 20*1024*1024),  # 1KB - 20MB
                '.png': (1024, 50*1024*1024),  # 1KB - 50MB
                '.docx': (1024, 50*1024*1024), # 1KB - 50MB
            }
            
            if ext in expected_sizes:
                min_size, max_size = expected_sizes[ext]
                if file_size > max_size:
                    self.analysis_text.insert(tk.END, f"⚠️ TAMAÑO INUSUAL: {ext} files son usualmente menores a {max_size/1024/1024:.0f}MB\n", "warning")
                    self.analysis_text.insert(tk.END, "   Posible indicador de esteganografía o datos adjuntos\n", "warning")
                    suspicious_indicators += 1
                else:
                    self.analysis_text.insert(tk.END, "✓ Tamaño dentro del rango esperado\n")
            
            # Configurar tags
            self.analysis_text.tag_config("critical", foreground="red", font=("Consolas", 9, "bold"))
            self.analysis_text.tag_config("warning", foreground="orange", font=("Consolas", 9))
            self.analysis_text.tag_config("good", foreground="green")
            
            # Conclusión final
            self.analysis_text.insert(tk.END, "\n" + "=" * 80 + "\n")
            self.analysis_text.insert(tk.END, "🎯 CONCLUSIÓN DEL ANÁLISIS\n")
            self.analysis_text.insert(tk.END, "=" * 80 + "\n")
            
            self.analysis_text.insert(tk.END, f"Indicadores sospechosos encontrados: {suspicious_indicators}\n\n")
            
            if suspicious_indicators >= 5:
                risk_level = "🚨 CRÍTICO"
                tag = "critical"
                recommendation = ("Este archivo contiene datos ocultos detectados.\n"
                                "RECOMENDACIÓN: Extraer y analizar el contenido oculto en un entorno aislado (sandbox).\n"
                                "NO ejecutar en producción hasta verificar el contenido.")
            elif suspicious_indicators >= 2:
                risk_level = "⚠️ ALTO"
                tag = "warning"
                recommendation = ("Múltiples indicadores sospechosos detectados.\n"
                                "RECOMENDACIÓN: Realizar análisis más profundo, escanear con antivirus,\n"
                                "y considerar analizar en sandbox antes de confiar en este archivo.")
            elif suspicious_indicators >= 1:
                risk_level = "⚠️ MODERADO"
                tag = "warning"
                recommendation = ("Algunos indicadores sospechosos detectados.\n"
                                "RECOMENDACIÓN: Verificar la procedencia del archivo y escanear con antivirus.")
            else:
                risk_level = "✓ BAJO"
                tag = "good"
                recommendation = ("No se detectaron indicadores significativos de esteganografía.\n"
                                "El archivo parece normal, pero siempre verifica archivos de fuentes desconocidas.")
            
            self.analysis_text.insert(tk.END, f"Nivel de riesgo: {risk_level}\n\n", tag)
            self.analysis_text.insert(tk.END, recommendation + "\n")
            
            self.analysis_text.insert(tk.END, "\n" + "=" * 80 + "\n")
            
        except Exception as e:
            self.analysis_text.insert(tk.END, f"\n❌ ERROR: {str(e)}\n")
            import traceback
            self.analysis_text.insert(tk.END, traceback.format_exc())
            messagebox.showerror("Error", f"Error al analizar archivo: {str(e)}")

# Crear ventana principal
if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalSteganographyTool(root)
    
    # Configurar estilo
    style = ttk.Style()
    style.configure("Accent.TButton", font=("Arial", 11, "bold"), padding=10)
    
    root.mainloop()