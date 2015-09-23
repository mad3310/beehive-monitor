__author__ = 'mazheng'

import sys

from base_worker import BaseWorker
from resource_letv.containerResourceOpers import ContainerDiskIOPSHandler


class ContainerDiskIOPSWorker(BaseWorker):

    def __init__(self, timeout=5):
        super(ContainerDiskIOPSWorker, self).__init__()
        self.timeout = timeout
        self.disk_iops_handler = ContainerDiskIOPSHandler()

    def job(self):
        try:
            self.disk_iops_handler.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
