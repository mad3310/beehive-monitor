__author__ = 'mazheng'

import sys

from base_worker import BaseWorker
from resource_letv.containerResourceOpers import ContainerNetworkIOHandler


class ContainerNetworkIOWorker(BaseWorker):

    def __init__(self, timeout=5):
        super(ContainerNetworkIOWorker, self).__init__()
        self.timeout = timeout
        self.network_io = ContainerNetworkIOHandler()

    def job(self):
        try:
            self.network_io.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
