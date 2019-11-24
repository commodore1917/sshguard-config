import os
import re
import platform
import socket
import ipaddress

FILEPATH_OSX_PLANT = os.path.dirname(__file__) + "/resources/osx-conf.txt"
FILEPATH_OSX_CONFIG = "/etc/pf.conf"
FILEPATH_BANNER = os.path.dirname(__file__) + "/resources/banner.txt"
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
    os.system("clear")
    with open(FILEPATH_BANNER, 'r') as file:
        f = file.read()
    print(colors.RED + f + "\n")
    print("Created by Ioar Crespo and Guillermo Berasategui")
    print(colors.BLUE + "Running on " + getOS() + " system") 
    print("[!] WARNING! This script only will work if sshguard is already installed.")   
    print(colors.RESET)

def menu():
    i = ""
    while(i != "x"):
        print(colors.YELLOW + "---------- MAIN MENU ----------")
        print("Select option: ")
        print(" [1] Set protected ports.")
        print(" [2] Whitelist addresses.")
        print(" [3] Set attack score threshold.")
        print(" [4] Set blocktime.")
        print(" [5] Set detection time.")       
        print(" [x] Exit.")
        i = input("> ")
        if i == "1":
             menu_ports()
        elif i == "2":
            print(colors.RED + "Sorry. Not working until SSHGUARD fixes it.")
            # menu_whitelist()
        elif i == "3":
            print(colors.RED + "Sorry. Not working until SSHGUARD fixes it.")
            # set_score()
        elif i == "4":
            print(colors.RED + "Sorry. Not working until SSHGUARD fixes it.")
            # set_blocktime()
        elif i == "5":
            print(colors.RED + "Sorry. Not working until SSHGUARD fixes it.")
            # set_detection_time()
        elif i == "x":
            print(colors.YELLOW + "Bye :)" + colors.RESET)
        else:
            print(colors.RED +  "Invalid option.")

def menu_whitelist():
    print(colors.YELLOW + "Insert IP addresses, IP address ranges or hostnames to whitelist (type 'x' to exit): ")
    i = input("> ")
    while(i != "."):
        whitelist(i)
        i = input("> ")

def menu_ports():
    print(colors.YELLOW + "Input ports to be secured by sshguard, separated by spaces (f.e.: 22 80 25).")
    print("Type 'all' to secure all ports. Type 'x' to go back to menu.")
    i = input("> ")
    if i == "all":
        ports = []
    elif i == "x":
        return
    else:
        ports = list(map(int, re.findall('\d+', i)))
    print(ports)
    if getOS() == "OSX":
        setPortConfigOSX(ports)
    elif getOS() == "Linux":	
        setPortConfigLinux(ports)
    else:
        print(colors.RED + "Sorry but this script only works in Linux and OSX by now :(")
        exit()

def set_score():
    print(colors.YELLOW + "Block attackers when their cumulative attack score exceeds threshold.") 
    print("Most attacks have a score of 10. Default is 30.")
    print("Type score number. Type 'x' to exit.")
    i = input("> ")
    while True:
        i = input("> ")
        if i.isdigit():
            if getOS() == "Linux":
                os.system("sudo sshguard -a " + i)
                print(colors.GREEN + "Done." + colors.RESET)
                restart()
            elif getOS() == "OSX":
                os.system("sudo /usr/local/opt/sshguard/sbin/sshguard -a " + i)
                print(colors.GREEN + "Done." + colors.RESET)
                restart()
        elif i == "x":
            return
        else:
            print("Wrong input. Try again (type 'x' to exit)")

def set_blocktime():
    print(colors.YELLOW + "Block  attackers  for initially blocktime seconds after exceeding threshold.")
    print("Subsequent blocks increase by a factor of 1.5. Default is 120.")
    print("Type seconds number. Type 'x' to exit.")
    i = input("> ")
    while True:
        i = input("> ")
        if i.isdigit():
            if getOS() == "Linux":
                os.system("sudo sshguard -p " + i)
                print(colors.GREEN + "Done." + colors.RESET)
                restart()
            elif getOS() == "OSX":
                os.system("sudo /usr/local/opt/sshguard/sbin/sshguard -p " + i)
                print(colors.GREEN + "Done." + colors.RESET)
                restart()
        elif i == "x":
            return
        else:
            print("Wrong input. Try again (type 'x' to exit)")

