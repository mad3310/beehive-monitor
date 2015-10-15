#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
Created on Sep 8, 2014

@author: root
'''

import logging
import sys

from status.status_enum import Status
from utils.exceptions import UserVisiableException
from container.container_model import Container_Model
from zk.zkOpers import Requests_ZkOpers
from componentProxy.componentContainerClusterValidator import ComponentContainerClusterValidator
from utils.threading_exception_queue import Threading_Exception_Queue


class ContainerCluster_Opers(object):

    component_container_cluster_validator = ComponentContainerClusterValidator()
    threading_exception_queue = Threading_Exception_Queue()

    def __init__(self):
        super(ContainerCluster_Opers, self).__init__()

    def check(self, containerClusterName):
        zkOper = Requests_ZkOpers()
        exists = zkOper.check_containerCluster_exists(containerClusterName)
        if not exists:
            raise UserVisiableException(
                'containerCluster %s not existed' % containerClusterName)

        cluster_status = self.component_container_cluster_validator.container_cluster_status_validator(
            containerClusterName)
        return cluster_status

    def sync(self):
        clusters_zk_info = self.get_clusters_zk()
        
        clusters = []
        for cluster_name, nodes in clusters_zk_info.items():
            try:
                cluster, nodeInfo = {}, []
                logging.info('sync action, cluster name:%s' % cluster)
                cluster_status = self.component_container_cluster_validator.container_cluster_status_validator(cluster_name)
                cluster.setdefault('status', cluster_status)
                cluster.setdefault('clusterName', cluster_name)
                
                zkOper = Requests_ZkOpers()
                cluster_info = zkOper.retrieve_container_cluster_info(cluster_name)
                _type = cluster_info.get('type')
                cluster.setdefault('type', _type)
                
                for _,node_value in nodes.items():
                    container_info = node_value.get('container_info')
                    con = Container_Model()
                    create_info = con.create_info(container_info)
                    nodeInfo.append(create_info)
                cluster.setdefault('nodeInfo', nodeInfo)
                clusters.append(cluster)
                
            except:
                self.threading_exception_queue.put(sys.exc_info())
                continue
            
        return clusters

    def get_clusters_zk(self):
        zkOper = Requests_ZkOpers()
        cluster_name_list = zkOper.retrieve_cluster_list()
        clusters_zk_info = {}
        for cluster_name in cluster_name_list:
            cluster_info_dict = self.get_cluster_zk(cluster_name)
            clusters_zk_info.setdefault(cluster_name, cluster_info_dict)

        return clusters_zk_info

    def get_cluster_zk(self, cluster_name):
        cluster_zk_info = {}
        zkOper = Requests_ZkOpers()
        container_ip_list = zkOper.retrieve_container_list(cluster_name)
        for container_ip in container_ip_list:
            container_node = {}
            create_info = zkOper.retrieve_container_node_value(
                cluster_name, container_ip)
            status = zkOper.retrieve_container_status_value(
                cluster_name, container_ip)
            container_node.setdefault('container_info', create_info)
            container_node.setdefault('status', status)
            cluster_zk_info.setdefault(container_ip, container_node)
        return cluster_zk_info

    '''
        one cluster status func
    '''

    def __get_cluster_status(self, nodes):
        n = 0
        for _, container_info in nodes.items():
            stat = container_info.get('status').get('status')
            if stat == Status.destroyed:
                n += 1
        if n == len(nodes):
            exist = Status.destroyed
        else:
            exist = Status.alive
        return exist

    def create_result(self, containerClusterName):
        create_successful = {'code': "000000"}
        creating = {'code': "000001"}
        create_failed = {'code': "000002", 'status': Status.create_failed}

        zkOper = Requests_ZkOpers()
        exists = zkOper.check_containerCluster_exists(containerClusterName)
        if not exists:
            raise UserVisiableException(
                'containerCluster %s not existed' % containerClusterName)

        result = {}

        container_cluster_info = zkOper.retrieve_container_cluster_info(
            containerClusterName)
        start_flag = container_cluster_info.get('start_flag')

        if start_flag == Status.failed:
            result.update(create_failed)
            result.setdefault('error_msg', 'create containers failed!')

        elif start_flag == Status.succeed:
            create_info = self.__cluster_created_info(containerClusterName)
            result.update(create_successful)
            result.update(create_info)
        else:
            result.update(creating)
        return result

    def __cluster_created_info(self, cluster):
        zkOper = Requests_ZkOpers()
        message_list = []

        container_node_list = zkOper.retrieve_container_list(cluster)
        result = {}
        for container_node in container_node_list:
            container_node_value = zkOper.retrieve_container_node_value(
                cluster, container_node)
            con = Container_Model()
            create_info = con.create_info(container_node_value)
            message_list.append(create_info)
        result.setdefault('containers', message_list)
        return result
