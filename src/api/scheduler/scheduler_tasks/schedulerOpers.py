#!/usr/bin/env python2.6.6
#-*- coding: utf-8 -*-

'''
Created on 2013-7-21

@author: root
'''

from tornado.ioloop import PeriodicCallback
from tornado.options import options

from scheduler.worker.threading_exception_handle_worker import Thread_Exception_Handler_Worker
from scheduler.worker.server_resource_worker import ServerResourceWorker
from scheduler.worker.container_cpuacct_worker import ContainerCPUAcctWorker
from scheduler.worker.container_memory_worker import ContainerMemoryWorker
from scheduler.worker.container_network_io_worker import ContainerNetworkIOWorker
from scheduler.worker.container_disk_iops_worker import ContainerDiskIOPSWorker
from scheduler.worker.container_disk_load_worker import ContainerDiskLoadWorker
from scheduler.worker.container_cache_worker import ContainerCacheWorker


class SchedulerOpers(object):

    def __init__(self):

        self.thread_exception_hanlder(10)
        self.container_cache_handler(7)

        self.server_resource_handler(options.server_gather_duration)

        self.container_cpuacct_handler(options.container_gather_duration)
        self.container_memory_handler(options.container_gather_duration)
        self.container_network_io_handler(options.container_gather_duration)
        self.container_disk_iops_handler(options.container_gather_duration)
        self.container_disk_load_handler(options.container_gather_duration)

    @staticmethod
    def valid(timeout):
        return timeout > 0

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

    def thread_exception_hanlder(self, action_timeout=5):

        def __create_worker_exception_handler():
            exception_hanlder_worker = Thread_Exception_Handler_Worker()
            exception_hanlder_worker.start()

        if self.valid(action_timeout):
            _exception_async_t = PeriodicCallback(
                __create_worker_exception_handler, action_timeout * 1000)
            _exception_async_t.start()
