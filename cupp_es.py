#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CUPP-Español (Common User Passwords Profiler)
Generador de diccionarios de contraseñas personalizadas para pentesting
Adaptación hispana basada en CUPP v3.3.0 de Mebus
"""

import argparse
import sys
import os
import itertools
import re
from datetime import datetime

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║     ██████╗██╗   ██╗██████╗ ██████╗     ███████╗           ║
║    ██╔════╝██║   ██║██╔══██╗██╔══██╗    ██╔════╝           ║
║    ██║     ██║   ██║██████╔╝██████╔╝    ███████╗           ║
║    ██║     ██║   ██║██╔═══╝ ██╔═══╝     ╚════██║           ║
║    ╚██████╗╚██████╔╝██║     ██║         ███████║           ║
║     ╚═════╝ ╚═════╝ ╚═╝     ╚═╝         ╚══════╝           ║
║                                                              ║
║     Common User Passwords Profiler - Versión Española        ║
║     v3.3.0-es | Para pruebas de penetración autorizadas    ║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}
    """
    print(banner)

def leet_transform(word):
    """Transforma palabras al modo leet (1337) - Igual que CUPP original"""
    leet_map = {
        'a': ['4', '@'],
        'e': ['3'],
        'i': ['1', '!'],
        'o': ['0'],
        's': ['5', '$'],
        't': ['7'],
        'g': ['9'],
        'b': ['8', '13'],
        'z': ['2'],
        'l': ['1'],
        'q': ['9']
    }
    
    variations = [word]
    for char, replacements in leet_map.items():
        new_variations = []
        for variation in variations:
            if char in variation.lower():
                for replacement in replacements:
                    new_var = variation.replace(char, replacement)
                    new_var = new_var.replace(char.upper(), replacement)
                    new_variations.append(new_var)
        variations.extend(new_variations)
    return list(set(variations))

def generate_years():
    """Genera años relevantes (actual +- 50 años)"""
    current_year = datetime.now().year
    years = []
    for year in range(current_year - 50, current_year + 1):
        years.append(str(year))
        years.append(str(year)[-2:])  # Solo últimos 2 dígitos
    return years

def generate_numbers():
    """Genera números comunes para contraseñas"""
    numbers = []
    # Números del 0 al 100
    for i in range(0, 101):
        numbers.append(str(i))
        numbers.append(f"{i:02d}")  # Con padding
    # Años de nacimiento comunes
    numbers.extend(generate_years())
    # Números especiales
    special_nums = ['123', '1234', '12345', '123456', '007', '666', '777', '888', '999', '000', '111', '222', '333', '444', '555', '321', '654']
    numbers.extend(special_nums)
    return list(set(numbers))

def get_common_spanish_words():
    """Palabras comunes en contraseñas de hispanohablantes"""
    return [
        'amor', 'amorcito', 'corazon', 'cielo', 'vida', 'familia', 'casa',
        'dinero', 'trabajo', 'escuela', 'universidad', 'carrera', 'meta',
        'futbol', 'messi', 'cr7', 'barcelona', 'madrid', 'america', 'chivas',
        'mexico', 'argentina', 'colombia', 'chile', 'peru', 'venezuela', 'españa',
        'password', 'clave', 'contraseña', 'admin', 'usuario', 'root',
        'estrella', 'luna', 'sol', 'mar', 'tierra', 'cielo', 'fuego',
        'carro', 'moto', 'casa', 'perro', 'gato', 'conejo', 'pez',
        'novia', 'novio', 'esposa', 'esposo', 'mama', 'papa', 'hijo', 'hija',
        'princesa', 'principe', 'rey', 'reina', 'angel', 'demonio',
        'tequiero', 'teamo', 'feliz', 'suerte', 'libre', 'fuerte', 'guapo', 'bella',
        'secreto', 'esperanza', 'sueño', 'estudio', 'exito', 'fuerza', 'paz'
    ]

def generate_combinations(base_words, numbers, special_chars, use_leet=False):
    """Genera todas las combinaciones posibles - Lógica mejorada de CUPP"""
    passwords = set()
    
    # Palabras base con variaciones de caso
    for word in base_words:
        if len(word) >= 2:
            passwords.add(word.lower())
            passwords.add(word.capitalize())
            passwords.add(word.upper())
    
    # Combinaciones con números (al final y al principio)
    base_list = list(passwords)
    for word in base_list:
        for num in numbers[:50]:  # Limitar para rendimiento
            passwords.add(f"{word}{num}")
            passwords.add(f"{num}{word}")
    
    # Combinaciones con caracteres especiales
    if special_chars:
        current_list = list(passwords)
        for word in current_list:
            for char in special_chars:
                passwords.add(f"{word}{char}")
                passwords.add(f"{char}{word}")
    
    # Modo leet
    if use_leet:
        leet_words = []
        for word in base_words:
            leet_words.extend(leet_transform(word))
        for word in leet_words:
            if len(word) >= 2:
                passwords.add(word)
                # Combinaciones leet + números
                for num in numbers[:20]:
                    passwords.add(f"{word}{num}")
    
    return list(passwords)

