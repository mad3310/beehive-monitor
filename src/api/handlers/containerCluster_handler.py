#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
Created on Sep 8, 2014

@author: root
'''

from tornado.web import asynchronous
from tornado.gen import engine
from utils.decorators import run_on_executor, run_callback

from tornado_letv.tornado_basic_auth import require_basic_auth
from base import APIHandler
from utils.exceptions import HTTPAPIError
from container.containerOpers import Container_Opers
from containerCluster.containerClusterOpers import ContainerCluster_Opers
from zk.zkOpers import Requests_ZkOpers


class GatherClusterResourceHandler(APIHandler):
    '''
        the result is webportal need, return to webportal
    '''

    container_opers = Container_Opers()

    def cluster_resoure(self, cluster, resource_type):
        zkOper = Requests_ZkOpers()

        exists = zkOper.check_containerCluster_exists(cluster)
        if not exists:
            error_message = 'container cluster %s not exist, please check your cluster name' % cluster
            raise HTTPAPIError(status_code=417, error_detail=error_message,
                               notification="direct",
                               log_message=error_message,
                               response=error_message)

        container_node_list = zkOper.retrieve_container_list(cluster)
        result = []
        
        for container_node in container_node_list:
            resource = {}
            resource_value = zkOper.retrieve_container_resource(cluster, container_node, resource_type)
            host_ip = self.container_opers.get_host_ip_from_zk(cluster, container_node)
            container_name = self.container_opers.get_container_name_from_zk(cluster, container_node)
            resource.setdefault('value', resource_value)
            resource.setdefault('hostIp', host_ip)
            resource.setdefault('containerName', container_name)
            result.append(resource)

        return result

    @asynchronous
    @engine
    def get(self, cluster, resource_type):
        result = yield self.do(cluster, resource_type)
        self.finish({'data': result})

    @run_on_executor()
    @run_callback
    def do(self, cluster, resource_type):
        return self.cluster_resoure(cluster, resource_type)


class GatherClusterMemeoyHandler(GatherClusterResourceHandler):

    def get(self, cluster):
        super(GatherClusterMemeoyHandler, self).get(cluster, 'memory')


class GatherClusterCpuacctHandler(GatherClusterResourceHandler):

    def get(self, cluster):
        super(GatherClusterCpuacctHandler, self).get(cluster, 'cpuacct')


class GatherClusterNetworkioHandler(GatherClusterResourceHandler):

    def get(self, cluster):
        super(GatherClusterNetworkioHandler, self).get(cluster, 'networkio')


class GatherClusterDiskiopsHandler(GatherClusterResourceHandler):

    def get(self, cluster):
        super(GatherClusterDiskiopsHandler, self).get(cluster, 'diskiops')


class GatherClusterDiskHandler(GatherClusterResourceHandler):

    def get(self, cluster):
        super(GatherClusterDiskHandler, self).get(cluster, 'disk')


@require_basic_auth
class CheckContainerClusterStatusHandler(APIHandler):
    '''
    classdocs
    '''
    containerClusterOpers = ContainerCluster_Opers()
    
    @asynchronous
    @engine
    def get(self, cluster):
        result = yield self.do(cluster)
        self.finish(result)

    @run_on_executor()
    @run_callback
    def do(self, cluster):
        return self.containerClusterOpers.check(cluster)


@require_basic_auth
class CheckClusterSyncHandler(APIHandler):
    """
        webportal do info sync every 10 minutes,
        then interface will invoke this class
    """

    container_cluster_opers = ContainerCluster_Opers()
    
    @asynchronous
    @engine
    def get(self):
        """ # eg. curl --user root:root -X GET
            # http://10.154.156.150:6666/containerCluster/sync
        """
        
        result = yield self.do()
        ret = {}
        ret.setdefault('data', result)
        self.finish(ret)

    @run_on_executor()
    @run_callback
    def do(self):
        return self.container_cluster_opers.sync()


