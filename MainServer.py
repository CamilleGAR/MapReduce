import socket 
import threading
from Server import Server

server = Server()

# def start():
#     server.make_connexions()
    
    

if __name__ == "main" :
    
    server.make_connexions()
    server.send_all_texts()
    server.close_connexions()