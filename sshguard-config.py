import os
import re
import platform

FILEPATH_OSX_PLANT = "osx-conf.txt"
FILEPATH_OSX_CONFIG = "/etc/pf.conf"
FILEPATH_BANNER = "banner.txt"
PLANTILLA =  "### __SSHGUARD-CONFIG___ ###"

class colors:
	RED = '\u001b[31m'
	GREEN = '\u001b[32m'
	YELLOW = '\u001b[33m'
	BLUE = '\u001b[34m'
	MAGENTA = '\u001b[35m'
	CYAN = '\u001b[36m'
	RESET = '\u001b[0m'

def getOS():
    if platform.system() == "Darwin":
        return "OSX"
    return platform.system()

def printBanner():
    with open(FILEPATH_BANNER, 'r') as file:
        f = file.read()
    print(colors.RED + f + "\n")
    print(colors.BLUE + "Running on " + getOS() + " system")    
    print(colors.RESET)

def menu():
    i = input(colors.YELLOW + "Input ports to be secured by sshguard, separated by spaces (f.e. 22 80 25): " + colors.RESET)
    ports = list(map(int, re.findall('\d+', i)))
    print(ports)
    if getOS() == "OSX":
        setConfigOSX(ports)
        
def setConfigOSX(ports):
    print(colors.YELLOW + "Configuring sshguard in OSX...")
    # Recibir plantilla de configuración
    with open(FILEPATH_OSX_PLANT, 'r') as file:
        f = file.read()
    if len(ports): # Si se reciben puertos, ponerlos en la plantilla
        s = ' '.join([str(elem) for elem in ports])
        f = f.replace("_PUERTOS_",s) 
        f = f.replace("_PORTS_"," port $ports ")
    else: # Si no se reciben puertos, hacer referencia a todos los puertos
        f = f.replace("_PUERTOS_","")
        f = f.replace("_PORTS_"," ")

    # Buscar los números de línea de las plantilla
    with open(FILEPATH_OSX_CONFIG, 'r') as file_c:
        f_conf = file_c.read();
    indicesPlantillas = [i for i, x in enumerate(f_conf.split("\n")) if x == PLANTILLA]

    if len(indicesPlantillas) == 0: # Si no hay números, no había configuración previa
        with open(FILEPATH_OSX_CONFIG, "a") as file: # Escribir configuración en pf.conf
            file.write(f)
    else: # Si hay números, sustituir configuración antigua entre las plantillas
        with open(FILEPATH_OSX_CONFIG, "r") as fi: # Recoger lineas
            lines = fi.readlines()
        with open(FILEPATH_OSX_CONFIG, "w") as fi: # Borrar lineas
            i = 0
            for line in lines:
                if i<indicesPlantillas[0] or i>indicesPlantillas[1]:
                    fi.write(line)
                i = i + 1
        with open(FILEPATH_OSX_CONFIG, "a") as file: # Escribir configuración en pf.conf
            file.write(f)   

    # Recargar configuración de pf
    print("Reloading pf configuration...")
    os.system("pfctl -f /etc/pf.conf") 
    # Hacer que sshguard se ejecute en el inicio
    print("Configuring sshguard to run at startup...")
    os.system("cp -fv /usr/local/opt/sshguard/*.plist /Library/LaunchDaemons")
    # Ejecutar sshguard
    print("Executing sshguard...")
    os.system("launchctl load /Library/LaunchDaemons/homebrew.mxcl.sshguard.plist")
    print("Done." + colors.RESET)

#setConfigOSX([22]);
printBanner()
menu()
