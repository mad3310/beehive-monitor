#-*- coding: utf-8 -*-

'''
Created on 2013-7-21

@author: asus
'''
from tornado.web import asynchronous
from tornado.gen import engine
from utils.decorators import run_on_executor, run_callback

from base import APIHandler
from zk.zkOpers import Requests_ZkOpers


# retrieve the status value of all monitor type
# eg. curl "http://localhost:6666/mcluster/status"
class ContainerStatus(APIHandler):

    @asynchronous
    @engine
    def get(self):
        result = yield self.do()
        self.finish(result)

    @run_on_executor()
    @run_callback
    def do(self):
        zkOper = Requests_ZkOpers()
        monitor_types = zkOper.retrieve_monitor_type()
        stat_dict = {}
        for monitor_type in monitor_types:
            monitor_status_list = zkOper.retrieve_monitor_status_list(monitor_type)

            monitor_type_sub_dict = {}
            for monitor_status_key in monitor_status_list:
                monitor_status_value = zkOper.retrieve_monitor_status_value(monitor_type, monitor_status_key)
                monitor_type_sub_dict.setdefault(monitor_status_key, monitor_status_value)

            stat_dict.setdefault(monitor_type, monitor_type_sub_dict)
        return stat_dict
