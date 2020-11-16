# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 14:45:42 2020

@author: camil
"""


import socket

class Mapper:
    
    
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
            self.client.recv(2048).decode(self.FORMAT)
            self.client.settimeout(0)
            self.client.setblocking(True)
            
            print("Vous etes connectes")
            
            self.map_func()
            
        except socket.timeout:
            print('La connexion a ete refusee')
            
            
    def map_func(self):
        
       self.reducers = eval(self.client.recv(2048).decode(self.FORMAT))
       msg_length = int(self.client.recv(2048).decode(self.FORMAT))
       print(msg_length)
       text = self.client.recv(msg_length).decode(self.FORMAT)
       print(text)
       results = dict()
       next_word = ''
       for lettre in text:
           if (lettre == ' ' or lettre == '\n') and len(next_word) > 0:
               try : results[next_word]+=1
               except KeyError: results[next_word] = 1
               finally: next_word = ''
           else :
               next_word+=lettre
               
       print(results)
               
       self.client.send(b'DONE')
           
            
            
from collections import Counter
dict1 = {'a':1, 'b': 2}
dict2 = {'b':10, 'c': 11}
result = dict(Counter(dict1) + Counter(dict2))
        