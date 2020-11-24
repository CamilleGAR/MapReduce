# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 14:45:42 2020

@author: camil
"""


import socket
import threading
from Constantes import *
from Settings import *
from ResponseError import ResponseError
import hashlib

class Mapper:
    
    def __init__(self):
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        
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
            
            #On commence la tache map
            while 1:
                self.map_func()
            
        except socket.timeout:
            print('Pas de reponse : La connexion a ete refusee')
            
        except ResponseError as error_msg:
            print(error_msg, ': La connexion a ete refusee')
     
        
    def compter(self, text):
        """Compte le nombre d'apparition de chaque mot du texte"""
        
        results = dict()
        next_word = ''
        for lettre in text:
            if (lettre in PONCTUATION) and len(next_word) > 0:
                try : results[next_word]+=1
                except KeyError: results[next_word] = 1
                finally: next_word = ''
            elif lettre in ALPHABET :
                next_word+=lettre
                
        return results
     
        
    def send_dict_to_reducer(self, port_reducer, results):
        """Cree un socket qui se connecte au reducer.
        Lui envoie ensuite les resultats mis en parametre"""
        
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((REDUCER_IP, port_reducer))
        client.send(repr(results).encode())
        print('\nresultat envoyé au reducer [port : {}], :'.format(port_reducer), repr(results).encode())


    def map_func(self):
        
       #On se met en attente jusqu'au prochain message du server
       self.client.setblocking(True)
       
       #Liste reducers avec lesquels travailler
       self.reducers = eval(self.client.recv(2048).decode(FORMAT))
       print('Reducers :', self.reducers)
       
       #On recupere la taille du texte qui peut etre long
       msg_length = int(self.client.recv(2048).decode(FORMAT))
       print('le texte est de taille :', msg_length)
       
       #On confirme la reception
       self.client.send(CONFIRM_RECEPTION_MESSAGE.encode())
       
       #Reception du message
       text = self.client.recv(msg_length).decode(FORMAT)
       print('Texte :', text)
       
       results = self.compter(text)
                      
       #On setup le dictionnaire des reducers
       nb_reducers = len(self.reducers)
       destination_occurences = dict()
       for reducer in self.reducers :
           destination_occurences[reducer] = {}
       
       #On remplie le dictionnaires avec les mots et les occurences
       #Les mots sont repartis sur les differents reducers avec une fonction de hashage
       for word, occurence in results.items() :
           index = int(hashlib.md5(word.encode()).hexdigest(),16)%nb_reducers #Sert a la repartition des mots
           destination_occurences[self.reducers[index]][word] = occurence
          
       self.client.send(CONFIRMATION_MAP.encode())  
       
       #Attente du signal avant de transmettre les resultats aux reducers
       if self.client.recv(2048).decode(FORMAT) != TRANSMIT_TO_REDUCERS_MESSAGE :
           raise ResponseError('Le message recu n\'est pas celui attendu')
       
       for reducer in self.reducers:
           thread = threading.Thread(target=self.send_dict_to_reducer, args=(reducer, destination_occurences[reducer]))
           thread.start()
           
            
            

        