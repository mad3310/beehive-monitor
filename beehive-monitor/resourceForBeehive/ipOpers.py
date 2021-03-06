#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
Created on Sep 17, 2014

@author: root
'''

import time
import Queue
import logging
import re
import kazoo

from utils import ping_ip_available
from utils.threadUtil import doInThread
from dockerForBeehive.dockerOpers import Docker_Opers
from zk.zkOpers import Common_ZkOpers


class IpOpers(object):
    '''
    classdocs
    '''
    
    store_illegal_ips_queue = Queue.Queue()
    store_all_ips_queue = Queue.Queue()

    docker_opers = Docker_Opers()
    
    def __init__(self):
        '''
        constructor
        '''     

    def __ip_legal(self, ip):
        ip_pattern = '((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)'
        if not re.match(ip_pattern, ip):
            logging.info('ip :%s not legal in pool' % ip)
            return False
        
        ret = ping_ip_available(ip)
        if ret:
            logging.info('ping ip: %s result :%s' % (ip, str(ret)) )
            return False
        
        host_con_ip_list = self.docker_opers.retrieve_containers_ips()
        if ip in host_con_ip_list:
            return False
        return True

        
    def __ips_legal(self):
        """
        """
        while not self.store_all_ips_queue.empty():
            ip = self.store_all_ips_queue.get(block=False)
            is_lagel = self.__ip_legal(ip)
            if not is_lagel:
                self.store_illegal_ips_queue.put(ip)

    def get_illegal_ips(self, thread_num):
        """check ip pools
           
           thread_num: how many thread to do check if ip is legal
           put all ips in ip pools into store_all_ips_queue,
           do check ip is legal in  threads, if illegal, put illegal ip into store_illegal_ips_queue,
           if all threads end, get illegal ips and return them
        """
        
        illegal_ips, thread_obj_list = [], []
        zkOper = Common_ZkOpers()
        ip_list = zkOper.get_ips_from_ipPool()
        logging.info('put all ips in ip pools into store_all_ips_queue')
        
        self.store_all_ips_queue._init(0)
        self.store_all_ips_queue.queue.extend(ip_list)
        
        logging.info('queue size :%s' % str(self.store_all_ips_queue.qsize()) )
        for i in range(thread_num):
            thread_obj = doInThread(self.__ips_legal)
            thread_obj_list.append(thread_obj)
        
        while thread_obj_list:
            succ = []
            for thread_obj in thread_obj_list:
                if not thread_obj.isAlive():
                    succ.append(thread_obj)
            for item in succ:
                thread_obj_list.remove(item)
            time.sleep(0.5)
        
        logging.info('get illegal_ip')
        while not self.store_illegal_ips_queue.empty():
            illegal_ip = self.store_illegal_ips_queue.get(block=False)
            illegal_ips.append(illegal_ip)
        logging.info('illegal_ips :%s' % str(illegal_ips) )
        return illegal_ips
    
    def get_ip_num(self):
        """
            monitor item: get ip num from ip Pool
        """
        zkOper = Common_ZkOpers()
        ip_list = zkOper.get_ips_from_ipPool()
        return len(ip_list)

    def retrieve_ip_resource(self, ip_count, try_times=5):
        n = 0
        while n < try_times:
            n += 1
            ip_list = self.do_retrieve_ip_action(ip_count)
            if ip_list:
                return ip_list
            time.sleep(1)
 
    def do_retrieve_ip_action(self, ip_count):
        ip_list, isLock = None, None
        
        zkOper = Common_ZkOpers()
        try:
            isLock,lock = zkOper.lock_assign_ip()
            if isLock:
                ip_list = zkOper.retrieve_ip(ip_count)
        except kazoo.exceptions.LockTimeout:
            return
            
        finally:
            if isLock:
                zkOper.unLock_assign_ip(lock)
            
        return ip_list

