import os

def block_all_ports():
    c1 = "sudo iptables -N sshguard"
    c2 = "sudo ip6tables -N sshguard"
    os.system(c1)
    os.system(c2)
    return 

def block_some_ports():
    print("Introduce los puertos separados por comas y 'enter' para finalizar")
    print("ej: 22, 80, 120")
    in_puertos = input()
    arr_puertos = in_puertos.split(",")
    arr_puertos = [port.replace(" ", "") for port in arr_puertos] #eliminar espacios en blanco
    p1 = "sudo iptables -A INPUT -m multiport -p tcp --destination-ports "
    p2 = " -j sshguard"
    for port in arr_puertos[:-1]:
        p1 += port + ','
    p1 += arr_puertos[-1]
    comando = p1 + p2
    print(comando)
    os.system(comando)
    return 

def block_extrem():
    print("AVISO: En este modo selecciona los puertos que deseas mantener abiertos y el resto seran cerrados (default deny)")
    print("En caso de querer volver abrir todos los puertos ejecutar $iptables -I INPUT -j ACCEPT")
    print("Indique los puertos que desee mantener abiertos separados por comas")
    print("ejemplo: 22, 53, 80")
    in_puertos = input()
    arr_puertos = in_puertos.split(",")
    arr_puertos = [port.replace(" ", "") for port in arr_puertos] #eliminar espacios en blanco
    p1 = "sudo iptables -A INPUT -p tcp --dport "
    p2 = " -j ACCEPT"
    for puerto in arr_puertos:
        auxp1 = p1
        auxp2 = p2
        comando = p1 + puerto + p2
        os.system(comando)
    final = "sudo iptables -P INPUT DROP"
    os.system(final)
    return 

    

def main():
    block_all_ports()
    print("Script para configuar los puertos los puertos bloqueados por sshguard")
    print("Seleccione una opcion: ")
    print("1 - Proteger todos los puertos")
    print("2 - Elegir los puertos a seleccionar")
    print("3 - Seguridad extrema")
    eleccion = input()
    while not eleccion.isdigit():
        print("Por favor introduce un numero")
        eleccion = input()
    while (int(eleccion) not in [1,2,3]):
        print("Por favor seleccione 1 o 2")
        eleccion = input()
        while not eleccion.isdigit():
            print("Por favor introduce un numero")
            eleccion = input()
    eleccion = int(eleccion)

    if eleccion==1:
        block_all_ports()
    elif eleccion==2:
        block_some_ports()
    else:
        block_extrem()
    print("\n\n¡Puertos asegurados, puedes utilizar tu pc tranquilo!")

main()