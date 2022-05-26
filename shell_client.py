import subprocess
import os
import socket
import threading
import sys
import random

green = "\u001b[32m"
reset = "\u001b[0m"

class Client():

    def __init__(self) -> None:
        self.currentServer = None
        self.file_prefix = "**_$$"

    def PrivateMount(self, host, port, path):
        data = 'mount private ' + path
        self.UDPClientSocket.sendto(data.encode('utf-8'),(host,int(port)))

    def SharedMount(self, host, port, path):
        data = 'mount shared ' + path
        self.UDPClientSocket.sendto(data.encode('utf-8'),(host,int(port)))

    def sendToServer(self,message):
        self.UDPClientSocket.sendto(message.encode('utf-8'),self.currentServer )

    # gets a string of a command to be run, runs it and returns the output
    def RunCommand(self, command):
        command_formatted = command.split()
        if (command_formatted[0] == "mount"):
            if (command_formatted[1] == "private"):
                remote = command_formatted[2].split(":")
                self.PrivateMount(remote[0], remote[1], remote[2])
            elif (command_formatted[1] == "shared"):
                remote = command_formatted[2].split(":")
                self.SharedMount(remote[0], remote[1], remote[2])
            return ""

        if (command_formatted[0] == "cd"):
            if (":" in command_formatted[1]):
                destination = command_formatted[1].split(":")
                if (destination[0] == "local"):
                    self.currentServer = (destination[0],destination[1]) = None
                    try:
                        os.chdir(destination[2])
                    except Exception as e:
                        print(e)
                    
                else:
                    self.currentServer = (destination[0],int(destination[1]))
                    self.sendToServer(f"cd {destination[2]}")
                return ""
            if (self.currentServer == None):
                try:
                    os.chdir(command_formatted[1])
                except Exception as e:
                    print(e)
                return ""
        if (self.currentServer == None):
            result = subprocess.run(command_formatted, stdout=subprocess.PIPE)
        else:
            self.sendToServer(command)
            return ""

        return result.stdout.decode('utf-8')

    #Client Code

    bufferSize = 1024
    def ReceiveData(self, sock):
        while True:
            try:
                buf=1024
                data,addr = sock.recvfrom(self.bufferSize)
                data = data.decode('utf-8')
                if (self.file_prefix in data):
                    data = data[len(self.file_prefix):]
                    print ("Received File:",data.strip())
                    with open(data.strip(),'w+b') as f:
                        data,addr = sock.recvfrom(buf)
                        try:
                            while(data):
                                f.write(data)
                                sock.settimeout(2)
                                data,addr = sock.recvfrom(buf)
                        except socket.timeout:
                            pass
                        print ("File Downloaded")
                else:
                    print(data)
            except:
                pass

    def RunClient(self, serverIP):
        host = socket.gethostbyname(socket.gethostname())
        port = random.randint(6000,10000)
        print('Client IP->'+str(host)+' Port->'+str(port))
        server = (str(serverIP),5000)
        self.UDPClientSocket = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
        self.UDPClientSocket.bind((host,port))
        
        threading.Thread(target=self.ReceiveData,args=(self.UDPClientSocket,)).start()
        while True:        
            # shell simulation
            if (self.currentServer == None):
                prefix = ""
            else:
                prefix = f"({self.currentServer[0]}) "
            command = input(f"{green}{prefix}{os.getcwd()} $ {reset}")
            if command == 'quit':
                break
            output = self.RunCommand(command)
            print(output)       
            
        #UDPClientSocket.sendto(data.encode('utf-8'),server)
        self.UDPClientSocket.close()
        os._exit(1)
    #Client Code Ends Here

def main():
    client = Client()
    client.RunClient(sys.argv[1])

if __name__ == "__main__":
    main()