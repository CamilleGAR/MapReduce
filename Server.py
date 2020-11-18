# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 15:27:14 2020

@author: camil
"""

import socket
import threading
import time

import ctypes 

                       
class Text:
    
    """Classe contenant le texte a traiter"""
    
    def __init__(self, source, reference):
        """Veuillez indiquer la source pour savoir comment traiter l'information"""
        
        if source == 'web' :
            pass
        
        elif source == 'txt' :
            pass
        
        elif source == 'str' :
            self.text = reference
            
        else :
            raise BaseException("La source doit être web/txt/str")
            
            
    def set_subdivision(self, nb_subd):
        """Divise le texte en n parties égales"""
        
        self.nb_subd = nb_subd
        self.subdivisions = []
        for subd in self.generateur_subdivisions(nb_subd):
            self.subdivisions.append(subd)
            
    def generateur_subdivisions(self, nb_sub):
        """Generateur qui renvoie les subdvisions. Le texte est coupe entre deux mots"""
        
        nb_char = len(self.text)
        pas = nb_char // nb_sub
        index_char = 0
        for i in range(nb_sub):
            debut = index_char
            index_char += pas
            while index_char < nb_char and self.text[index_char] != " ":
                index_char += 1
            yield self.text[debut:index_char]
        
    
    def __getitem__(self, index):
        
        try :
            return self.subdivisions[index]
        
        except :
            print("Les subdivisions n'ont pas ete creees")
            


class Client:
    
    """Classe conservant les informations des sockets clients"""
    
    def __init__(self, conn, addr):
        
        self.client = {'conn' : conn, 'addr' : addr}
        
    def __getitem__(self, item) :
        
        return self.client[item]
    

class Server:
    
    HEADER = 64
    PORT = 5050
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR = (SERVER, PORT)
    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "DISCONNECT"
    NOT_CONNECTED_MESSAGE = "NOT_CONNECTED"
        
    
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)
        self.mappers, self.reducers = set(), list()
        
        self.server.listen()
        self.server.settimeout(0.1)


    def _make_connexions_reducers(self):
        """Connetion aux reducers. Ne pas appeler directement"""
        
        #On vide les tentatives de connexions envoyees avant        
        vider = True
        while vider:
            try :
                conn, addr = self.server.accept()
                conn.close()
                print(conn,addr)
            except socket.timeout:
               vider = False
                      
        #Attente de connexions 
        print("nombre de connexions : {}".format(len(self.reducers)))               
        while self.waiting_for_reducers :  
            try :
                conn, addr = self.server.accept()
            except socket.timeout:
                continue
            if self.waiting_for_reducers : 
                self.reducers.append(Client(conn, addr))
                conn.send("CONNECTED".encode(self.FORMAT))
                print("nombre de connexions : {}".format(len(self.reducers)))
            else :
                conn.close()

                
                
                        
    def _make_connexions_mappers(self):
        """Connetion aux mappers. Ne pas appeler directement"""
        
        #On vide les tentatives de connexions envoyees avant
        vider = True
        while vider:
            try :
                conn, addr = self.server.accept()
                conn.close()
            except socket.timeout:
                vider = False
                     
        #Attente de connexions  
        print("nombre de connexions : {}".format(len(self.mappers)))
        while self.waiting_for_mappers :       
            try :
                conn, addr = self.server.accept()
            except socket.timeout:
                continue
            if self.waiting_for_mappers : 
                self.mappers.add(Client(conn, addr))              
                conn.send("CONNECTED".encode(self.FORMAT))
                print("nombre de connexions : {}".format(len(self.mappers)))
            else :
                conn.close()
    
    

    def make_connexions_reducers(self):
        """appel a _make_connexions_reducers. Vous pouvez stopper l'attente de reducers"""

        self.waiting_for_reducers = True
        
        thread = threading.Thread(target=self._make_connexions_reducers)
        thread.start()
        
        input("Appuyez pour ne plus attendre de reducers")
        
        self.waiting_for_reducers = False
        
        
    def make_connexions_mappers(self):
        """appel a _make_connexions_mappers. Vous pouvez stopper l'attente de mappers"""
        
        self.waiting_for_mappers = True
        
        thread = threading.Thread(target=self._make_connexions_mappers)
        thread.start()
        
        input("Appuyez pour ne plus attendre de mappers")
        
        self.waiting_for_mappers = False        
        
        
    def make_connexions(self):
        """Permet de setup toutes les connexions des le debut. Pour n'ajouter que des 
        reducers ou que des mappers, appeller la fonction prevue a cet effet"""
        
        self.make_connexions_reducers()
        self.make_connexions_mappers()
    
        

    
    def send_text_to_mappers(self, client, text):
        """Envoie le texte au client."""
        
        try :
            msg = text.encode(self.FORMAT)
            client['conn'].send(repr(list([abs(hash(r))%100000 for r in self.reducers])).encode()) #genere des adresses pour les reducers
            msg_length = len(msg)
            client['conn'].send(str(msg_length).encode(self.FORMAT))
            time.sleep(1)
            client['conn'].send(text.encode(self.FORMAT))
            client['conn'].settimeout(5)
            client['conn'].recv(2048).decode(self.FORMAT)
            client['conn'].settimeout(0.1)
        
        except socket.timeout :
            print('Un client ne repond pas. Il est retire de la liste')
            self.mappers.remove(client)
 
    def receive_dict_from_reducers(self, client):
        """Recoit les resultats"""
        
        try:
            client['conn'].settimeout(5)
            result = client['conn'].recv(2048).decode(self.FORMAT)
            client['conn'].settimeout(0.1)
            
        except socket.timeout :
            pass
        
        print(result)
        
    def setup_reducer(self, client, nb_mappers):
        client['conn'].send(str((nb_mappers, abs(hash(client))%100000)).encode())
        try :
            client['conn'].settimeout(5)
            client['conn'].recv(2048).decode(self.FORMAT)
            client['conn'].settimeout(0.1)
        except socket.timeout:
            pass
        
    def map_reduce(self, text_object):
        """Decoupe le texte et l'envoie a chaque mapper.
        Attend la reponse de chaque reducer."""
        
        nb_mappers = len(self.mappers)
        text_object.set_subdivision(nb_mappers)
        
        threads = list()
        for index, mapper in enumerate(self.mappers) :
            thread = threading.Thread(target=self.send_text_to_mappers, args=(mapper, text_object[index]))
            thread.start()
            threads.append(thread)
            
        #On attend que toutes les actions map soient faites
        for thread in threads:
            thread.join()
            
        print('OUIIII')
            
        #On setup les reducers
        for reducer in self.reducers:
            thread = threading.Thread(target = self.setup_reducer(reducer, len(self.mappers)))
            thread.start()
            threads.append(thread)
            
        for thread in threads:
            thread.join()
            
        #On donne le signal pour envoyer les resultats aux reducers
        for mapper in self.mappers:
            mapper['conn'].send(b"GO")
                       
            
            thread = threading.Thread(target = self.receive_dict_from_reducers, args=(reducer))
            

            
        
    
    
    def close_connexions(self):
        """Ferme tous les sockets"""
        
        for mapper in self.mappers :
            mapper['conn'].close()
        
        

#conn.send(repr(set([r['addr'] for r in self.reducers])).encode())        
        