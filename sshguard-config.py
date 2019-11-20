import os
import re
import platform
import socket

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
	print("[!] WARNING! This script only will work if sshguard is already installed.")   
	print(colors.RESET)

def menu():
	print(colors.YELLOW + "Select option: ")
	print(" [1] Protect ports.")
	print(" [2] Whitelist addresses.")
	print(" [x] Exit.")
	i = input("> ")
	while(i != "x"):
		if i == "1":
			print("1")
		elif i == "2":
			print("2")
		else:
			print("Invalid option.")	

def menu_whitelist():
	print(colors.YELLOW + "Insert IP addresses, IP address ranges or hostnames to whitelist (type . to finish): ")
	i = input("> ")
	while(i != "."):
		whitelist(i)

def menu_ports():
	i = input(colors.YELLOW + "Input ports to be secured by sshguard, separated by spaces (f.e. 22 80 25): " + colors.RESET)
	ports = list(map(int, re.findall('\d+', i)))
	print(ports)
	if getOS() == "OSX":
		print("OSX")
		#setConfigOSX(ports)
	elif getOS() == "Linux":
		print("Linux")		
		#setConfigLinux(ports)
	else:
		print(colors.RED + "Sorry but this script only works in Linux and OSX by now :(")
		exit()
        
def setConfigOSX(ports):
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
	print("Done." + colors.RESET)

def setConfigLinux(ports):
	if len(ports): # Si se reciben puertos, ponerlos en la plantilla
		print(colors.YELLOW + "Securing selected ports...")
		p1 = "sudo iptables -A INPUT -m multiport -p tcp --destination-ports "
		p2 = " -j sshguard"
		for port in ports[:-1]:
		    p1 += str(port) + ','
		p1 += str(ports[-1])
		comando = p1 + p2
		os.system(comando)
		os.system("sudo service iptables save")
		os.system("sudo service iptables restart")
	else: # Si no se reciben puertos, hacer referencia a todos los puertos
		print(colors.YELLOW + "Securing all ports...")
		os.system("sudo iptables -N sshguard")
		os.system("sudo ip6tables -N sshguard")
	print("Done." + colors.RESET)
	return

def whitelist(addr):
	# CAMBIAR!!!!
	# Comprobar formato ip, rango ip o hostname	
	try:
		socket.inet_aton(addr) # legal
		# Realizar whitelisting
		print(colors.GREEN + addr + " whitelisted." + colors.RESET)
	except socket.error:
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
	# Comprobar si se ha ejecutado en modo root
	#if os.getuid() != 0:
	#	print(colors.RED + "Please, run as root." + colors.RESET)
	#	exit()

	try:
		printBanner()
		#menu()
		#whitelist("hola.com")
		print(is_valid_ip("192.168.1.1"))	
		print(is_valid_hostname("hola.com"))	
		exit()
	except KeyboardInterrupt:
		print(colors.YELLOW + "\nBye :)" + colors.RESET)
		exit()

if __name__== "__main__":
	main()
