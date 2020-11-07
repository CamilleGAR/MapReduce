# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 15:27:14 2020

@author: camil
"""

import socket
import threading
import time


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
    DISCONNECT_MESSAGE = "!DISCONNECT"
        
    
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)
        self.clients = set()
        
        
    def _make_connexions(self):
        """Connetion aux clients. Ne pas appeler directement"""
        
        self.server.listen()
        while self.waiting_for_clients :
            
            print("nombre de connexions : {}".format(len(self.clients)))
            conn, addr = self.server.accept()
            if self.waiting_for_clients : self.clients.add(Client(conn, addr))
            
            
    def make_connexions(self):
        """Appel à _make_connexions. Vous pouvez stopper l'attente de clients"""
        
        self.waiting_for_clients = True
        
        thread = threading.Thread(target=self._make_connexions)
        thread.start()
        
        input("Appuyez pour ne plus attendre de clients")
        self.waiting_for_clients = False
        
    
    def send_text(self, client, text):
        """Envoie le texte au client. Recoie le dictionnaire des occurences"""
        
        try :
            client['conn'].send(text.encode(self.FORMAT))
            client['conn'].settimeout(5)
            client['conn'].receive(2048).decode(self.FORMAT)
            client['conn'].settimeout(None)
        
        except Exception :
            pass
        
        
    def repartir(self, text_object):
        """Decoupe le texte et l'envoie a chaque client"""
        
        nb_clients = len(self.clients)
        text_object.set_subdivision(nb_clients)
        
        for index, client in enumerate(self.clients) :
            self.send_text(client, text_object[index])
    
    
    def close_connexions(self):
        """Ferme tous les sockets"""
        
        for client in self.clients :
            client['conn'].close()
        
        

        
        