def set_detection_time():
    print(colors.YELLOW + "Remember  potential attackers for up to detection_time seconds before resetting their score.")
    print("Default is 1800.")
    print("Type seconds number. Type 'x' to exit.")
    i = input("> ")
    while True:
        i = input("> ")
        if i.isdigit():
            if getOS() == "Linux":
                os.system("sudo sshguard -s " + i)
                print(colors.GREEN + "Done." + colors.RESET)
                restart()
            elif getOS() == "OSX":
                os.system("sudo /usr/local/opt/sshguard/sbin/sshguard -s " + i)
                print(colors.GREEN + "Done." + colors.RESET)
                restart()
        elif i == "x":
            return
        else:
            print("Wrong input. Try again (type 'x' to exit)")

def setPortConfigOSX(ports):
    print(colors.YELLOW + "Configuring sshguard in OSX...")
    # Recibir plantilla de configuración
    with open(FILEPATH_OSX_PLANT, 'r') as file:
        f = file.read()
    if len(ports): # Si se reciben puertos, ponerlos en la plantilla
        print("Securing selected ports...")
        s = ' '.join([str(elem) for elem in ports])
        f = f.replace("_PUERTOS_",s) 
        f = f.replace("_PORTS_"," port $ports ")
    else: # Si no se reciben puertos, hacer referencia a todos los puertos
        print("Securing all ports...")        
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
                i += 1
    with open(FILEPATH_OSX_CONFIG, "a") as file: # Escribir configuración en pf.conf
        file.write(f)   

    # Recargar configuración de pf
    print("Reloading pf configuration...")
    os.system("sudo pfctl -f /etc/pf.conf") 
    # Hacer que sshguard se ejecute en el inicio
    print("Configuring sshguard to run at startup...")
    os.system("sudo cp -fv /usr/local/opt/sshguard/*.plist /Library/LaunchDaemons")
    # Ejecutar sshguard
    print("Executing sshguard...")
    os.system("sudo launchctl load /Library/LaunchDaemons/homebrew.mxcl.sshguard.plist")
    print(colors.GREEN + "Done." + colors.RESET)
    restart()

def setPortConfigLinux(ports):
    if len(ports): # Si se reciben puertos, ponerlos en la plantilla
        print(colors.YELLOW + "Securing selected ports...")
        p1 = "sudo iptables -A INPUT -m multiport -p tcp --destination-ports "
        p2 = " -j sshguard"
        for port in ports[:-1]:
            p1 += str(port) + ','
            p1 += str(ports[-1])
            comando = p1 + p2
            os.system(comando)
            os.system("sudo service networking restart") # (Ubuntu)
    else: # Si no se reciben puertos, hacer referencia a todos los puertos
        print(colors.YELLOW + "Securing all ports...")
        os.system("sudo iptables -N sshguard")
        os.system("sudo ip6tables -N sshguard")
        print(colors.GREEN + "Done." + colors.RESET)
    restart()
    return

def restart():
    if getOS() == "Linux":
        os.system("sudo service sshguard restart")
    elif getOS() == "OSX":
        os.system("brew services start sshguard")
    print(colors.GREEN + "SSHGuard restarted." + colors.RESET)

def whitelist(addr):
    # Comprobar formato ip, rango ip o hostname	
    if is_valid_ip(addr) or is_valid_hostname(addr) or is_valid_ip_range(addr):
        if getOS() == "Linux":
            os.system("sudo sshguard -w " + addr)
            print(colors.GREEN + addr + " whitelisted." + colors.RESET)
        elif getOS() == "OSX":
            os.system("sudo /usr/local/opt/sshguard/sbin/sshguard -w " + addr)
            print(colors.GREEN + addr + " whitelisted." + colors.RESET)
        restart()
    else:
        print(colors.RED + "Wrong format. Try again." + colors.RESET)

def is_valid_ip(addr):
	try:
		socket.inet_aton(addr)
		return True
	except socket.error:
		return False

def is_valid_ip_range(addr):
	try:
		ipaddress.ip_network('192.168.0.0/28')
		return True
	except ValueError:
		return False

def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))

def main():
    # Si el script se ejecuta en Windows cerrar, porque no es compatible
    if getOS() == "Windows":
        exit()

    # Comprobar si se ha ejecutado en modo root
    if os.getuid() != 0:
        print(colors.RED + "Please, run as root." + colors.RESET)
        exit()

    try:
        printBanner()
        menu()
        exit()
    except KeyboardInterrupt:
        print(colors.YELLOW + "\nExiting...\nBye :)" + colors.RESET)
        exit()

if __name__== "__main__":
    main()
