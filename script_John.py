#!/usr/bin/env python3
"""
John Simple - Hash cracker directo
"""

import subprocess
import sys
import os
import time
import re

# Colores hacker
G = '\033[92m'   # Verde
R = '\033[91m'   # Rojo
Y = '\033[93m'   # Amarillo
C = '\033[96m'   # Cyan
M = '\033[95m'   # Magenta
W = '\033[97m'   # Blanco
D = '\033[90m'   # Gris oscuro
E = '\033[0m'    # Reset

def banner():
    print(f"""{R}
     ██╗ ██████╗ ██╗  ██╗███╗   ██╗
     ██║██╔═══██╗██║  ██║████╗  ██║
     ██║██║   ██║███████║██╔██╗ ██║
██   ██║██║   ██║██╔══██║██║╚██╗██║
╚█████╔╝╚██████╔╝██║  ██║██║ ╚████║
 ╚════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
{E}{C}    ══════════════════════════════════════════════════════════{E}
{D}            [John The Ripper - Hash Cracker v1.0]{E}
{C}    ══════════════════════════════════════════════════════════{E}
""")

def formatos_comunes():
    """Muestra formatos de hash comunes"""
    print(f"\n{M}{'─'*60}{E}")
    print(f"{Y}[>]{W} Formatos de hash comunes:{E}\n")
    print(f"{D}  • {G}raw-md5{D}     - MD5 hash (32 chars){E}")
    print(f"{D}  • {G}raw-sha1{D}    - SHA1 hash (40 chars){E}")
    print(f"{D}  • {G}raw-sha256{D}  - SHA256 hash (64 chars){E}")
    print(f"{D}  • {G}NT{D}          - NTLM (Windows) (32 chars){E}")
    print(f"{D}  • {G}descrypt{D}    - DES Unix{E}")
    print(f"{D}  • {G}bcrypt{D}      - Bcrypt ($2a$, $2b$, $2y$){E}")
    print(f"{D}  • {G}md5crypt{D}    - MD5 Unix ($1$){E}")
    print(f"{M}{'─'*60}{E}")

def identificar_hash(hash_value):
    """Intenta identificar el tipo de hash por características"""
    hash_value = hash_value.strip()
    longitud = len(hash_value)
    
    posibles = []
    
    # Por prefijos
    if hash_value.startswith('$1$'):
        posibles.append(('md5crypt', 'MD5 Unix'))
    elif hash_value.startswith('$2a$') or hash_value.startswith('$2b$') or hash_value.startswith('$2y$'):
        posibles.append(('bcrypt', 'Bcrypt'))
    elif hash_value.startswith('$5$'):
        posibles.append(('sha256crypt', 'SHA256 Unix'))
    elif hash_value.startswith('$6$'):
        posibles.append(('sha512crypt', 'SHA512 Unix'))
    elif hash_value.startswith('{SHA}'):
        posibles.append(('raw-sha1', 'SHA1 (Base64)'))
    elif hash_value.startswith('$P$') or hash_value.startswith('$H$'):
        posibles.append(('phpass', 'WordPress/phpBB'))
    
    # Por longitud (solo hex)
    if re.match(r'^[a-fA-F0-9]+$', hash_value):
        if longitud == 32:
            posibles.append(('raw-md5', 'MD5'))
            posibles.append(('NT', 'NTLM (Windows)'))
        elif longitud == 40:
            posibles.append(('raw-sha1', 'SHA1'))
        elif longitud == 64:
            posibles.append(('raw-sha256', 'SHA256'))
        elif longitud == 96:
            posibles.append(('raw-sha384', 'SHA384'))
        elif longitud == 128:
            posibles.append(('raw-sha512', 'SHA512'))
        elif longitud == 13:
            posibles.append(('descrypt', 'DES Unix'))
    
    # Cisco ASA/PIX (suelen tener formato específico)
    if ':' in hash_value:
        partes = hash_value.split(':')
        if len(partes) == 2 and len(partes[1]) == 16:
            posibles.append(('asa-md5', 'Cisco ASA MD5'))
    
    return posibles

def mostrar_identificacion(hash_value, john_cmd):
    """Usa hashcat o análisis manual para identificar el hash"""
    print(f"\n{C}[*]{W} Analizando el hash...{E}\n")
    
    # Identificación manual
    posibles = identificar_hash(hash_value)
    
    if posibles:
        print(f"{G}[✓]{W} Posibles tipos de hash detectados:{E}\n")
        for idx, (formato, descripcion) in enumerate(posibles, 1):
            print(f"{D}  [{idx}] {G}{formato}{D} - {descripcion}{E}")
        print()
        return [f[0] for f in posibles]
    else:
        print(f"{Y}[!]{W} No se pudo identificar automáticamente el tipo de hash{E}")
        print(f"{Y}[!]{W} Puedes intentar con autodetección de John{E}\n")
        return []

