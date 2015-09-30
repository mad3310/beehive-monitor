__author__ = 'mazheng'

import sys

from common.abstractAsyncThread import Abstract_Async_Thread
from resource_letv.containerResourceOpers import ContainerNetworkIOHandler


class ContainerNetworkIOWorker(Abstract_Async_Thread):

    def __init__(self, timeout=5):
        super(ContainerNetworkIOWorker, self).__init__()
        self.timeout = timeout
        self.network_io = ContainerNetworkIOHandler()

    def run(self):
        try:
            self.network_io.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
