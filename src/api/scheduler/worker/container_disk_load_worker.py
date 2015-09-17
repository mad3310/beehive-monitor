__author__ = 'mazheng'

import sys

from common.abstractAsyncThread import Abstract_Async_Thread
from resource_letv.containerResourceOpers import ContainerDiskLoadHandler


class ContainerDiskLoadWorker(Abstract_Async_Thread):

    def __init__(self, timeout=5):
        super(ContainerDiskLoadWorker, self).__init__()
        self.timeout = timeout
        self.disk_load_handler = ContainerDiskLoadHandler()

    def run(self):
        try:
            self.disk_load_handler.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
