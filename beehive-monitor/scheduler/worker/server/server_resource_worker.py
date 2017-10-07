__author__ = 'mazheng'

import sys

from scheduler.worker.base_worker import BaseWorker
from resourceForBeehive.serverResourceOpers import (ServerCPUHandler,
                                               ServerMemoryHandler,
                                               ServerDiskusageHandler,
                                               ContainerCountHandler,
                                               ServerDiskiopsHandler)


class ServerResourceWorker(BaseWorker):

    def __init__(self, timeout=2):
        self.timeout = timeout
        self.cpu_handler = ServerCPUHandler()
        self.memory_handler = ServerMemoryHandler()
        self.diskusage_handler = ServerDiskusageHandler()
        self.diskiops_handler = ServerDiskiopsHandler()
        self.container_count_handler = ContainerCountHandler()

    def job(self):
        try:
            self._write_server_resource()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())

    def _write_server_resource(self):
        self.cpu_handler.gather()
        self.memory_handler.gather()
        self.diskusage_handler.gather()
        self.container_count_handler.gather()
        self.diskiops_handler.gather()
