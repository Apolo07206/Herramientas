#!/usr/bin/env python3
"""
Web Enumeration Tool - FIXED & OPTIMIZED
Autor: Ferxxo (Arreglado y optimizado)
"""

import subprocess as sp
import os
import sys
import re
from pathlib import Path
from collections import defaultdict

class C:
    R = '\033[91m'
    G = '\033[92m'
    Y = '\033[93m'
    B = '\033[94m'
    C = '\033[96m'
    M = '\033[95m'
    W = '\033[97m'
    D = '\033[90m'
    E = '\033[0m'
    BOLD = '\033[1m'

def banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"""
{C.R}{'═'*75}
{C.R}  ██╗    ██╗███████╗██████╗     ███████╗███╗   ██╗██╗   ██╗███╗   ███╗
  ██║    ██║██╔════╝██╔══██╗    ██╔════╝████╗  ██║██║   ██║████╗ ████║
  ██║ █╗ ██║█████╗  ██████╔╝    █████╗  ██╔██╗ ██║██║   ██║██╔████╔██║
  ██║███╗██║██╔══╝  ██╔══██╗    ██╔══╝  ██║╚██╗██║██║   ██║██║╚██╔╝██║
  ╚███╔███╔╝███████╗██████╔╝    ███████╗██║ ╚████║╚██████╔╝██║ ╚═╝ ██║
   ╚══╝╚══╝ ╚══════╝╚═════╝     ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝
{C.R}{'═'*75}
{C.C}  🔍 Web Directory Scanner | {C.Y}FIXED & WORKING VERSION
{C.D}  Enumeración rápida y efectiva con salida en tiempo real{C.E}
{C.R}{'═'*75}{C.E}
""")

def check_tool(tool):
    """Verifica si una herramienta está instalada"""
    try:
        sp.run(['which', tool], capture_output=True, check=True, timeout=3)
        return True
    except:
        return False

def get_wordlists(mode):
    """Obtiene wordlists según el modo"""
    all_paths = [
        "/usr/share/wordlists/dirb/common.txt",
        "/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt",
        "/usr/share/seclists/Discovery/Web-Content/common.txt",
        "/usr/share/seclists/Discovery/Web-Content/raft-small-words.txt",
        "/usr/share/wordlists/dirb/big.txt",
    ]
    
    available = [p for p in all_paths if os.path.exists(p)]
    
    if not available:
        return None
    
    if mode == 'rapido':
        return available[:1]
    elif mode == 'medio':
        return available[:2]
    else:  # supremo
        return available[:3]

def normalize_url(url):
    """Normaliza la URL"""
    url = url.strip()
    
    if url.startswith('http://') or url.startswith('https://'):
        return url
    
    # Si no tiene protocolo, preguntar
    print(f"\n{C.Y}[?]{C.W} ¿Protocolo?{C.E}")
    print(f"{C.D}[{C.G}1{C.D}]{C.W} HTTP{C.E}")
    print(f"{C.D}[{C.C}2{C.D}]{C.W} HTTPS{C.E}")
    
    proto = input(f"{C.Y}[>]{C.W} Opción [1]: {C.E}").strip() or '1'
    
    if proto == '2':
        return f"https://{url}"
    else:
        return f"http://{url}"

