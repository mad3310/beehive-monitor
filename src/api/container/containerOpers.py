#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
Created on Sep 8, 2014

@author: root
'''

import logging
import re

from docker_letv.dockerOpers import Docker_Opers
from container.container_model import Container_Model
from utils.exceptions import CommonException, UserVisiableException
from utils import get_current_time, getHostIp
from zk.zkOpers import Container_ZkOpers
from status.status_enum import Status
from state.stateOpers import StateOpers
from utils import get_containerClusterName_from_containerName


class Container_Opers(object):

    docker_opers = Docker_Opers()

    def __init__(self):
        '''
        Constructor
        '''

    def check(self, container_name):
        exists = self.check_container_exists(container_name)
        if not exists:
            raise UserVisiableException(
                "container(name:%s) dont's existed!" % (container_name))

        container_operation_record = self.retrieve_container_status_from_containerName(
            container_name)
        status = container_operation_record.get('status')
        message = container_operation_record.get('message')

        result = {}
        result.setdefault('status', status)
        result.setdefault('message', message)
        return result

    def get_container_stat(self, container_name):
        """
        """
        exists = self.check_container_exists(container_name)
        if not exists:
            return Status.destroyed

        container_info_list = self.docker_opers.containers(all=True)

        for container_info in container_info_list:
            name = container_info.get('Names')[0]
            name = name.replace('/', '')
            if name == container_name:
                stat = container_info.get('Status')
                if 'Up' in stat:
                    return Status.started
                elif 'Exited' in stat:
                    return Status.stopped

    def get_all_containers(self, is_all=True):
        """get all containers on some server

        all -> True  all containers on such server
        all -> False  started containers on such server
        """
        container_name_list = []
        container_info_list = self.docker_opers.containers(all=is_all)
        for container_info in container_info_list:
            name = container_info.get('Names')[0]
            name = name.replace('/', '')
            container_name_list.append(name)
        return container_name_list

    def check_container_exists(self, container_name):
        cluster_name = get_containerClusterName_from_containerName(
            container_name)
        container_node = self.get_container_node_from_container_name(
            cluster_name, container_name)
        zk_op = Container_ZkOpers()
        return zk_op.check_container_exists(cluster_name, container_node)

    @staticmethod
    def cluster_start(cluster):
        zkOper = Container_ZkOpers()
        cluster_info = zkOper.retrieve_container_cluster_info(cluster)
        return cluster_info.get('start_flag', 'failed') == 'succeed'

    def check_container_name_legal(self, container_name):
        matched = re.match('^d-\w+.*-n-\d', container_name)
        return matched is not None

    def get_container_node_from_container_name(self, cluster, container_name):
        con_node = ''
        zkOper = Container_ZkOpers()
        cluster_info = zkOper.retrieve_container_cluster_info(cluster)
        use_ip = cluster_info.get('isUseIp')
        if use_ip:
            container_node_list = zkOper.retrieve_container_list(cluster)
            for container_node in container_node_list:
                container_info = zkOper.retrieve_container_node_value(
                    cluster, container_node)
                inspect = container_info.get('inspect')
                con = Container_Model(inspect=inspect)
                con_name = con.name()
                if container_name == con_name:
                    con_node = container_node
                    break
        else:
            con_node = container_name

        return con_node

    def retrieve_container_node_value_from_containerName(self, container_name):
        cluster = get_containerClusterName_from_containerName(container_name)
        container_node = self.get_container_node_from_container_name(
            cluster, container_name)

        zkOper = Container_ZkOpers()
        node_value = zkOper.retrieve_container_node_value(
            cluster, container_node)
        return node_value

    def retrieve_container_status_from_containerName(self, container_name):
        cluster = get_containerClusterName_from_containerName(container_name)
        container_node = self.get_container_node_from_container_name(
            cluster, container_name)

        zkOper = Container_ZkOpers()
        status_value = zkOper.retrieve_container_status_value(
            cluster, container_node)
        return status_value

    def write_container_node_value_by_containerName(self, container_name, container_props):
        """only write container value and not write status value

        """
        cluster = get_containerClusterName_from_containerName(container_name)
        container_node = self.get_container_node_from_container_name(
            cluster, container_name)

        zkOper = Container_ZkOpers()
        zkOper.write_container_node_value(
            cluster, container_node, container_props)

    def write_container_status_by_containerName(self, container_name, record):
        containerClusterName = get_containerClusterName_from_containerName(
            container_name)
        container_node = self.get_container_node_from_container_name(
            containerClusterName, container_name)

        zkOper = Container_ZkOpers()
        zkOper.write_container_status(
            containerClusterName, container_node, record)

    def get_container_name_from_zk(self, cluster, container_node):
        zkOper = Container_ZkOpers()
        container_info = zkOper.retrieve_container_node_value(
            cluster, container_node)
        inspect = container_info.get('inspect')
        con = Container_Model(inspect=inspect)
        return con.name()

    def get_host_ip_from_zk(self, cluster, container_node):
        zkOper = Container_ZkOpers()
        container_info = zkOper.retrieve_container_node_value(
            cluster, container_node)
        return container_info.get('hostIp')

    def write_container_node_info_to_zk(self, container_stat, containerProps):

        inspect = containerProps.get('inspect')
        is_use_ip = containerProps.get('isUseIp')
        con = Container_Model(inspect=inspect)
        container_name = con.name()
        cluster = con.cluster(container_name)
        logging.info('get container cluster :%s' % cluster)
        if is_use_ip:
            container_node = con.ip()
            logging.info('get container ip :%s' % container_node)
            if not (container_node and cluster):
                raise CommonException(
                    'get container ip or cluster name failed, not write this info, inspect:%s' % (inspect))

            container_node = container_node
        else:
            container_node = container_name

        zkOper = Container_ZkOpers()
        zkOper.write_container_node_info(
            cluster, container_node, container_stat, containerProps)

    def _get_containers(self, container_name_list):
        host_cons = self.get_all_containers(False)
        return list(set(host_cons) & set(container_name_list))

    def get_containers_disk_load(self, container_name_list):
        result = {}
        containers = self._get_containers(container_name_list)
        for container in containers:
            load = {}
            conl = StateOpers(container)
            #root_mnt_size, mysql_mnt_size = conl.get_sum_disk_usage()
            root_mnt_size, _ = conl.get_sum_disk_usage()
            load.setdefault('root_mount', root_mnt_size)
            #load.setdefault('mysql_mount', mysql_mnt_size)
            result.setdefault(container, load)
        return result

    def get_containers_resource(self, resource_type):
        container_name_list = self.get_all_containers(False)
        if not container_name_list:
            return {}

        resource_func_dict = {'under_oom': 'get_under_oom_value',
                              'oom_kill_disable': 'get_oom_kill_disable_value',
                              }

        resource_info, resource_item, container_resource = {}, {}, {}
        current_time = get_current_time()
        for container_name in container_name_list:
            state_opers = StateOpers(container_name)
            _method = resource_func_dict.get(resource_type)
            resource_item = getattr(state_opers, _method)()
            container_resource.setdefault(container_name, resource_item)

        resource_info.setdefault(str(resource_type), container_resource)
        resource_info.setdefault('time', current_time)
        return resource_info

    def write_containers_resource_to_zk(self, resource_type, resource_info):
        zkOper = Container_ZkOpers()
        host_ip = getHostIp()
        zkOper.writeDataNodeContainersResource(
            host_ip, resource_type, resource_info)

    def container_info(self, container_name, _type=None):
        """get container node info
        
        """
        create_info = {}
        _inspect = self.docker_opers.inspect_container(container_name)
        con = Container_Model(_inspect)
        if not _type:
            _type = con.inspect_component_type()
        
        create_info.setdefault('type', _type)
        create_info.setdefault('hostIp', getHostIp())
        create_info.setdefault('inspect', con.inspect)
        create_info.setdefault('isUseIp', con.use_ip())
        create_info.setdefault('containerName', container_name)
        return create_info
