#!/usr/bin/env python3
import subprocess
import os
import time

# Colores ANSI
class Color:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def limpiar_pantalla():
    """Limpia la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    """Muestra el banner ASCII"""
    banner_art = f"""
{Color.CYAN}{Color.BOLD}
  ████████╗ ██████╗  ██████╗ ██╗     ███████╗
  ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
     ██║   ██║   ██║██║   ██║██║     ███████╗
     ██║   ██║   ██║██║   ██║██║     ╚════██║
     ██║   ╚██████╔╝╚██████╔╝███████╗███████║
     ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
{Color.RESET}
{Color.RED}    ╔═══════════════════════════════════════════════════╗
    ║  {Color.YELLOW}🔓   autor: Ferxxo                         {Color.RED}      ║
    ╚═══════════════════════════════════════════════════╝{Color.RESET}
"""
    print(banner_art)

def mostrar_menu():
    """Muestra el menú principal"""
    limpiar_pantalla()
    banner()

    print()
    print(f"  {Color.YELLOW}[{Color.WHITE}1{Color.YELLOW}]{Color.CYAN} ➤  Nmap           {Color.DIM}(Network Scanner){Color.RESET}")
    print(f"  {Color.YELLOW}[{Color.WHITE}2{Color.YELLOW}]{Color.CYAN} ➤  Gobuster       {Color.DIM}(Directory Bruteforce){Color.RESET}")
    print(f"  {Color.YELLOW}[{Color.WHITE}3{Color.YELLOW}]{Color.CYAN} ➤  SQLmap         {Color.DIM}(SQL Injection){Color.RESET}")
    print(f"  {Color.YELLOW}[{Color.WHITE}4{Color.YELLOW}]{Color.CYAN} ➤  John The Ripper{Color.DIM}(Password Cracker){Color.RESET}")
    print(f"  {Color.YELLOW}[{Color.WHITE}5{Color.YELLOW}]{Color.CYAN} ➤  Hydra          {Color.DIM}(Login Bruteforce){Color.RESET}")
    print(f"  {Color.YELLOW}[{Color.WHITE}6{Color.YELLOW}]{Color.CYAN} ➤  MSFvenom          {Color.DIM}(Create payloads){Color.RESET}")
    print(f"  {Color.YELLOW}[{Color.WHITE}7{Color.YELLOW}]{Color.CYAN} ➤  Spoofer          {Color.DIM}(Spoofer ){Color.RESET}")
    print(f"  {Color.YELLOW}[{Color.WHITE}8{Color.YELLOW}]{Color.CYAN} ➤  Wfuzz          {Color.DIM}(escaneo de subdominios ){Color.RESET}")
    print(f"  {Color.YELLOW}[{Color.WHITE}9{Color.YELLOW}]{Color.CYAN} ➤  hack-wifi          {Color.DIM}(Aircrak-ng ){Color.RESET}")
    print()
    print(f"  {Color.RED}[{Color.WHITE}0{Color.RED}]{Color.MAGENTA} ➤  Salir{Color.RESET}")
    print()
    print(f"{Color.GREEN}{'─' * 59}{Color.RESET}")
    print()

def main():
    """Función principal"""
    
    # Diccionario con los NOMBRES DE ARCHIVO de cada herramienta
    herramientas = {
        '1': 'script_nmap.py',
        '2': 'script_gobuster.py',
        '3': 'script_sqlmap.py',
        '4': 'script_John.py',
        '5': 'scritp_hydra.py',
        '6': 'script_MSFvenom.py',
        '7': 'spoofer.py',
        '8': 'WFUZZ.py',
        '9': 'aircrak-ng.py',
    }
    
    nombres_herramientas = {
        '1': 'Nmap',
        '2': 'Gobuster',
        '3': 'SQLmap',
        '4': 'John The Ripper',
        '5': 'Hydra',
        '6': 'MSVvenom',
        '7': 'Spoofing',
        '8': 'Wfuzz',
        '9': 'hack-wifi',
    }
    
    while True:
        mostrar_menu()
        opcion = input(f"{Color.YELLOW}┌──({Color.RED}root@tools{Color.YELLOW})-[{Color.CYAN}~{Color.YELLOW}]\n└─{Color.RED}$ {Color.RESET}").strip()
        
        if opcion == '0':
            limpiar_pantalla()
            print(f"\n{Color.RED}[{Color.YELLOW}!{Color.RED}] {Color.CYAN}Cerrando herramientas...{Color.RESET}")
            time.sleep(0.5)
            print(f"{Color.GREEN}[{Color.YELLOW}✓{Color.GREEN}] {Color.WHITE}¡Hasta luego, hacker!{Color.RESET}\n")
            break
        
        if opcion in herramientas:
            limpiar_pantalla()
            print(f"\n{Color.CYAN}{'═' * 59}{Color.RESET}")
            print(f"{Color.GREEN}[{Color.YELLOW}+{Color.GREEN}] {Color.WHITE}Ejecutando: {Color.CYAN}{nombres_herramientas[opcion]}{Color.RESET}")
            print(f"{Color.CYAN}{'═' * 59}{Color.RESET}\n")
            
            # Ejecuta el archivo .py de la herramienta
            subprocess.run(['python3', herramientas[opcion]])
            
            print(f"\n{Color.CYAN}{'═' * 59}{Color.RESET}")
            input(f"{Color.GREEN}[{Color.YELLOW}✓{Color.GREEN}] {Color.WHITE}Presiona ENTER para volver al menú...{Color.RESET}")
        else:
            print(f"\n{Color.RED}[{Color.YELLOW}!{Color.RED}] {Color.WHITE}Opción no válida{Color.RESET}")
            time.sleep(1)

if __name__ == "__main__":
    main()