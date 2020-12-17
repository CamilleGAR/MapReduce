
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:30:20 2020

@author: camil
"""


import socket
import threading
from ResponseError import ResponseError
from collections import Counter

class Reducer:
        
    def __init__(self):
        
        self.REDUCER_IP = socket.gethostbyname(socket.gethostname())
        
        #Socket se connectant au Server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        
        #Socket recevant les connexions des mappers
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #Initialisation des attributs
        self.occurences = {}
        self.lock = threading.RLock()
        
        try : 
            
            #Connexion au Server
            self.client.connect(SERVER_ADDR)
            
            #Si on ne recoit aucune confirmation, on considere ca comme un refus
            self.client.settimeout(2)
            
            #On verifie qu'on recoit bien le bon message de confirmation
            if self.client.recv(2048).decode(FORMAT) != CONNECTED_MESSAGE :
                raise ResponseError('Le message recu n\'est pas celui attendu')
                
            self.client.settimeout(0)
            
            #Aucune erreur ne s'est produite, on est connecte.
            print("Vous etes connectes")
            
            #On commence la tache reduce
            while 1:
                self.reduce_func()
            
        except socket.timeout:
            print('La connexion a ete refusee')
        
        
    def read_occurences(self, conn):
        """Recois le dictionnaire du mapper. Met a jour self.occurence"""
        
        #Recupere les resultats du mapper
        occurences = eval(conn.recv(2048).decode())
        
        #On s'assure de ne pas entrer en conflit avec les autres threads
        with self.lock :
            self.occurences = dict(Counter(self.occurences) + Counter(occurences))
        
        
    def reduce_func(self):
        
        #reinitialisation
        self.occurences = {}
            
        #On se met en attente jusqu'au prochain message du server
        self.client.setblocking(True)
            
        #Le server nous envoie le nombre de mappers ainsi que le port qui nous est imposee
        nb_mappers, my_port = eval(self.client.recv(2048).decode(FORMAT)) 
        self.client.send(b'OK') #Confirmation
            
        #Setting du socket server
        try :
            self.server.bind((self.REDUCER_IP, my_port))
            self.server.listen()
        except OSError:
            pass
            
        threads = []
        for m in range(nb_mappers) :
            conn, addr = self.server.accept()
            thread = threading.Thread(target = self.read_occurences, args = [conn])
            thread.start()
            threads.append(thread)
            
        for thread in threads :
            thread.join()
            
        self.client.send(repr(self.occurences).encode())
        print('Dictionnaire envoye :', self.occurences)
                
        
                
                
                
     

        
        