def interactive_mode():
    """Modo interactivo - Estructura fiel a CUPP original pero en español"""
    print(f"\n{Colors.GREEN}[+] Modo Interactivo de CUPP-Español{Colors.ENDC}")
    print(f"{Colors.WARNING}[!] Introduce la información conocida sobre el objetivo para generar un diccionario personalizado{Colors.ENDC}")
    print(f"{Colors.WARNING}[!] Si no conoces algún dato, solo presiona ENTER para omitir{Colors.ENDC}\n")
    
    # Información personal básica
    print(f"{Colors.CYAN}--- Información Personal ---{Colors.ENDC}")
    nombre = input("> Nombre(s): ").strip()
    apellido = input("> Apellido(s): ").strip()
    apodo = input("> Apodo/Alias: ").strip()
    
    # Fecha de nacimiento
    fecha_nac = input("> Fecha de nacimiento (DDMMYYYY): ").strip()
    while fecha_nac and not re.match(r'^\d{8}$', fecha_nac):
        print(f"{Colors.WARNING}[!] Formato inválido. Usa DDMMYYYY (ejemplo: 15051990){Colors.ENDC}")
        fecha_nac = input("> Fecha de nacimiento (DDMMYYYY): ").strip()
    
    # Información de pareja
    print(f"\n{Colors.CYAN}--- Información de Pareja ---{Colors.ENDC}")
    pareja_nombre = input("> Nombre de la pareja: ").strip()
    pareja_apodo = input("> Apodo de la pareja: ").strip()
    pareja_fecha = input("> Fecha de nacimiento de la pareja (DDMMYYYY): ").strip()
    while pareja_fecha and not re.match(r'^\d{8}$', pareja_fecha):
        print(f"{Colors.WARNING}[!] Formato inválido. Usa DDMMYYYY{Colors.ENDC}")
        pareja_fecha = input("> Fecha de nacimiento de la pareja (DDMMYYYY): ").strip()
    
    # Información de hijos
    print(f"\n{Colors.CYAN}--- Información de Hijos ---{Colors.ENDC}")
    hijo_nombre = input("> Nombre del hijo(a): ").strip()
    hijo_apodo = input("> Apodo del hijo(a): ").strip()
    hijo_fecha = input("> Fecha de nacimiento del hijo(a) (DDMMYYYY): ").strip()
    while hijo_fecha and not re.match(r'^\d{8}$', hijo_fecha):
        print(f"{Colors.WARNING}[!] Formato inválido. Usa DDMMYYYY{Colors.ENDC}")
        hijo_fecha = input("> Fecha de nacimiento del hijo(a) (DDMMYYYY): ").strip()
    
    # Mascota
    mascota = input("> Nombre de la mascota: ").strip()
    
    # Información laboral y educativa
    print(f"\n{Colors.CYAN}--- Información Laboral/Educativa ---{Colors.ENDC}")
    empresa = input("> Nombre de la empresa: ").strip()
    escuela = input("> Nombre de la escuela/universidad: ").strip()
    cargo = input("> Cargo o puesto: ").strip()
    carrera = input("> Carrera o especialidad: ").strip()
    
    # Preferencias personales
    print(f"\n{Colors.CYAN}--- Preferencias Personales ---{Colors.ENDC}")
    equipo = input("> Equipo de fútbol favorito: ").strip()
    otros = input("> Otras palabras clave (hobbies, lugares, etc. separadas por coma): ").strip()
    
    # Opciones de generación
    print(f"\n{Colors.CYAN}--- Opciones de Generación ---{Colors.ENDC}")
    usar_leet = input("> ¿Agregar variaciones Leet (1337)? [s/N]: ").lower().startswith('s')
    usar_especiales = input("> ¿Agregar caracteres especiales? [s/N]: ").lower().startswith('s')
    
    # Construir lista de palabras base (lógica mejorada de CUPP)
    base_words = []
    
    # Función auxiliar para agregar variaciones
    def add_variations(text):
        if not text:
            return
        base_words.append(text)
        base_words.append(text.lower())
        base_words.append(text.upper())
        base_words.append(text.capitalize())
        # Sin espacios
        base_words.append(text.replace(" ", ""))
        base_words.append(text.replace(" ", "").lower())
    
    # Agregar datos personales con variaciones
    add_variations(nombre)
    add_variations(apellido)
    add_variations(apodo)
    
    # Combinaciones de nombre y apellido
    if nombre and apellido:
        base_words.append(f"{nombre}{apellido}")
        base_words.append(f"{nombre.lower()}{apellido.lower()}")
        base_words.append(f"{nombre[0]}{apellido}")
        base_words.append(f"{nombre[0].lower()}{apellido.lower()}")
        base_words.append(f"{apellido}{nombre}")
        base_words.append(f"{apellido.lower()}{nombre.lower()}")
    
    # Procesar fechas (múltiples formatos)
    fechas = [fecha_nac, pareja_fecha, hijo_fecha]
    for fecha in fechas:
        if fecha and len(fecha) == 8:
            # DDMMAAAA
            base_words.append(fecha)
            base_words.append(fecha[:4])  # DDMM
            base_words.append(fecha[4:])  # AAAA
            base_words.append(fecha[-2:])  # AA
            # Separadores
            base_words.append(f"{fecha[:2]}{fecha[2:4]}{fecha[4:]}")
            base_words.append(f"{fecha[:2]}-{fecha[2:4]}-{fecha[4:]}")
            base_words.append(f"{fecha[:2]}/{fecha[2:4]}/{fecha[4:]}")
    
    # Agregar datos de pareja
    add_variations(pareja_nombre)
    add_variations(pareja_apodo)
    
    # Agregar datos de hijos
    add_variations(hijo_nombre)
    add_variations(hijo_apodo)
    
    # Agregar mascota
    add_variations(mascota)
    
    # Agregar datos laborales/educativos
    add_variations(empresa)
    add_variations(escuela)
    add_variations(cargo)
    add_variations(carrera)
    add_variations(equipo)
    
    # Procesar palabras adicionales
    if otros:
        for palabra in otros.split(','):
            p = palabra.strip()
            if p:
                add_variations(p)
    
    # Agregar palabras comunes en español
    base_words.extend(get_common_spanish_words())
    
    # Caracteres especiales
    special_chars = ['!', '@', '#', '$', '%', '&', '*', '?', '¡', '¿', '+', '-', '_', '.']
    if not usar_especiales:
        special_chars = []
    
    # Generar números
    numbers = generate_numbers()
    
    # Generar contraseñas
    print(f"\n{Colors.GREEN}[+] Generando diccionario de contraseñas...{Colors.ENDC}")
    print(f"{Colors.CYAN}[i] Esto puede tomar unos segundos...{Colors.ENDC}")
    
    passwords = generate_combinations(base_words, numbers, special_chars, usar_leet)
    
    # Filtrar por longitud razonable (igual que CUPP original: 6-12 caracteres)
    passwords = [pwd for pwd in passwords if 6 <= len(pwd) <= 12]
    
    # Eliminar duplicados y ordenar
    passwords = sorted(set(passwords))
    
    # Guardar archivo
    filename = f"{nombre.lower() if nombre else 'wordlist'}_cupp.txt"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for pwd in passwords:
                f.write(pwd + '\n')
        
        print(f"\n{Colors.GREEN}[+] ¡Diccionario generado exitosamente!{Colors.ENDC}")
        print(f"{Colors.CYAN}[+] Archivo guardado: {filename}{Colors.ENDC}")
        print(f"{Colors.CYAN}[+] Total de contraseñas generadas: {len(passwords)}{Colors.ENDC}")
        print(f"{Colors.WARNING}[!] Recuerda: Usa esta herramienta solo para pruebas de penetración autorizadas{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.FAIL}[!] Error al guardar el archivo: {e}{Colors.ENDC}")
        sys.exit(1)

