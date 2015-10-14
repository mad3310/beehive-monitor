__author__ = 'mazheng'

import sys

from scheduler.worker.base_worker import BaseWorker
from resource_letv.serverResourceOpers import ServerCPUHandler, ServerMemoryHandler, ServerDiskHandler, ContainerCountHandler


class ServerResourceWorker(BaseWorker):

    def __init__(self, timeout=2):
        super(ServerResourceWorker, self).__init__()
        self.timeout = timeout
        self.cpu_handler = ServerCPUHandler()
        self.memory_handler = ServerMemoryHandler()
        self.disk_handler = ServerDiskHandler()
        self.container_count_handler = ContainerCountHandler()

    def job(self):
        try:
            self._write_server_resource()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())

    def _write_server_resource(self):
        self.cpu_handler.gather()
        self.memory_handler.gather()
        self.disk_handler.gather()
        self.container_count_handler.gather()