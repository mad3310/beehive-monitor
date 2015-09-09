__author__ = 'mazheng'

import sys
import logging

from kazoo.exceptions import LockTimeout

from zk.zkOpers import Scheduler_ZkOpers
from common.abstractAsyncThread import Abstract_Async_Thread
from resource_letv.containerResourceOpers import ContainerNetworkIOHandler


class ContainerNetworkIOWorker(Abstract_Async_Thread):

    def __init__(self,timeout=5):
        super(ContainerNetworkIOWorker,self).__init__()
        self.timeout=timeout
        self.network_io=ContainerNetworkIOHandler()

    def run(self):
        zkOper = Scheduler_ZkOpers()
        try:
            isLock, lock = zkOper.lock_container_networkio()
        except LockTimeout:
            logging.info("a thread is running the monitor async, give up this oper on this machine!")
            return

        if not isLock:
            return

        try:
            self.network_io.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
        finally:
            if isLock:
                zkOper.unLock_container_networkio(lock)
