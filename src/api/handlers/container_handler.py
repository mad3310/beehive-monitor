#!/usr/bin/env python
#-*- coding: utf-8 -*-

import logging

from base import APIHandler
from utils.exceptions import HTTPAPIError
from utils import get_current_time
from tornado_letv.tornado_basic_auth import require_basic_auth
from tornado.web import asynchronous
from container.containerOpers import Container_Opers
from status.status_enum import Status
from state.stateOpers import StateOpers


class GatherContainerMemeoyHandler(APIHandler):
    
    container_opers = Container_Opers()
    
    def get(self, container_name):

        exists = self.container_opers.check_container_exists(container_name)
        if not exists:
            massage = {}
            massage.setdefault("message", "container %s not exists" % container_name)
            self.finish(massage)
            return

        result = {}
        conl = StateOpers(container_name)
        memory_stat_item = conl.get_memory_stat_item()
        current_time = get_current_time()
        
        result.setdefault('memory', memory_stat_item)
        result.setdefault('time', current_time)
        result.setdefault('containerName', container_name)
        self.finish(result)


class GatherContainerCpuacctHandler(APIHandler):
    
    container_opers = Container_Opers()
    
    @asynchronous
    def get(self, container_name):

        exists = self.container_opers.check_container_exists(container_name)
        if not exists:
            massage = {}
            massage.setdefault("message", "container %s not exists" % container_name)
            self.finish(massage)
            return

        result = {}
        conl = StateOpers(container_name)
        cpuacct_stat_item = conl.get_cpuacct_stat_item()
        current_time = get_current_time()
        
        result.setdefault('cpuacct', cpuacct_stat_item)
        result.setdefault('time', current_time)
        result.setdefault('containerName', container_name)
        self.finish(result)


class GatherContainerNetworkioHandler(APIHandler):
    
    container_opers = Container_Opers()
    
    def get(self, container_name):

        exists = self.container_opers.check_container_exists(container_name)
        if not exists:
            massage = {}
            massage.setdefault("message", "container %s not exists" % container_name)
            self.finish(massage)
            return

        result = {}
        conl = StateOpers(container_name)
        network_io_item = conl.get_network_io()
        current_time = get_current_time()
        
        result.setdefault('networkio', network_io_item)
        result.setdefault('time', current_time)
        result.setdefault('containerName', container_name)
        self.finish(result)


class GatherContainerIopsHandler(APIHandler):
    pass


@require_basic_auth
class CheckContainerStatusHandler(APIHandler):
    '''
    classdocs
    '''
    container_opers = Container_Opers()
    
    @asynchronous
    def get(self, container_name):
        status = self.container_opers.check(container_name)
        self.finish(status)
