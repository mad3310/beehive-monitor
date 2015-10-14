#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
Created on Sep 8, 2014

@author: root
'''

from tornado_letv.tornado_basic_auth import require_basic_auth
from serverCluster.serverClusterOpers import ServerCluster_Opers
from base import APIHandler

@require_basic_auth
class UpdateServerClusterHandler(APIHandler):
    """
    update serverCluster 
    """
    
    serverCluster_opers = ServerCluster_Opers()
    
    # eg. curl --user root:root -X GET http://localhost:8888/serverCluster/update
    def get(self):
        
        self.serverCluster_opers.update()

        return_message = {}
        return_message.setdefault("message", "serverCluster update successful")
        self.finish(return_message)