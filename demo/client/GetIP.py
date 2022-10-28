import socket
import asyncio
import rsa
import json
import os
import sys
import random
import string

config = {}
DIR = os.path.dirname(os.path.realpath(__file__))
try:
    file = open(os.path.join(DIR,"config.json"),"r",encoding="utf-8")
    config = json.loads(file.read())
    config["PUBLIC_KEY"] = rsa.PublicKey.load_pkcs1(config["PUBLIC_KEY"].encode('utf8'))
    config["PRIVATE_KEY"] = rsa.PrivateKey.load_pkcs1(config["PRIVATE_KEY"].encode('utf8'))
    file.close()
except FileNotFoundError:
    print("Generating default config.")
    publicKey, privateKey = rsa.newkeys(512)
    config["PUBLIC_KEY"] = publicKey.save_pkcs1().decode('utf8')
    config["PRIVATE_KEY"] = privateKey.save_pkcs1().decode('utf8')
    config["ROLE"] = ""
    config["SECRET"] = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    config["SERVER_ADDRESS"] = ""
    config["SERVER_PORT"] = random.randint(2048,8192)
    config["HOSTNAME"] = socket.gethostname()
    file = open(os.path.join(DIR,"config.json"),"w",encoding="utf-8")
    json.dump(config,file,indent=2)
    file.close()
    print("Finish generating default config. Exiting...")
    sys.exit(1)

bufferSize = 1024

def server():
    bufferSize = 1024

    # Create a datagram socket
    listenSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # Bind to address and ip
    listenSocket.bind((config["SERVER_ADDRESS"], config["SERVER_PORT"]))
    print("UDP server up and listening")

    clientHostnameIP = ""
    while True:
        bytesAddressPair = listenSocket.recvfrom(bufferSize)
        try:
            decMessage = rsa.decrypt(bytesAddressPair[0], config["PRIVATE_KEY"]).decode()
        except rsa.DecryptionError:
            print(f"Receive invalid message {bytesAddressPair[0]}")
            continue

        revSecret = decMessage[:len(config["SECRET"])]
        secret = config["SECRET"]
        if  revSecret == secret:
            role = decMessage[len(config["SECRET"])+1:]
            if role[:len("CLIENT")] == "CLIENT":
                hostname = decMessage[len(config['SECRET'])+2+len('CLIENT'):]
                ip_add = bytesAddressPair[1][0]
                print(f"{hostname}: {ip_add}")
                clientHostnameIP = f"{hostname}: {ip_add}"
            elif role[:len("OBSERVER")] == "OBSERVER":
                message = f"{secret} SERVER {clientHostnameIP}"
                encMessage = rsa.encrypt(message.encode(),config["PUBLIC_KEY"])

                listenSocket.sendto(encMessage, bytesAddressPair[1])

def client():
    message = f"{config['SECRET']} {config['ROLE'].upper()} {config['HOSTNAME']}"
    encMessage = rsa.encrypt(message.encode(),config["PUBLIC_KEY"])

    serverAddressPort   = (config["SERVER_ADDRESS"], config["SERVER_PORT"])

    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # Send to server using created UDP socket
    UDPClientSocket.sendto(encMessage, serverAddressPort)

def observer():
    message = f"{config['SECRET']} OBSERVER"
    encMessage = rsa.encrypt(message.encode(),config["PUBLIC_KEY"])

    serverAddressPort   = (config["SERVER_ADDRESS"], config["SERVER_PORT"])

    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # Send to server using created UDP socket
    UDPClientSocket.sendto(encMessage, serverAddressPort)

    bytesAddressPair = UDPClientSocket.recvfrom(bufferSize)
    try:
        decMessage = rsa.decrypt(bytesAddressPair[0], config["PRIVATE_KEY"]).decode()
    except rsa.DecryptionError:
        print(f"Receive invalid message {bytesAddressPair[0]}")
        return

    revSecret = decMessage[:len(config["SECRET"])]
    secret = config["SECRET"]
    if revSecret == secret:
        role = decMessage[len(config["SECRET"])+1:len(config["SECRET"])+1+len("SERVER")]
        if role == "SERVER":
                print(decMessage[len(config["SECRET"])+2+len("SERVER"):])


if config["ROLE"].lower() == "server":
    server()
elif config["ROLE"].lower() == "client":
    client()
elif config["ROLE"].lower() == "observer":
    observer()
else:
    print("Wrong ROLE in config.")

    