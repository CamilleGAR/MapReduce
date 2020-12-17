# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 13:30:27 2020

@author: camil
"""

import socket

SERVER_PORT = 5050
SERVER_IP = socket.gethostbyname(socket.gethostname()) #Normalement on met l'adresse ip du server
SERVER_ADDR = (SERVER_IP, SERVER_PORT)