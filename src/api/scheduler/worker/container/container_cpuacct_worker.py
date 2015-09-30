__author__ = 'mazheng'

import sys

from common.abstractAsyncThread import Abstract_Async_Thread
from resource_letv.containerResourceOpers import ContainerCPUAcctHandler


class ContainerCPUAcctWorker(Abstract_Async_Thread):

    def __init__(self, timeout=5):
        super(ContainerCPUAcctWorker, self).__init__()
        self.timeout = timeout
        self.cpuacct_handler = ContainerCPUAcctHandler()

    def run(self):
        try:
            self.cpuacct_handler.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
