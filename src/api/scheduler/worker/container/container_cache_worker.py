__author__ = 'mazheng'

import sys

from ..base_worker import BaseWorker
from resource_letv.containerResourceOpers import ContainerCacheHandler


class ContainerCacheWorker(BaseWorker):

    def __init__(self, timeout=5):
        super(ContainerCacheWorker, self).__init__()
        self.timeout = timeout
        self.cache_handler = ContainerCacheHandler()

    def job(self):
        try:
            self.cache_handler.gather()
        except Exception:
            self.threading_exception_queue.put(sys.exc_info())
