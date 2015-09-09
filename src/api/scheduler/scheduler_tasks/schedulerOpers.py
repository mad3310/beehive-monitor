#!/usr/bin/env python2.6.6
#-*- coding: utf-8 -*-

'''
Created on 2013-7-21

@author: root
'''

from tornado.ioloop import PeriodicCallback
from scheduler.worker.threading_exception_handle_worker import Thread_Exception_Handler_Worker
from scheduler.worker.server_resource_worker import ServerResourceWorker
from scheduler.worker.container_cpuacct_worker import ContainerCPUAcctWorker
from scheduler.worker.container_memory_worker import ContainerMemoryWorker
from scheduler.worker.container_network_io_worker import ContainerNetworkIOWorker
from scheduler.worker.container_disk_iops_worker import ContainerDiskIOPSWorker
from scheduler.worker.container_disk_load_worker import ContainerDiskLoadWorker


class SchedulerOpers(object):

    def __init__(self):
        
        self.thread_exception_hanlder(5)
        self.server_resource_handler(2)
        self.container_cpuacct_handler(5)
        self.container_memory_handler(5)
        self.container_network_io_handler(5)
        self.container_disk_iops_handler(5)
        self.container_disk_load_handler(5)

    @staticmethod
    def valid(timeout):
        return timeout>0

    def container_cpuacct_handler(self,action_timeout=5):

        def __container_cpuacct_worker():
            container_cpuacct_worker=ContainerCPUAcctWorker(action_timeout)
            container_cpuacct_worker.start()

        if self.valid(action_timeout):
            container_cpuacct=PeriodicCallback(__container_cpuacct_worker, action_timeout * 1000)
            container_cpuacct.start()

    def container_memory_handler(self,action_timeout=5):

        def __container_memory_worker():
            container_memory_worker=ContainerMemoryWorker(action_timeout)
            container_memory_worker.start()

        if self.valid(action_timeout):
            container_memory=PeriodicCallback(__container_memory_worker, action_timeout * 1000)
            container_memory.start()

    def container_network_io_handler(self,action_timeout=5):

        def __container_network_io_worker():
            container_network_io_worker=ContainerNetworkIOWorker(action_timeout)
            container_network_io_worker.start()

        if self.valid(action_timeout):
            container_network_io=PeriodicCallback(__container_network_io_worker, action_timeout * 1000)
            container_network_io.start()

    def container_disk_iops_handler(self,action_timeout=5):

        def __container_disk_iops_worker():
            container_disk_iops_worker=ContainerDiskIOPSWorker(action_timeout)
            container_disk_iops_worker.start()

        if self.valid(action_timeout):
            container_disk_iops=PeriodicCallback(__container_disk_iops_worker, action_timeout * 1000)
            container_disk_iops.start()

    def container_disk_load_handler(self,action_timeout=5):

        def __container_disk_load_worker():
            container_disk_load_worker=ContainerDiskLoadWorker(action_timeout)
            container_disk_load_worker.start()

        if self.valid(action_timeout):
            container_disk_load=PeriodicCallback(__container_disk_load_worker, action_timeout * 1000)
            container_disk_load.start()

    def server_resource_handler(self, action_timeout = 2):
        
        def __server_resource_worker():
            server_resource_worker = ServerResourceWorker(action_timeout)
            server_resource_worker.start()
        
        if self.valid(action_timeout):
            _server_resource_async_t = PeriodicCallback(__server_resource_worker, action_timeout * 1000)
            _server_resource_async_t.start()

    def thread_exception_hanlder(self, action_timeout = 5):

        def __create_worker_exception_handler():
            exception_hanlder_worker = Thread_Exception_Handler_Worker()
            exception_hanlder_worker.start()
        
        if self.valid(action_timeout):
            _exception_async_t = PeriodicCallback(__create_worker_exception_handler, action_timeout * 1000)
            _exception_async_t.start()
