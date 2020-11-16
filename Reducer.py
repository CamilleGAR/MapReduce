# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:30:20 2020

@author: camil
"""


import socket

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
        
        try :   
            self.client.connect(self.ADDR)
            
            self.client.settimeout(2)
            msg = self.client.recv(2048).decode(self.FORMAT)
            self.client.settimeout(0)
            
            print("Vous etes connectes")
            
            self.read_text()
            
        except socket.timeout:
            print('La connexion a ete refusee')
            
            
    def read_text(self):
        
        #self.client.recv(self.HEADER).decode(self.FORMAT)
        pass
        