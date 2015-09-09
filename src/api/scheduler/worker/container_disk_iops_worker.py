__author__ = 'mazheng'

import sys
import logging

from kazoo.exceptions import LockTimeout

from zk.zkOpers import Scheduler_ZkOpers
from common.abstractAsyncThread import Abstract_Async_Thread
from resource_letv.containerResourceOpers import ContainerDiskIOPSHandler


class ContainerDiskIOPSWorker(Abstract_Async_Thread):

    def __init__(self,timeout=5):
        super(ContainerDiskIOPSWorker,self).__init__()
        self.timeout=timeout
        self.disk_iops_handler=ContainerDiskIOPSHandler()

    def run(self):
        zkOper = Scheduler_ZkOpers()
        try:
            isLock, lock = zkOper.lock_container_diskiops()
        except LockTimeout:
            logging.info("a thread is running the monitor async, give up this oper on this machine!")
            return

        if not isLock:
            return

        try:
            self.disk_iops_handler.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
        finally:
            if isLock:
                zkOper.unLock_container_diskiops(lock)
