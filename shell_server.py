#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 13:05:25 2021

@author: alex
"""
import socket
import threading
import queue
import sys
import os
import sqlite3
from sqlite3 import Error
import subprocess

class Server():
    bufferSize = 1024



    #Server Code
    def RecvData(self,sock,recvPackets):
        while True:
            data,addr = sock.recvfrom(self.bufferSize)
            recvPackets.put((data,addr))

    def __init__(self) -> None:
        self.private_clients = []
        self.shared_clients = []
        self.curr_client = 1
        self.file_prefix = "**_$$"

        # gets a string of a command to be run, runs it and returns the output
    def RunCommand(self, command_formatted):
        if (command_formatted[0] == "cd"):
            try:
                os.chdir(command_formatted[1])
            except Exception as e:
                return str(e)
            return ""

        result = subprocess.run(command_formatted, stdout=subprocess.PIPE)
        return result.stdout.decode('utf-8')

    def RunServer(self,host):
        #host = socket.gethostbyname(socket.gethostname())
        port = 5000
        print('Server hosting on IP-> '+str(host))
        self.UDPServerSocket = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((host,port))
        recvPackets = queue.Queue()

        print('Server Running...')

        threading.Thread(target=self.RecvData,args=(self.UDPServerSocket,recvPackets)).start()

        while True:
            while not recvPackets.empty():
                data,addr = recvPackets.get()
                data = data.decode('utf-8')
                print(f"{addr} requested: {data}")
                command_formatted = data.split()
                if (command_formatted[0] == "mount"):
                    if (command_formatted[1] == "private"):
                        self.private_clients.append(addr)
                    elif (command_formatted[1] == "shared"):
                        self.shared_clients.append((addr, f"Client {self.curr_client}"))
                        self.curr_client += 1
                elif (command_formatted[0] == "get"):
                    if (command_formatted[2] == "cwd"):
                        file_name_dest = f"{self.file_prefix} {os.getcwd()}/{command_formatted[1]}"
                    else:
                        file_name_dest=f"{self.file_prefix} {command_formatted[2]}" 
                    file_name_src=command_formatted[1]

                    self.UDPServerSocket.sendto(file_name_dest.encode('utf-8'),addr)

                    buf =1024
                    with open(file_name_src,"rb") as f:
                        file_data = f.read(buf)
                        while (file_data):
                            if(self.UDPServerSocket.sendto(file_data,addr)):
                                print ("sending ...")
                                file_data = f.read(buf)
                
                elif (addr in self.private_clients):
                    output = self.RunCommand(command_formatted)
                    self.UDPServerSocket.sendto(output.encode('utf-8'),addr) 
                elif (len(list(filter(lambda x: x[0] == addr, self.shared_clients))) != 0):
                    output = self.RunCommand(command_formatted)
                    self.UDPServerSocket.sendto(output.encode('utf-8'),addr)
                    for shared_client in self.shared_clients:
                        if (shared_client[0] != addr):

                            self.UDPServerSocket.sendto((f"{data}\n({shared_client[1]}) {output}").encode('utf-8'),shared_client[0])                                        

        UDPServerSocket.close()
        data_base.close()
    #Serevr Code Ends Here



if __name__ == '__main__':
    server = Server()
    server.RunServer(sys.argv[1])

 