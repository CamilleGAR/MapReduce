# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 22:00:22 2020

@author: camil
"""


class ResponseError(Exception):
    
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return self.message