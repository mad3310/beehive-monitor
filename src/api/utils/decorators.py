#!/usr/bin/env python 2.6.6
# coding:utf-8

from __future__ import absolute_import, division, print_function, with_statement

import functools
import logging
import sys
import traceback

from tornado.gen import Task
from tornado.ioloop import IOLoop
from tornado import stack_context

from utils import get_zk_address
from .exceptions import CommonException
from concurrent.futures import ThreadPoolExecutor


def singleton(cls):

    instances = {}

    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


def zk_singleton(cls):

    instances = {}

    def _zk_singleton(*args, **kw):

        zk_addr, zk_port = get_zk_address()
        if not (zk_addr and zk_port):
            raise CommonException(
                'zookeeper address and port are not written!')

        if cls not in instances:
            logging.info('no zk client, init one')
            instances[cls] = cls(*args, **kw)

        if instances[cls].zk is None:
            logging.info('zk client disconnect, init another one')
            instances[cls] = cls(*args, **kw)

        return instances[cls]
    return _zk_singleton


# def handle_exception(func):
# 
#     @functools.wraps(func)
#     def _handle_exception(*args, **kwargs):
#         ret = func(*args, **kwargs)
#         if isinstance(ret, tuple):
#             ret = "".join([ln for ln in traceback.format_exception(*ret)])
#             raise
#     return _handle_exception


default_executor =  ThreadPoolExecutor(10)


def run_on_executor(executor=default_executor):

    def run_on_executor_decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            task = Task(executor.submit, func, *args, **kwargs)
            return task
        return wrapper
    return run_on_executor_decorator


def run_callback(func):
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        callback = kwargs.pop('callback',None)
        assert callback
        try:
            res = func(*args, **kwargs)
        except:
            res = sys.exc_info()
        callback = stack_context.wrap(callback)
        IOLoop.instance().add_callback(lambda :callback(res))
    return wrapper