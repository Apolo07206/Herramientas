#!/usr/bin/env python3
"""
Simple Nmap Scanner - Enumeración Efectiva
Versión simplificada con los modos más útiles
"""

import subprocess
import sys
import os
import time
from datetime import datetime

# Colores
G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[97m'
D = '\033[90m'
E = '\033[0m'

def banner():
    print(f"""{C}
    ╔═══════════════════════════════════════╗
    ║     NMAP SCANNER - Simple & Efectivo  ║
    ║          Enumeración Profesional      ║
    ╚═══════════════════════════════════════╝{E}
""")

def verificar_nmap():
    """Verifica si nmap está instalado"""
    try:
        subprocess.run(["nmap", "--version"], capture_output=True, check=True)
        return True
    except:
        return False

def es_root():
    """Verifica privilegios de root"""
    return os.geteuid() == 0

def menu():
    """Menú simplificado con los escaneos más útiles"""
    print(f"\n{C}┌─[ MODOS DE ESCANEO ]─────────────────────────────────────┐{E}\n")
    
    print(f"  {G}[1] Rápido{E}          → Puertos comunes + versiones (5 min)")
    print(f"  {G}[2] Completo{E}        → Todos los puertos + enum básica (15-30 min)")
    print(f"  {Y}[3] Profesional{E}     → Enum completa + scripts + OS (30-60 min)")
    print(f"  {R}[4] Vulnerabilidades{E} → Detección de vulns conocidas (20-40 min)")
    
    if es_root():
        print(f"  {C}[5] Sigiloso{E}        → Modo stealth SYN (lento, 30+ min)")
    
    print(f"\n{C}└──────────────────────────────────────────────────────────┘{E}")

def obtener_comando(modo, target, output_file=None):
    """Retorna el comando de nmap según el modo"""
    
    # Construir comando base sin archivo de salida
    comandos_base = {
        "1": {
            "cmd": [
                "nmap", "-T4", "-F",           # Fast scan, top 100 puertos
                "-sV",                          # Detección de versiones
                "--version-intensity", "5",     # Intensidad media
                "-sC",                          # Scripts default
                "-Pn",                          # Sin ping
                "--open",                       # Solo puertos abiertos
            ],
            "desc": "Escaneo Rápido",
            "tiempo": "~5 minutos",
            "info": "Top 100 puertos + detección de versiones + scripts básicos"
        },
        
        "2": {
            "cmd": [
                "nmap", "-T4", "-p-",          # Todos los puertos
                "-sV",                          # Versiones
                "--version-intensity", "7",     # Intensidad alta
                "-sC",                          # Scripts default
                "-Pn", "--open",
                "--min-rate", "1000",           # Velocidad mínima
            ],
            "desc": "Escaneo Completo",
            "tiempo": "~15-30 minutos",
            "info": "Todos los puertos (65535) + versiones + scripts"
        },
        
        "3": {
            "cmd": [
                "nmap", "-T4", "-p-",          # Todos los puertos
                "-sV", "--version-all",         # Máxima detección versiones
                "-sC",                          # Scripts default
                "-O", "--osscan-guess",         # Detección de OS
                "-A",                           # Modo agresivo
                "--script", "default,discovery,safe", # Scripts seguros
                "-Pn", "--open",
            ],
            "desc": "Escaneo Profesional",
            "tiempo": "~30-60 minutos",
            "info": "Enumeración completa + OS + traceroute + scripts avanzados"
        },
        
        "4": {
            "cmd": [
                "nmap", "-T4",
                "-sV", "--version-intensity", "9",
                "--script", "vuln,vulners",     # Scripts de vulnerabilidades
                "-Pn", "--open",
            ],
            "desc": "Detección de Vulnerabilidades",
            "tiempo": "~20-40 minutos",
            "info": "Búsqueda de vulnerabilidades conocidas (CVEs)"
        },
        
        "5": {
            "cmd": [
                "nmap", "-sS",                 # SYN scan (requiere root)
                "-T2",                          # Timing lento
                "-p-",
                "-sV", "--version-intensity", "7",
                "-sC",
                "-Pn", "--open",
                "--scan-delay", "500ms",        # Delay entre paquetes
            ],
            "desc": "Escaneo Sigiloso",
            "tiempo": "~30+ minutos",
            "info": "Modo stealth para evadir detección (requiere root)"
        }
    }
    
    info = comandos_base.get(modo)
    if not info:
        return None
    
    # Agregar archivo de salida si se especificó
    cmd = info['cmd'].copy()
    if output_file:
        cmd.extend(["-oN", output_file])
    cmd.append(target)
    
    info['cmd'] = cmd
    return info

def mostrar_info(target, info, guardar, output=None):
    """Muestra información del escaneo"""
    print(f"\n{C}┌─[ INFORMACIÓN DEL ESCANEO ]──────────────────────────────┐{E}")
    print(f"  {Y}Objetivo:{E}     {G}{target}{E}")
    print(f"  {Y}Modo:{E}         {G}{info['desc']}{E}")
    print(f"  {Y}Descripción:{E}  {W}{info['info']}{E}")
    print(f"  {Y}Tiempo est.:{E}  {W}{info['tiempo']}{E}")
    if guardar and output:
        print(f"  {Y}Salida:{E}       {G}{output}{E}")
    else:
        print(f"  {Y}Salida:{E}       {D}No se guardará{E}")
    print(f"{C}└──────────────────────────────────────────────────────────┘{E}")
    
    print(f"\n{D}Comando:{E} {' '.join(info['cmd'])}\n")

def ejecutar_escaneo(cmd):
    """Ejecuta el escaneo y muestra progreso"""
    print(f"\n{G}┌─[ ESCANEO INICIADO ]─────────────────────────────────────┐{E}")
    print(f"  {D}Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{E}")
    print(f"{G}└──────────────────────────────────────────────────────────┘{E}\n")
    
    print(f"{Y}Ejecutando nmap... (Presiona Ctrl+C para cancelar){E}\n")
    print(f"{C}{'─'*60}{E}\n")
    
    inicio = time.time()
    
    try:
        # Ejecutar nmap y mostrar salida en tiempo real
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Mostrar salida línea por línea
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        fin = time.time()
        duracion = fin - inicio
        
        print(f"\n{C}{'─'*60}{E}")
        
        if process.returncode == 0:
            print(f"\n{G}┌─[ COMPLETADO EXITOSAMENTE ]──────────────────────────────┐{E}")
            print(f"  {D}Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{E}")
            print(f"  {D}Duración: {int(duracion//60)}m {int(duracion%60)}s{E}")
            print(f"{G}└──────────────────────────────────────────────────────────┘{E}\n")
        else:
            print(f"\n{Y}[!] Escaneo finalizado con código: {process.returncode}{E}\n")
            
    except KeyboardInterrupt:
        print(f"\n\n{R}[!] Escaneo interrumpido por el usuario{E}\n")
        process.kill()
    except Exception as e:
        print(f"\n{R}[✗] Error: {e}{E}\n")

def main():
    banner()
    
    # Verificar nmap
    if not verificar_nmap():
        print(f"{R}[✗] Nmap no está instalado{E}")
        print(f"{D}    Ejecuta: sudo apt install nmap{E}\n")
        sys.exit(1)
    
    print(f"{G}[✓] Nmap detectado{E}")
    
    # Verificar privilegios
    if es_root():
        print(f"{G}[✓] Ejecutando como root (todas las opciones disponibles){E}")
    else:
        print(f"{Y}[!] Modo usuario (opción [5] requiere root){E}")
    
    # Mostrar menú
    menu()
    
    # Obtener modo
    modo = input(f"\n{C}Selecciona modo [1-{'5' if es_root() else '4'}]: {E}").strip()
    
    if modo not in ["1", "2", "3", "4"] and not (es_root() and modo == "5"):
        print(f"\n{R}[✗] Opción inválida{E}\n")
        sys.exit(1)
    
    # Si es modo 5 sin root
    if modo == "5" and not es_root():
        print(f"\n{R}[✗] El modo sigiloso requiere privilegios de root{E}")
        print(f"{D}    Ejecuta: sudo python3 {sys.argv[0]}{E}\n")
        sys.exit(1)
    
    # Obtener objetivo
    print(f"\n{C}{'─'*60}{E}")
    target = input(f"{C}Objetivo (IP/dominio/rango): {E}").strip()
    
    if not target:
        print(f"\n{R}[✗] Debes especificar un objetivo{E}\n")
        sys.exit(1)
    
    # Preguntar si quiere guardar resultados
    print(f"\n{C}{'─'*60}{E}")
    guardar = input(f"{C}¿Guardar resultados? (s/n): {E}").strip().lower()
    
    output_file = None
    if guardar == 's':
        # Sugerir nombre por defecto
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_sugerido = f"scan_{target.replace('.', '_').replace('/', '_')}_{timestamp}.txt"
        
        print(f"\n{D}Nombre sugerido: {nombre_sugerido}{E}")
        nombre = input(f"{C}Nombre del archivo (Enter para usar sugerido): {E}").strip()
        
        if not nombre:
            output_file = nombre_sugerido
        else:
            # Agregar .txt si no tiene extensión
            if not nombre.endswith('.txt'):
                nombre += '.txt'
            output_file = nombre
        
        print(f"{G}[✓] Se guardará en: {output_file}{E}")
    else:
        print(f"{D}[!] Los resultados no se guardarán{E}")
    
    # Obtener comando
    info = obtener_comando(modo, target, output_file)
    if not info:
        print(f"\n{R}[✗] Error al generar comando{E}\n")
        sys.exit(1)
    
    # Mostrar información
    mostrar_info(target, info, guardar == 's', output_file)
    
    # Confirmar
    confirmar = input(f"{Y}¿Iniciar escaneo? (s/n): {E}").strip().lower()
    
    if confirmar != 's':
        print(f"\n{R}[!] Escaneo cancelado{E}\n")
        sys.exit(0)
    
    # Ejecutar
    ejecutar_escaneo(info['cmd'])

if __name__ == "__main__":
    try:
        if os.name != 'posix':
            print(f"{R}[!] Este script requiere Linux/Unix{E}\n")
            sys.exit(1)
        
        main()
        
    except KeyboardInterrupt:
        print(f"\n{R}[!] Programa interrumpido{E}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{R}[✗] Error fatal: {e}{E}\n")
        sys.exit(1)