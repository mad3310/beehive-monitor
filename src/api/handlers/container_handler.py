#!/usr/bin/env python
#-*- coding: utf-8 -*-

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


class GatherContainerMemeoyHandler(BaseContainerHandler):

    def get(self, container_name):
        self.check_container_name(container_name)

        result = self.get_container_resource(container_name, 'memory')
        self.finish(result)


class GatherContainerCpuacctHandler(BaseContainerHandler):

    container_opers = Container_Opers()

    def get(self, container_name):
        self.check_container_name(container_name)

        result = self.get_container_resource(container_name, 'cpuacct')
        self.finish(result)


class GatherContainerNetworkioHandler(BaseContainerHandler):

    def get(self, container_name):
        self.check_container_name(container_name)

        result = self.get_container_resource(container_name, 'networkio')
        self.finish(result)


class GatherContainerDiskIopsHandler(BaseContainerHandler):

    def get(self, container_name):
        self.check_container_name(container_name)

        result = self.get_container_resource(container_name, 'diskiops')
        self.finish(result)


class GatherContainerDiskLoadHandler(BaseContainerHandler):

    def get(self, container_name):
        self.check_container_name(container_name)

        result = self.get_container_resource(container_name, 'diskload')
        self.finish(result)


@require_basic_auth
class CheckContainerStatusHandler(BaseContainerHandler):
    '''
    classdocs
    '''
    container_opers = Container_Opers()

    def get(self, container_name):
        status = self.container_opers.check(container_name)
        self.finish(status)
