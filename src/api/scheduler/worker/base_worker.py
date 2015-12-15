__author__ = 'mazheng'

from concurrent import futures

from utils.threading_exception_queue import Threading_Exception_Queue


class BaseWorker(object):

    threading_exception_queue = Threading_Exception_Queue()
    _thread_pool = futures.ThreadPoolExecutor(17)

    def job(self):
        raise NotImplemented("base worker job method should be implemented")

    def __call__(self, *args, **kwargs):
        self.run()

    def run(self):
        self._thread_pool.submit(self.job)