def run():
    banner()
    
    # Verificar John - buscar en múltiples ubicaciones
    john_cmd = None
    possible_cmds = ["john", "/usr/sbin/john", "/usr/bin/john", "/snap/bin/john"]
    
    print(f"{C}[*]{W} Buscando John The Ripper...{E}\n")
    
    for cmd in possible_cmds:
        try:
            # John no acepta --version, probamos sin argumentos
            result = subprocess.run([cmd], 
                                  capture_output=True, 
                                  stderr=subprocess.STDOUT,
                                  timeout=1)
            # Si el comando existe (aunque falle por falta de args)
            john_cmd = cmd
            print(f"{G}[✓]{W} John encontrado: {C}{john_cmd}{E}\n")
            break
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            # Si timeout, significa que existe pero está esperando input
            john_cmd = cmd
            print(f"{G}[✓]{W} John encontrado: {C}{john_cmd}{E}\n")
            break
        except Exception:
            continue
    
    if not john_cmd:
        # Último intento - usar which
        try:
            result = subprocess.run(["which", "john"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and result.stdout.strip():
                john_cmd = result.stdout.strip()
                print(f"{G}[✓]{W} John encontrado con 'which': {C}{john_cmd}{E}\n")
        except:
            pass
    
    if not john_cmd:
        print(f"{R}[✗] John The Ripper no encontrado{E}")
        print(f"{D}    Instalar: sudo apt install john{E}\n")
        return
    
    # Tipo de ataque
    print(f"{M}{'─'*60}{E}")
    print(f"{Y}[>]{W} ¿Qué deseas crackear?{E}\n")
    print(f"{D}  [1] {G}Hash individual{E}")
    print(f"{D}  [2] {G}Archivo con múltiples hashes{E}")
    print(f"{M}{'─'*60}{E}")
    
    tipo = input(f"\n{C}  Selecciona opción (1-2): {E}").strip()
    
    hash_file = None
    temp_file = False
    hash_para_identificar = None
    
    if tipo == "1":
        # Hash individual
        hash_value = input(f"\n{C}  Hash a crackear: {E}").strip()
        
        if not hash_value:
            print(f"{R}[✗] No se ingresó ningún hash{E}\n")
            return
        
        hash_para_identificar = hash_value
        
        # Crear archivo temporal
        hash_file = "/tmp/temp_hash.txt"
        with open(hash_file, 'w') as f:
            f.write(hash_value + '\n')
        temp_file = True
    
    elif tipo == "2":
        # Archivo
        hash_file = input(f"\n{C}  Ruta del archivo: {E}").strip()
        hash_file = os.path.expanduser(hash_file).strip('"').strip("'")
        
        if not os.path.exists(hash_file):
            print(f"{R}[✗] Archivo no encontrado{E}\n")
            return
        
        # Contar hashes y leer el primero para identificación
        with open(hash_file, 'r') as f:
            lineas = [line.strip() for line in f if line.strip()]
            num_hashes = len(lineas)
            if lineas:
                hash_para_identificar = lineas[0]
        
        print(f"{G}[✓]{W} {num_hashes} hash(es) encontrado(s){E}")
    
    else:
        print(f"{R}[✗] Opción inválida{E}\n")
        return
    
    # Identificar hash
    formatos_detectados = []
    if hash_para_identificar:
        formatos_detectados = mostrar_identificacion(hash_para_identificar, john_cmd)
    
    # Wordlist
    print(f"\n{M}{'─'*60}{E}")
    print(f"{Y}[>]{W} Wordlist (dejar vacío para rockyou.txt):{E}")
    wordlist = input(f"{C}  Ruta: {E}").strip()
    
    if not wordlist:
        # Primero buscar en la carpeta actual
        if os.path.exists("rockyou.txt"):
            wordlist = os.path.abspath("rockyou.txt")
            print(f"{G}[✓]{W} Usando rockyou.txt (carpeta actual){E}")
        elif os.path.exists("/usr/share/wordlists/rockyou.txt"):
            wordlist = "/usr/share/wordlists/rockyou.txt"
            print(f"{G}[✓]{W} Usando rockyou.txt (sistema){E}")
        else:
            print(f"{Y}[!]{W} rockyou.txt no encontrado, modo incremental{E}")
            wordlist = None
    else:
        wordlist = os.path.expanduser(wordlist).strip('"').strip("'")
        if not os.path.exists(wordlist):
            print(f"{Y}[!]{W} Wordlist no encontrado, modo incremental{E}")
            wordlist = None
    
    # Formato
    formatos_comunes()
    
    formato = None
    if formatos_detectados:
        print(f"\n{Y}[>]{W} ¿Usar uno de los formatos detectados?{E}")
        print(f"{D}  [0] {G}Autodetección{E}")
        for idx, fmt in enumerate(formatos_detectados, 1):
            print(f"{D}  [{idx}] {G}{fmt}{E}")
        print(f"{D}  [X] {G}Escribir manualmente{E}")
        
        seleccion = input(f"\n{C}  Selecciona opción: {E}").strip()
        
        if seleccion == "0":
            formato = None
            print(f"{G}[✓]{W} Autodetección activada{E}")
        elif seleccion.lower() == 'x':
            formato = input(f"{C}  Escribe el formato: {E}").strip()
            if formato:
                print(f"{G}[✓]{W} Formato manual: {formato}{E}")
            else:
                formato = None
                print(f"{G}[✓]{W} Autodetección activada{E}")
        else:
            try:
                idx = int(seleccion) - 1
                if 0 <= idx < len(formatos_detectados):
                    formato = formatos_detectados[idx]
                    print(f"{G}[✓]{W} Formato seleccionado: {formato}{E}")
            except:
                formato = None
                print(f"{Y}[!]{W} Selección inválida, usando autodetección{E}")
    else:
        print(f"\n{Y}[>]{W} Formato (dejar vacío para autodetección):{E}")
        formato = input(f"{C}  Formato: {E}").strip()
        
        if not formato:
            print(f"{G}[✓]{W} Autodetección activada{E}")
    
    # Construir comando
    cmd = [john_cmd, hash_file]
    
    if wordlist:
        cmd.append(f"--wordlist={wordlist}")
    
    if formato:
        cmd.append(f"--format={formato}")
    
    # Mostrar info
    print(f"\n{M}{'─'*60}{E}")
    print(f"{Y}[*]{W} Hash file: {G}{hash_file}{E}")
    if wordlist:
        print(f"{Y}[*]{W} Wordlist: {G}{wordlist}{E}")
    if formato:
        print(f"{Y}[*]{W} Formato: {G}{formato}{E}")
    else:
        print(f"{Y}[*]{W} Formato: {G}Autodetección{E}")
    print(f"{M}{'─'*60}{E}")
    
    # Confirmación
    confirm = input(f"\n{Y}[?]{W} ¿Iniciar cracking? (s/n): {E}").strip().lower()
    
    if confirm != 's':
        print(f"{R}[!] Cancelado{E}\n")
        if temp_file:
            os.remove(hash_file)
        return
    
    # Ejecutar
    print(f"\n{G}{'═'*60}")
    print(f"  🔐 INICIANDO JOHN THE RIPPER")
    print(f"{'═'*60}{E}\n")
    
    print(f"{D}Comando: {' '.join(cmd)}{E}\n")
    print(f"{M}{'─'*60}{E}\n")
    
    try:
        # Ejecutar john
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        print(f"\n{M}{'─'*60}{E}")
        
        # Mostrar resultados
        print(f"\n{C}[*]{W} Buscando contraseñas crackeadas...{E}\n")
        
        show_cmd = [john_cmd, "--show", hash_file]
        if formato:
            show_cmd.append(f"--format={formato}")
        
        result = subprocess.run(show_cmd, capture_output=True, text=True)
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            cracked = [line for line in lines if ':' in line and 'password hash' not in line.lower()]
            
            if cracked:
                print(f"{G}{'═'*60}")
                print(f"  💀 ¡CONTRASEÑAS CRACKEADAS!")
                print(f"{'═'*60}{E}\n")
                for line in cracked:
                    if ':' in line:
                        parts = line.split(':', 1)
                        print(f"{C}  Hash: {D}{parts[0]}{E}")
                        print(f"{C}  Pass: {G}{parts[1]}{E}\n")
                print(f"{G}{'═'*60}{E}")
            else:
                print(f"{Y}[!] No se crackearon hashes{E}")
                print(f"{Y}[!] Sugerencias:{E}")
                print(f"{D}    • La contraseña puede no estar en el wordlist{E}")
                print(f"{D}    • Intenta con un formato diferente{E}")
                print(f"{D}    • El hash puede estar dañado o incompleto{E}")
        else:
            print(f"{Y}[!] No se encontraron resultados{E}")
        
        print()
    
    except KeyboardInterrupt:
        print(f"\n{R}[!] Proceso cancelado{E}\n")
    
    except Exception as e:
        print(f"\n{R}[✗] Error: {e}{E}\n")
    
    finally:
        # Limpiar archivo temporal
        if temp_file and os.path.exists(hash_file):
            os.remove(hash_file)

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print(f"\n{R}[!] Programa interrumpido{E}\n")