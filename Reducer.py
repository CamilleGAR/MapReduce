# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:30:20 2020

@author: camil
"""


import socket
import threading

from collections import Counter
dict1 = {'a':1, 'b': 2}
dict2 = {'b':10, 'c': 11}
result = dict(Counter(dict1) + Counter(dict2))

class Reducer:
    
    
    HEADER = 64
    PORT = 5050
    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "!DISCONNECT"
    CONNECTED_MESSAGE = "CONNECTED"
    SERVER = "192.168.1.26"
    ADDR = (SERVER, PORT)
    
    
    def __init__(self):
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.occurences = {}
        
        
        try : 
            self.client.connect(self.ADDR)
            self.client.settimeout(2)
            msg = self.client.recv(2048).decode(self.FORMAT)
            self.client.settimeout(0)
            self.client.setblocking(True)
            
            print("Vous etes connectes")
            
        except socket.timeout:
            print('La connexion a ete refusee')
            
        nb_mappers, serv_port = eval(self.client.recv(2048).decode(self.FORMAT))
        self.server.bind((self.SERVER, serv_port))
        self.server.listen()
        
        threads = []
        for m in range(nb_mappers) :
            conn, addr = self.server.accept()
            occurences = eval(conn.recv(2048).decode())
            self.occurences = dict(Counter(self.occurences) + Counter(occurences))
            print(occurences)
        
            # thread = threading.Thread(target= self.read_occurences, args = conn)
            # thread.start()
            # threads.append(thread)
            
        # for thread in threads :
        #     thread.join()
            
        print(self.occurences)
            
            
            
     
    def read_occurences(self, conn):
        
        occurences = eval(conn.recv(2048).decode())
        self.occurences = dict(Counter(self.occurences) + Counter(occurences))
        print(occurences)
        
        
        