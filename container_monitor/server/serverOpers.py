#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Sep 10, 2014

@author: root
'''

from zk.zkOpers import Common_ZkOpers


class Server_Opers(object):
    '''
    classdocs
    '''

    def host_exist(self, host_ip):
        zk_op = Common_ZkOpers()
        return zk_op.check_data_node_exist(host_ip)
