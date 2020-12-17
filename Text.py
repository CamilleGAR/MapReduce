# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 13:28:45 2020

@author: camil
"""
from tika import parser

class Text:
    
    """Classe contenant le texte a traiter"""
    
    def __init__(self, source, reference):
        """Veuillez indiquer la source pour savoir comment traiter l'information"""
        
        if source == 'txt' :
            with open(reference, 'r') as file:
                self.text = file.read()
        
        elif source == 'str' :
            self.text = reference
            
        else :
            raise BaseException("La source doit être str/txt")
            
            
    def set_subdivision(self, nb_subd):
        """Divise le texte en n parties égales"""
        
        self.nb_subd = nb_subd
        self.subdivisions = []
        for subd in self.generateur_subdivisions(nb_subd):
            #On ajoute un point pour faciliter le traitement du texte
            self.subdivisions.append(subd+'.')
            
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
            
    def __len__(self):
        return len(self.text)
            