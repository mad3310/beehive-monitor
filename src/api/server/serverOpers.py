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


class Server_Opers(object):
    '''
    classdocs
    '''
    
    def update(self):
        host_ip = getHostIp()
        server_update_action = ServerUpdateAction(host_ip)
        server_update_action.start()

    def host_exist(self, host_ip):
        zk_op = Common_ZkOpers()
        return zk_op.check_data_node_exist(host_ip)


class ServerUpdateAction(Abstract_Async_Thread):

    docker_opers = Docker_Opers()
    container_opers = Container_Opers()

    def __init__(self, host_ip):
        super(ServerUpdateAction, self).__init__()
        self.host_ip = host_ip

    def run(self):
        try:
            logging.info('do update on server : %s' % self.host_ip)
            self.__update()
        except:
            self.threading_exception_queue.put(sys.exc_info())

    def __update(self):
        host_containers = self._get_containers_from_host()
        zk_containers = self._get_containers_from_zookeeper()
        add, delete, both = self._compare(host_containers, zk_containers)
        
        logging.info('delete item: %s' % str(delete) )
        for item in add:
            self.update_add_node(item)
        for item in delete:
            self.update_del_node(item)
        for item in both:
            self.update_both_node(item)

    def update_both_node(self, container_name):
        
        '''
            container node info in zookeeper (not status) will not be changed, no need to update.
        '''
        status = {}

        zk_con_info = self.container_opers.retrieve_container_node_value_from_containerName(container_name)
        _type = zk_con_info.get('type')
        con_info = self.container_opers.container_info(container_name, _type)
        
        if con_info != zk_con_info:
            logging.info('update both node zookeeper info, container name :%s' % container_name)
            self.container_opers.write_container_node_value_by_containerName(container_name, con_info)
        
        server_con_stat = self.container_opers.get_container_stat(container_name)
        zk_con_stat = self.container_opers.retrieve_container_status_from_containerName(container_name)
        if server_con_stat != zk_con_stat:
            status.setdefault('status',  server_con_stat)
            status.setdefault('message',  '')
            self.container_opers.write_container_status_by_containerName(container_name, status)

    def update_add_node(self, container_name):
        logging.info('update add node : %s' % container_name )
        create_info = self.container_opers.container_info(container_name)
        self.container_opers.write_container_node_value_by_containerName(container_name, create_info)
        container_stat = self.container_opers.get_container_stat(container_name)
        status = {'status': container_stat, 'message': ''}
        self.container_opers.write_container_status_by_containerName(container_name, status)

    def update_del_node(self, container_name):
        status = {'status': Status.destroyed, 'message': ''}
        logging.info('container :%s are not existed, the infomation remains in zookeeper still' % container_name)
        self.container_opers.write_container_status_by_containerName(container_name, status)

    def _get_containers_from_host(self):
        container_name_list = []
        container_info_list = self.docker_opers.containers(all=True)
        for container_info in container_info_list:
            container_name = container_info.get('Names')[0]
            container_name = container_name.replace('/', '')
            container_name_list.append(container_name)
        return container_name_list

    def _get_containers_from_zookeeper(self):
        """if the status container in zookeeper is destroyed, regard this container as not exist.
        
        """
        container_name_list, container_info= [], {}
        
        zkOper = Common_ZkOpers()

        clusters = zkOper.retrieve_cluster_list()
        for cluster in clusters:
            container_ip_list = zkOper.retrieve_container_list(cluster)
            for container_ip in container_ip_list:
                container_info = zkOper.retrieve_container_node_value(cluster, container_ip)
                host_ip = container_info.get('hostIp')
                if self.host_ip == host_ip:
                    if container_info.has_key('containerName'):
                        container_name = container_info.get('containerName')
                    else:
                        inspect = container_info.get('inspect')
                        con = Container_Model(inspect=inspect)
                        container_name = con.name()
                    container_name_list.append(container_name)

        return container_name_list

    def _compare(self, host_container_list, zk_container_list):
        add = list( set(host_container_list) - set(zk_container_list) )
        delete = list( set(zk_container_list) - set(host_container_list) )
        both = list( set(host_container_list) & set( zk_container_list) )
        return add, delete, both

