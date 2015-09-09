__author__ = 'mazheng'

import sys
import logging

from kazoo.exceptions import LockTimeout

from zk.zkOpers import Scheduler_ZkOpers
from common.abstractAsyncThread import Abstract_Async_Thread
from resource_letv.containerResourceOpers import ContainerMemoryHandler


class ContainerMemoryWorker(Abstract_Async_Thread):

    def __init__(self,timeout=5):
        super(ContainerMemoryWorker,self).__init__()
        self.timeout=timeout
        self.memory_handler=ContainerMemoryHandler()

    def run(self):
        zkOper = Scheduler_ZkOpers()
        try:
            isLock, lock = zkOper.lock_container_memory()
        except LockTimeout:
            logging.info("a thread is running the monitor async, give up this oper on this machine!")
            return

        if not isLock:
            return

        try:
            self.memory_handler.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
        finally:
            if isLock:
                zkOper.unLock_container_memory(lock)
