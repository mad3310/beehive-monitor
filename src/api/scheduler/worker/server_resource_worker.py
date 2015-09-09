__author__ = 'mazheng'

import sys
import time
import logging

from kazoo.exceptions import LockTimeout

from zk.zkOpers import Scheduler_ZkOpers
from common.abstractAsyncThread import  Abstract_Async_Thread
from resource_letv.serverResourceOpers import ServerCPUHandler,ServerMemoryHandler,ServerDiskHandler


class ServerResourceWorker(Abstract_Async_Thread):

    def __init__(self,timeout=2):
        super(ServerResourceWorker,self).__init__()
        self.timeout=timeout
        self.cpu_handler=ServerCPUHandler()
        self.memory_handler=ServerMemoryHandler()
        self.disk_handler=ServerDiskHandler()

    def run(self):
        zk_op=Scheduler_ZkOpers()
        try:
            is_lock,lock=zk_op.lock_server_resource()
        except LockTimeout:
            logging.info("get zookeeper lock time out")
            return

        if not is_lock:
            logging.info("other thread keeps the lock,cannot get")
            return

        try:
            start=time.time()
            self._write_server_resource()
            while True:
                end=time.time()
                duration=end-start
                if duration > (self.timeout-1):
                    logging.info('release the log, get lock time: %s, release time: %s,\n total time : %s' % (str(start), str(end), int(duration)))
                    break
            time.sleep(1)
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
        finally:
            if is_lock:
                zk_op.unLock_server_resource(lock)

    def _write_server_resource(self):
        self.cpu_handler.gather()
        self.memory_handler.gather()
        self.disk_handler.gather()