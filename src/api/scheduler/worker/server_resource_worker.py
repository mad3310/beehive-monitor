__author__ = 'mazheng'

import sys

from common.abstractAsyncThread import Abstract_Async_Thread
from resource_letv.serverResourceOpers import ServerCPUHandler, ServerMemoryHandler, ServerDiskHandler


class ServerResourceWorker(Abstract_Async_Thread):

    def __init__(self, timeout=2):
        super(ServerResourceWorker, self).__init__()
        self.timeout = timeout
        self.cpu_handler = ServerCPUHandler()
        self.memory_handler = ServerMemoryHandler()
        self.disk_handler = ServerDiskHandler()

    def run(self):
        try:
            self._write_server_resource()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())

    def _write_server_resource(self):
        self.cpu_handler.gather()
        self.memory_handler.gather()
        self.disk_handler.gather()