def run_gobuster(url, wordlist, extensions=None, threads=50):
    """Ejecuta gobuster y muestra resultados en tiempo real"""
    
    # Construir comando base
    cmd = [
        'gobuster', 'dir',
        '-u', url,
        '-w', wordlist,
        '-t', str(threads),
        '-k',  # Skip SSL
        '-e',  # URLs completas
        '--no-error',
        '--timeout', '10s'
    ]
    
    # Agregar extensiones si se especificaron
    if extensions:
        cmd.extend(['-x', extensions])
    
    print(f"{C.D}    Comando: {' '.join(cmd)}{C.E}\n")
    
    proceso = None
    found_count = 0
    status_counts = defaultdict(int)
    
    try:
        # Ejecutar proceso
        proceso = sp.Popen(
            cmd,
            stdout=sp.PIPE,
            stderr=sp.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        found_count = 0
        status_counts = defaultdict(int)
        
        # Leer salida línea por línea
        for line in iter(proceso.stdout.readline, ''):
            if not line:
                break
                
            line = line.strip()
            
            # Mostrar encabezados de gobuster
            if line.startswith('=') or line.startswith('[+]') or 'Gobuster' in line:
                print(f"{C.D}{line}{C.E}")
                continue
            
            # Detectar resultados encontrados
            if 'http://' in line or 'https://' in line:
                found_count += 1
                
                # Extraer código de estado
                status_match = re.search(r'Status: (\d+)', line)
                if status_match:
                    status = status_match.group(1)
                    status_counts[status] += 1
                    
                    # Colorear según código
                    if status in ['200', '201', '204']:
                        print(f"{C.G}[✓ {status}] {line}{C.E}")
                    elif status in ['301', '302', '307']:
                        print(f"{C.Y}[→ {status}] {line}{C.E}")
                    elif status in ['401', '403']:
                        print(f"{C.M}[✗ {status}] {line}{C.E}")
                    else:
                        print(f"{C.C}[• {status}] {line}{C.E}")
                else:
                    print(f"{C.W}{line}{C.E}")
            
            # Mostrar progreso
            elif 'Progress:' in line:
                print(f"{C.D}{line}{C.E}", end='\r')
        
        proceso.wait()
        
        return found_count, status_counts
        
    except KeyboardInterrupt:
        print(f"\n{C.R}[!] Escaneo interrumpido{C.E}")
        proceso.kill()
        return found_count, status_counts
    except Exception as e:
        print(f"{C.R}[✗] Error: {e}{C.E}")
        return 0, {}

def main():
    try:
        banner()
        
        # Verificar herramientas
        print(f"{C.C}[·] Verificando herramientas...{C.E}")
        
        if not check_tool('gobuster'):
            print(f"{C.R}[✗] Gobuster no encontrado{C.E}")
            print(f"{C.Y}[!] Instala: sudo apt install gobuster{C.E}\n")
            return
        
        print(f"{C.G}[✓] Gobuster disponible{C.E}\n")
        
        # Menú de modo
        print(f"{C.Y}{'─'*75}{C.E}")
        print(f"{C.BOLD}{C.W}Modo de Escaneo:{C.E}\n")
        print(f"{C.D}[{C.G}1{C.D}]{C.W} RÁPIDO   {C.D}(1 wordlist, ~5 min){C.E}")
        print(f"{C.D}[{C.Y}2{C.D}]{C.W} MEDIO    {C.D}(2 wordlists, ~15 min){C.E}")
        print(f"{C.D}[{C.C}3{C.D}]{C.W} SUPREMO  {C.D}(3 wordlists, ~30 min){C.E}")
        print(f"{C.D}[{C.R}0{C.D}]{C.W} Salir{C.E}")
        print(f"{C.Y}{'─'*75}{C.E}")
        
        opcion = input(f"\n{C.Y}[>]{C.W} Opción [1]: {C.E}").strip() or '1'
        
        if opcion == '0':
            print(f"\n{C.G}[✓] Saliendo...{C.E}\n")
            return
        
        mode_map = {'1': 'rapido', '2': 'medio', '3': 'supremo'}
        mode = mode_map.get(opcion, 'rapido')
        
        # Obtener wordlists
        wordlists = get_wordlists(mode)
        
        if not wordlists:
            print(f"\n{C.R}[✗] No se encontraron wordlists{C.E}")
            print(f"{C.Y}[!] Instala: sudo apt install wordlists seclists{C.E}\n")
            return
        
        # Obtener URL
        print(f"\n{C.Y}{'─'*75}{C.E}")
        url_input = input(f"{C.Y}[>]{C.W} URL objetivo: {C.E}").strip()
        
        if not url_input:
            print(f"{C.R}[✗] URL requerida{C.E}\n")
            return
        
        url = normalize_url(url_input)
        
        # Threads
        print(f"\n{C.Y}[?]{C.W} Threads [50]: {C.E}", end="")
        threads_input = input().strip()
        threads = int(threads_input) if threads_input.isdigit() and 1 <= int(threads_input) <= 200 else 50
        
        # Extensiones
        print(f"\n{C.Y}[?]{C.W} Extensiones (php,html,txt) o ENTER para ninguna: {C.E}")
        extensions = input(f"{C.Y}[>]{C.W} {C.E}").strip()
        
        # Iniciar escaneo
        print(f"\n{C.M}{'═'*75}")
        print(f"{C.BOLD}{C.W}  ⚡ INICIANDO ESCANEO - MODO {mode.upper()}{C.E}")
        print(f"{C.M}{'═'*75}{C.E}")
        print(f"{C.C}[*]{C.W} Target: {C.Y}{url}{C.E}")
        print(f"{C.C}[*]{C.W} Wordlists: {C.Y}{len(wordlists)}{C.E}")
        print(f"{C.C}[*]{C.W} Threads: {C.Y}{threads}{C.E}")
        if extensions:
            print(f"{C.C}[*]{C.W} Extensiones: {C.Y}{extensions}{C.E}")
        print(f"{C.M}{'═'*75}{C.E}\n")
        
        total_found = 0
        all_status = defaultdict(int)
        
        # Ejecutar con cada wordlist
        for i, wordlist in enumerate(wordlists, 1):
            wl_name = os.path.basename(wordlist)
            
            try:
                wl_size = sum(1 for _ in open(wordlist, errors='ignore'))
            except:
                wl_size = 0
            
            print(f"{C.M}{'─'*75}")
            print(f"{C.BOLD}[{i}/{len(wordlists)}] {wl_name}{C.D} ({wl_size:,} palabras){C.E}")
            print(f"{C.M}{'─'*75}{C.E}\n")
            
            # Escaneo sin extensiones
            print(f"{C.C}[*] Escaneando directorios...{C.E}\n")
            found, status_counts = run_gobuster(url, wordlist, None, threads)
            total_found += found
            for status, count in status_counts.items():
                all_status[status] += count
            
            # Escaneo con extensiones si se especificaron
            if extensions:
                print(f"\n{C.C}[*] Escaneando archivos con extensiones...{C.E}\n")
                found, status_counts = run_gobuster(url, wordlist, extensions, threads)
                total_found += found
                for status, count in status_counts.items():
                    all_status[status] += count
        
        # Resumen final
        print(f"\n{C.G}{'═'*75}")
        print(f"{C.BOLD}{C.G}  ✓ ESCANEO COMPLETADO{C.E}")
        print(f"{C.G}{'═'*75}{C.E}")
        print(f"{C.C}[*]{C.W} Total encontrados: {C.Y}{total_found}{C.E}")
        
        if all_status:
            print(f"\n{C.C}[*]{C.W} Distribución por código:{C.E}")
            for status in sorted(all_status.keys()):
                color = C.G if status in ['200', '201', '204'] else C.Y if status in ['301', '302'] else C.M
                print(f"    {color}[{status}]: {all_status[status]}{C.E}")
        
        print(f"{C.G}{'═'*75}{C.E}\n")
        
    except KeyboardInterrupt:
        print(f"\n\n{C.R}[!] Interrumpido por usuario{C.E}\n")
    except Exception as e:
        print(f"\n{C.R}[✗] Error: {e}{C.E}\n")

if __name__ == "__main__":
    main()