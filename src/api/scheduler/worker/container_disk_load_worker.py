__author__ = 'mazheng'

import sys
import logging

from kazoo.exceptions import LockTimeout

from zk.zkOpers import Scheduler_ZkOpers
from common.abstractAsyncThread import Abstract_Async_Thread
from resource_letv.containerResourceOpers import ContainerDiskLoadHandler


class ContainerDiskLoadWorker(Abstract_Async_Thread):

    def __init__(self, timeout=5):
        super(ContainerDiskLoadWorker, self).__init__()
        self.timeout = timeout
        self.disk_load_handler = ContainerDiskLoadHandler()

    def run(self):
        zkOper = Scheduler_ZkOpers()
        try:
            isLock, lock = zkOper.lock_container_diskload()
        except LockTimeout:
            logging.info(
                "a thread is running the monitor async, give up this oper on this machine!")
            return

        if not isLock:
            return

        try:
            self.disk_load_handler.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
        finally:
            if isLock:
                zkOper.unLock_container_diskload(lock)
