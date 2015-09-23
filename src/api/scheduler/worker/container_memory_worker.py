__author__ = 'mazheng'

import sys

from base_worker import BaseWorker
from resource_letv.containerResourceOpers import ContainerMemoryHandler


class ContainerMemoryWorker(BaseWorker):

    def __init__(self, timeout=5):
        super(ContainerMemoryWorker, self).__init__()
        self.timeout = timeout
        self.memory_handler = ContainerMemoryHandler()

    def job(self):
        try:
            self.memory_handler.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
