# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 15:27:14 2020

@author: camil
"""

import socket
import threading
import time
from Text import Text
from ServerSettings import *
from Constantes import *
from ResponseError import ResponseError
import ctypes 
from collections import Counter

def join_threads(thread_list):
    for thread in thread_list :
        thread.join()
        
class Server:
    
    def __init__(self):
        #Parametrage du server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER_ADDR)
        self.server.listen()

        #Definition des attributs
        self.mappers, self.reducers = list(), list()
        self.waiting_for_reducers, self.waiting_for_mappers = False, False
        self.lock = threading.RLock()
        self.text_failed = ''
        self.lock_failed = threading.RLock()
        self.reducers_failed = set()
        self.resultats = {}
        
        #initialisation des clients
        self.add_mappers()
        self.add_reducers()
        
    def add_mappers(self):
        """Permet d'ajouter des mappers à notre liste"""
        self.make_connexions(self.mappers, client = "mapper")
        
    def add_reducers(self):
        """Permet d'ajouter des reducers à notre liste"""
        self.make_connexions(self.reducers, client = "reducer")
        
    def clean_mappers(self):
        """Vide la liste des mappers"""
        self.mappers = list()
        
    def clean_reducers(self):
        """Vide la liste des reducers"""
        self.reducers = list()
        
    def generate_port(self, conn):
        """Genere un port qu'on imposera à un reducer.
        On l'envoie aux reducers et aux mappers pour qu'ils puissent communiquer"""
        
        return abs(hash(conn))%65000
        
        
    def empty_waiting_list(self):
        """Vide les demandes de connexions antérieures. 
        On ne peut se connecter qu'apres cette opération"""
        
        #On enleve le blocking pour vider la liste et sortir de la boucle
        self.server.setblocking(False)
        
        vider = True     
        while vider:
            try :
                conn, addr = self.server.accept()
                conn.close()
                print(conn,addr)
            except BlockingIOError:
               vider = False
               
        self.server.setblocking(True)
        
        
    def _make_connexions(self, filled_list):
        """Connexion aux clients. Ne pas appeler directement"""
        
        #On vide les demandes de connexions antérieures.
        self.empty_waiting_list()
        
        #Attente de connexions 
        print("nombre de connexions : {}".format(len(filled_list)))     

        #Timeout permettant de sortir des requetes server.accept()
        self.server.settimeout(0.1)
        
        while waiting_condition :
            
            #On recupere les demandes de connexions
            try :
                conn, addr = self.server.accept()
            except socket.timeout:
                continue
            
            #On les ajoute à la liste adequate
            if waiting_condition : 
                filled_list.append(conn)
                conn.send(CONNECTED_MESSAGE.encode(FORMAT))
                print("nombre de connexions : {}".format(len(filled_list)))
            else :
                conn.close()
        
        self.server.settimeout(0)
        
        
    def make_connexions(self, filled_list, client = "client"):
        """appel a _make_connexions. Vous pouvez stopper l'attente de clients"""
        
        #Variable permettant d'arreter la recherche de clients
        global waiting_condition 
        waiting_condition = True
        
        #thread qui accepte les clients
        thread = threading.Thread(target=self._make_connexions, args = [filled_list])
        thread.start()
        
        input("Appuyez pour ne plus attendre de {}".format(client))
        
        waiting_condition = False
        
        #On attend que le thread soit clot
        thread.join()
        
        
    def send_text_to_mappers(self, conn, text):
        """Envoie le texte au client."""
        
        try : 
            
            conn.setblocking(True)
            
            #On envoie la liste des addr des reducers aux mappers.
            conn.send(repr(list((r.getpeername()[0], self.generate_port(r)) for r in self.reducers)).encode()) 
    
            #Envoi du message. On previent d'abord le mapper de la longueur du message.
            msg = text.encode(FORMAT)
            msg_length = str(len(msg)).encode(FORMAT)
            
            #Envoi de la longueur du message a recevoir
            conn.send(msg_length)
            
            #Attente de confirmation afin que le mapper ne recoive pas les deux message concatenes
            if conn.recv(2048).decode(FORMAT) != CONFIRM_RECEPTION_MESSAGE :
                raise ResponseError('Le message recu n\'est pas celui attendu')
                
            #Envoie du message
            conn.send(msg)
            
            #On attend la confirmation du travail du mapper. Sinon, on considere qu'il a echoue.
            conn.settimeout(5)
            if conn.recv(2048).decode(FORMAT) != CONFIRMATION_MAP :
                raise ResponseError('Le message recu n\'est pas celui attendu')
            conn.settimeout(0)
        
        except socket.timeout:
            print('\nUn mapper ne repond pas. Il est retire de la liste\n')
            self.mappers.remove(conn)
            with self.lock_failed:
                self.text_failed += text
            
        except ResponseError as error_msg:
            print('\n',error_msg, ': Le mapper est retire de la liste\n')
            self.mappers.remove(conn)
            with self.lock_failed:
                self.text_failed += text
                
        except ConnectionResetError:
            print('\nUn mapper est deconnecte. Il est retire de la liste\n')
            self.mappers.remove(conn)
            with self.lock_failed:
                self.text_failed += text
                
    
    def setup_reducer(self, conn, nb_mappers):
        """Envoie aux reducers le nombre de mappers et le port qu'il doit prendre"""
        
        #Transmet au reducer le nombre de connexions qu'il doit accepter et quel port il doit prendre.
        try :
            conn.send(str((nb_mappers, self.generate_port(conn))).encode())
        
        #Attente de confirmation
            conn.settimeout(2)
            conn.recv(2048).decode(FORMAT)
            conn.settimeout(0)
            
        except Exception:
            self.reducers_failed.add(conn)
            
            
    def receive_dict_from_reducers(self, conn):
        """Recoit les resultats"""
        
        try:
            conn.settimeout(5)
            occurences = eval(conn.recv(2048).decode(FORMAT))
            conn.settimeout(0)
            
            with self.lock :
                self.resultats = dict(Counter(self.resultats) + Counter(occurences))
            
        except Exception :
            self.reducers_failed.add(conn)
            
            
    def map_reduce(self, text_object, reset_results = True):
        """Decoupe le texte et l'envoie a chaque mapper.
        Attend la reponse de chaque reducer."""
           

        #On reinitialise les resultats
        self.reducers_failed = set()
        self.text_failed = ''
        if reset_results == True :
            self.resultats = {}
                
        #Nombre de mappers disponibles
        nb_mappers = len(self.mappers)
            
        #On divise le texte
        text_object.set_subdivision(nb_mappers)
            
        print('On envoie un morceau du texte à chaque mapper')
        #On envoie chaque morceau de texte à son mapper
        threads = list()
        for index, mapper in enumerate(self.mappers) :
            thread = threading.Thread(target=self.send_text_to_mappers, args=(mapper, text_object[index]))
            thread.start()
            threads.append(thread)
                
        #On attend que toutes les actions map soient faites
        join_threads(threads)
                
        print('Les mappers ont fini leur tache')
        print('On envoie aux reducers combien de mapper ils doivent accepter et quels ports ils doivent prendre')
        #On setup les reducers
        threads = list()
        for conn in self.reducers:
            thread = threading.Thread(target = self.setup_reducer(conn, len(self.mappers)))
            thread.start()
            threads.append(thread)
                
        #On attend que tous les reducers soient operationnels
        join_threads(threads)
                
        print('Les mappers transmettent leurs resultats aux reducers')
        #On dit aux mappers de transmettre leurs resultats aux reducers
        for conn in self.mappers:
            conn.send(TRANSMIT_TO_REDUCERS_MESSAGE.encode())
                           
        #On attend les resultats des reducers
        threads = list()
        for conn in self.reducers:
            thread = threading.Thread(target = self.receive_dict_from_reducers, args=[conn])
            thread.start()
            threads.append(thread)
                
        #On attend d'avoir recu tous les resultats
        join_threads(threads)
            
        #On relance les textes manquants a cause des mappers qui ont crash
        if self.text_failed != '':
            print('\non renvoie aux mappers restants les textes ayant echoues\n')
            self.map_reduce(Text('str', self.text_failed), reset_results = False)
                
        if self.reducers_failed != set() :
            print('\nUn ou plusieurs reducers n\'ont pas repondu, on relance sans ces reducers\n')
            for conn in self.reducers_failed :
                self.reducers.remove(conn)
            self.map_reduce(text_object)
                
        return self.resultats
            
            
    def __call__(self, text_object):
            """Simplifie l'appel à map_reduce()"""
            
            return self.map_reduce(text_object)