#!/usr/bin/env python2.6.6
#-*- coding: utf-8 -*-

'''
Created on 2013-7-21

@author: root
'''

from tornado.ioloop import PeriodicCallback
from tornado.options import options

from scheduler.worker.threading_exception_handle_worker import Thread_Exception_Handler_Worker
from scheduler.worker.container.container_cpuacct_worker import ContainerCPUAcctWorker
from scheduler.worker.container.container_memory_worker import ContainerMemoryWorker
from scheduler.worker.container.container_network_io_worker import ContainerNetworkIOWorker
from scheduler.worker.container.container_disk_iops_worker import ContainerDiskIOPSWorker
from scheduler.worker.container.container_disk_load_worker import ContainerDiskLoadWorker
from scheduler.worker.container.container_cache_worker import ContainerCacheWorker
from scheduler.worker.container.container_oom_worker import Containers_Oom_Worker

from scheduler.worker.server.server_resource_worker import ServerResourceWorker
from scheduler.worker.server.monitor_check_worker import Monitor_Check_Worker
from scheduler.worker.server.check_ip_legality_worker import Check_Ip_Legality_Worker
from scheduler.worker.server.sync_server_zk_worker import Sync_Server_Zk_Worker


class SchedulerOpers(object):

    def __init__(self):

        self.thread_exception_hanlder(10)
        self.container_cache_handler(7)

        self.container_cpuacct_handler(options.container_gather_duration)
        self.container_memory_handler(options.container_gather_duration)
        self.container_network_io_handler(options.container_gather_duration)
        self.container_disk_iops_handler(options.container_gather_duration)
        self.container_disk_load_handler(options.container_gather_duration)
        self.container_oom_handler(300)
        
        self.server_resource_handler(options.server_gather_duration)
        self.monitor_check_handler(55)
        self.check_ip_legality_handler(300)
        self.sync_server_zk_handler(240)

    @staticmethod
    def valid(timeout):
        return timeout > 0

    def container_oom_handler(self, action_timeout):
        
        def __container_oom_handler():
            _woker = Containers_Oom_Worker(action_timeout)
            _woker.start()
            
        _worker = PeriodicCallback(__container_oom_handler, action_timeout * 1000)
        _worker.start()

    def thread_exception_hanlder(self, action_timeout=5):

        def __create_worker_exception_handler():
            exception_hanlder_worker = Thread_Exception_Handler_Worker()
            exception_hanlder_worker.start()

        if self.valid(action_timeout):
            _exception_async_t = PeriodicCallback(
                __create_worker_exception_handler, action_timeout * 1000)
            _exception_async_t.start()

    def container_cache_handler(self, action_timeout=3):

        if self.valid(action_timeout):
            container_cache_worker = ContainerCacheWorker(action_timeout)
            container_cache = PeriodicCallback(
                container_cache_worker, action_timeout * 1000)
            container_cache.start()

    def container_cpuacct_handler(self, action_timeout=5):

        if self.valid(action_timeout):
            container_cpuacct_worker = ContainerCPUAcctWorker(action_timeout)
            container_cpuacct = PeriodicCallback(
                container_cpuacct_worker, action_timeout * 1000)
            container_cpuacct.start()

    def container_memory_handler(self, action_timeout=5):

        if self.valid(action_timeout):
            container_memory_worker = ContainerMemoryWorker(action_timeout)
            container_memory = PeriodicCallback(
                container_memory_worker, action_timeout * 1000)
            container_memory.start()

    def container_network_io_handler(self, action_timeout=5):

        if self.valid(action_timeout):
            container_network_io_worker = ContainerNetworkIOWorker(
                action_timeout)
            container_network_io = PeriodicCallback(
                container_network_io_worker, action_timeout * 1000)
            container_network_io.start()

    def container_disk_iops_handler(self, action_timeout=5):

        if self.valid(action_timeout):
            container_disk_iops_worker = ContainerDiskIOPSWorker(
                action_timeout)
            container_disk_iops = PeriodicCallback(
                container_disk_iops_worker, action_timeout * 1000)
            container_disk_iops.start()

    def container_disk_load_handler(self, action_timeout=5):

        if self.valid(action_timeout):
            container_disk_load_worker = ContainerDiskLoadWorker(
                action_timeout)
            container_disk_load = PeriodicCallback(
                container_disk_load_worker, action_timeout * 1000)
            container_disk_load.start()

    def server_resource_handler(self, action_timeout=2):

        if self.valid(action_timeout):
            server_resource_worker = ServerResourceWorker(action_timeout)
            _server_resource_async_t = PeriodicCallback(
                server_resource_worker, action_timeout * 1000)
            _server_resource_async_t.start()

    def check_ip_legality_handler(self, action_timeout):
        
        def __check_ip_legality_woker():
            check_ip_legality_worker = Check_Ip_Legality_Worker(action_timeout)
            check_ip_legality_worker.start()
            
        _worker = PeriodicCallback(__check_ip_legality_woker, action_timeout * 1000)
        _worker.start()

    def sync_server_zk_handler(self, action_timeout):
        
        def __sync_server_zk_woker():
            sync_server_zk_woker = Sync_Server_Zk_Worker()
            sync_server_zk_woker.start()
            
        _worker = PeriodicCallback(__sync_server_zk_woker, action_timeout * 1000)
        _worker.start()

    def monitor_check_handler(self, action_timeout = 55):
        
        def __monitor_check_worker():
            monitor_check_worker = Monitor_Check_Worker(action_timeout)
            monitor_check_worker.start()
        
        if self.valid(action_timeout):
            _monitor_async_t = PeriodicCallback(__monitor_check_worker, action_timeout * 1000)
            _monitor_async_t.start()