def download_common_wordlist():
    """Descarga listas de palabras comunes (funcionalidad añadida)"""
    print(f"\n{Colors.GREEN}[+] Descargando listas de palabras comunes...{Colors.ENDC}")
    # Aquí podrías implementar descarga de listas como rockyou.txt adaptadas
    print(f"{Colors.WARNING}[i] Función en desarrollo - Usa listas como rockyou.txt manualmente{Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(
        description='CUPP-Español: Common User Passwords Profiler - Generador de diccionarios personalizados',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python3 cupp_es.py -i              # Modo interactivo (recomendado)
  python3 cupp_es.py --help            # Mostrar esta ayuda
  python3 cupp_es.py -v                # Mostrar versión

CUPP-Español genera diccionarios de contraseñas basados en información 
personal. Úsalo solo para pruebas de seguridad autorizadas.
        """
    )
    
    parser.add_argument('-i', '--interactive', action='store_true',
                      help='Iniciar modo interactivo para perfilado de contraseñas')
    parser.add_argument('-v', '--version', action='store_true',
                      help='Mostrar versión del programa')
    parser.add_argument('-q', '--quiet', action='store_true',
                      help='Modo silencioso (sin banner)')
    parser.add_argument('-w', '--wordlist', action='store_true',
                      help='Descargar listas de palabras comunes')
    
    args = parser.parse_args()
    
    if args.version:
        print("CUPP-Español v3.3.0-es (Common User Passwords Profiler)")
        print("Adaptación hispana basada en CUPP de Mebus")
        print("Para pruebas de penetración autorizadas únicamente")
        sys.exit(0)
    
    if not args.quiet:
        print_banner()
    
    if args.wordlist:
        download_common_wordlist()
        sys.exit(0)
    
    if args.interactive:
        interactive_mode()
    else:
        parser.print_help()
        print(f"\n{Colors.WARNING}[!] Tip: Usa -i para iniciar el modo interactivo{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.FAIL}[!] Interrumpido por el usuario{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}[!] Error inesperado: {e}{Colors.ENDC}")
        sys.exit(1)