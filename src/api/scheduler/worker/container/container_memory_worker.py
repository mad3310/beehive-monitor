__author__ = 'mazheng'

import sys

from common.abstractAsyncThread import Abstract_Async_Thread
from resource_letv.containerResourceOpers import ContainerMemoryHandler


class ContainerMemoryWorker(Abstract_Async_Thread):

    def __init__(self, timeout=5):
        super(ContainerMemoryWorker, self).__init__()
        self.timeout = timeout
        self.memory_handler = ContainerMemoryHandler()

    def run(self):
        try:
            self.memory_handler.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
