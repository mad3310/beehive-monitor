#-*- coding: utf-8 -*-
from abc import abstractmethod
'''
Created on 2013-7-21

@author: asus
'''

class Abstract_Container_Opers(object):
    
    @abstractmethod
    def create(self, arg_dict):
        raise NotImplementedError, "Cannot call abstract method"
    
    @abstractmethod
    def start(self, arg_dict):
        raise NotImplementedError, "Cannot call abstract method"

    @abstractmethod
    def stop(self, arg_dict):
        raise NotImplementedError, "Cannot call abstract method"
    
    @abstractmethod
    def destroy(self, arg_dict):
        raise NotImplementedError, "Cannot call abstract method"
    
