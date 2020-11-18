# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 14:45:42 2020

@author: camil
"""


import socket
import threading

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
            
     
    def send_dict_to_reducer(self, reducer, results):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.SERVER, reducer))
        client.send(repr(results).encode())
        print(repr(results).encode())

    def map_func(self):
        
       self.reducers = eval(self.client.recv(2048).decode(self.FORMAT))
       msg_length = int(self.client.recv(2048).decode(self.FORMAT))
       print(msg_length)
       text = self.client.recv(msg_length).decode(self.FORMAT)
       print(text)
       results = dict()
       next_word = ''
       ponctuation = [' ', '\n', '.', '!', ',', '?']
       for lettre in text:
           if (lettre in ponctuation) and len(next_word) > 0:
               try : results[next_word]+=1
               except KeyError: results[next_word] = 1
               finally: next_word = ''
           elif lettre not in ponctuation :
               next_word+=lettre
               
       print(results)
                      
       nb_reducers = len(self.reducers)
       destination_occurences = dict()
       for reducer in self.reducers :
           destination_occurences[reducer] = {}
       
       for word, occurence in results.items() :
           index = hash(word)%nb_reducers #Sert a la repartition des mots
           destination_occurences[self.reducers[index]][word] = occurence
          
       self.client.send(b'DONE')       
       self.client.recv(2048) #Attente du GO pour synchroniser tous les mappers
       
       for reducer in self.reducers:
           thread = threading.Thread(target=self.send_dict_to_reducer, args=(reducer, destination_occurences[reducer]))
           thread.start()
           
            
            

        