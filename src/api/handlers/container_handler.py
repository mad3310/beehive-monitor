#!/usr/bin/env python
#-*- coding: utf-8 -*-

from tornado.web import asynchronous
from tornado.gen import engine
from utils.decorators import run_on_executor, run_callback

from base import APIHandler
from utils import get_current_time
from tornado_letv.tornado_basic_auth import require_basic_auth
from container.containerOpers import Container_Opers
from zk.zkOpers import Requests_ZkOpers
from utils import get_containerClusterName_from_containerName
from utils.exceptions import HTTPAPIError


class BaseContainerHandler(APIHandler):

    container_opers = Container_Opers()

    def check_container_name(self, container_name):
        exists = self.container_opers.check_container_exists(container_name)
        if not exists:
            error_message = 'container %s not exist, please check your container name' % container_name
            raise HTTPAPIError(status_code=417, error_detail=error_message,
                               notification="direct",
                               log_message=error_message,
                               response=error_message)

    def get_container_resource(self, container_name, resource_type):
        zk_opers = Requests_ZkOpers()

        result = {}
        cluster_name = get_containerClusterName_from_containerName(
            container_name)
        node_name = self.container_opers.get_container_node_from_container_name(
            cluster_name, container_name)
        resource_value = zk_opers.retrieve_container_resource(
            cluster_name, node_name, resource_type)
        current_time = get_current_time()

        result.setdefault(resource_type, resource_value)
        result.setdefault('time', current_time)
        result.setdefault('containerName', container_name)
        return result

    @asynchronous
    @engine
    def get(self, container_name, resource_type):
        result = yield self.do(container_name, resource_type)
        self.handle_exception(result)
        self.finish(result)

    @run_on_executor()
    @run_callback
    def do(self, container_name, resource_type):
        self.check_container_name(container_name)
        return self.get_container_resource(container_name, resource_type)


class GatherContainerMemeoyHandler(BaseContainerHandler):

    def get(self, container_name):
        super(GatherContainerMemeoyHandler, self).get(container_name, 'memory')


class GatherContainerCpuacctHandler(BaseContainerHandler):

    def get(self, container_name):
        super(GatherContainerCpuacctHandler, self).get(container_name, 'cpuacct')


class GatherContainerNetworkioHandler(BaseContainerHandler):

    def get(self, container_name):
        super(GatherContainerNetworkioHandler, self).get(container_name, 'networkio')


class GatherContainerDiskIopsHandler(BaseContainerHandler):

    def get(self, container_name):
        super(GatherContainerDiskIopsHandler, self).get(container_name, 'diskiops')


class GatherContainerDiskLoadHandler(BaseContainerHandler):
    
    def get(self, container_name):
        super(GatherContainerDiskLoadHandler, self).get(container_name, 'diskload')


@require_basic_auth
class CheckContainerStatusHandler(BaseContainerHandler):
    '''
    classdocs
    '''
    container_opers = Container_Opers()

    @asynchronous
    @engine
    def get(self, container_name):
        result = yield self.do(container_name)
        self.finish(result)

    @run_on_executor()
    @run_callback
    def do(self, container_name):
        return self.container_opers.check(container_name)
