__author__ = 'mazheng'

import sys

from ..base_worker import BaseWorker
from resource_letv.containerResourceOpers import ContainerDiskLoadHandler


class ContainerDiskLoadWorker(BaseWorker):

    def __init__(self, timeout=5):
        super(ContainerDiskLoadWorker, self).__init__()
        self.timeout = timeout
        self.disk_load_handler = ContainerDiskLoadHandler()

    def job(self):
        try:
            self.disk_load_handler.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
