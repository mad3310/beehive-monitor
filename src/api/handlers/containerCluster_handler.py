#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
Created on Sep 8, 2014

@author: root
'''
import logging

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


class GatherClusterMemeoyHandler(GatherClusterResourceHandler):

    def get(self, cluster):
        result = self.cluster_resoure(cluster, 'memory')
        self.finish({'data': result})


class GatherClusterCpuacctHandler(GatherClusterResourceHandler):

    def get(self, cluster):
        result = self.cluster_resoure(cluster, 'cpuacct')
        self.finish({'data': result})


class GatherClusterNetworkioHandler(GatherClusterResourceHandler):

    def get(self, cluster):
        result = self.cluster_resoure(cluster, 'networkio')
        self.finish({'data': result})


class GatherClusterDiskHandler(GatherClusterResourceHandler):

    def get(self, cluster):
        result = self.cluster_resoure(cluster, 'disk')
        self.finish({'data': result})


@require_basic_auth
class CheckContainerClusterStatusHandler(APIHandler):
    '''
    classdocs
    '''
    containerClusterOpers = ContainerCluster_Opers()

    # eg. curl --user root:root -X GET
    # http://10.154.156.150:8888/containerCluster/status/dh
    def get(self, containerClusterName):
        result = self.containerClusterOpers.check(containerClusterName)
        self.finish(result)


@require_basic_auth
class CheckClusterSyncHandler(APIHandler):

    container_cluster_opers = ContainerCluster_Opers()

    """
        webportal do info sync every 10 minutes,
        then interface will invoke this class
    """
    # eg. curl --user root:root -X GET
    # http://10.154.156.150:8888/containerCluster/sync

    def get(self):
        _clusterInfo = self.container_cluster_opers.sync()
        logging.info('data:%s' % str(_clusterInfo))
        result = {}
        result.setdefault('data', _clusterInfo)
        self.finish(result)
