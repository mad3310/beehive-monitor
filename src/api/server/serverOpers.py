#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
Created on Sep 10, 2014

@author: root
'''
import logging
import sys

from docker_letv.dockerOpers import Docker_Opers
from zk.zkOpers import Common_ZkOpers
from container.container_model import Container_Model
from container.containerOpers import Container_Opers
from common.abstractAsyncThread import Abstract_Async_Thread
from utils import getHostIp
from status.status_enum import Status
from resource_letv.serverResourceOpers import Server_Res_Opers


class Server_Opers(object):
    '''
    classdocs
    '''

    def host_exist(self, host_ip):
        zk_op = Common_ZkOpers()
        return zk_op.check_data_node_exist(host_ip)