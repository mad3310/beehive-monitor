__author__ = 'mazheng'

import sys

from ..base_worker import BaseWorker
from resource_letv.containerResourceOpers import ContainerDiskUsageHandler


class ContainerDiskUsageWorker(BaseWorker):

    def __init__(self, timeout=5):
        self.timeout = timeout
        self.disk_usage_handler = ContainerDiskUsageHandler()

    def job(self):
        try:
            self.disk_usage_handler.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
