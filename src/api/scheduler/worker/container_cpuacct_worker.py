__author__ = 'mazheng'

import sys

from base_worker import BaseWorker
from resource_letv.containerResourceOpers import ContainerCPUAcctHandler


class ContainerCPUAcctWorker(BaseWorker):

    def __init__(self, timeout=5):
        super(ContainerCPUAcctWorker, self).__init__()
        self.timeout = timeout
        self.cpuacct_handler = ContainerCPUAcctHandler()

    def job(self):
        try:
            self.cpuacct_handler.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
