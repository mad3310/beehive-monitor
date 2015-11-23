'''
Created on Sep 8, 2014

@author: root
'''
from tornado.web import asynchronous
from tornado.gen import engine
from utils.decorators import run_on_executor, run_callback

from base import APIHandler
from server.serverOpers import Server_Opers
from zk.zkOpers import Requests_ZkOpers
from utils.exceptions import HTTPAPIError


class ServerResHandler(APIHandler):

    server_opers = Server_Opers()

    def check_host_ip(self, host_ip):
        exist = self.server_opers.host_exist(host_ip)
        if not exist:
            error_message = 'server %s not exist, please check your server ip' % host_ip
            raise HTTPAPIError(status_code=417, error_detail=error_message,
                               notification="direct",
                               log_message=error_message,
                               response=error_message)

    @staticmethod
    def get_server_resource(host_ip, resource_type):
        zk_opers = Requests_ZkOpers()
        result = {}
        resource_value = zk_opers.retrieve_server_resource(
            host_ip, resource_type)
        result.setdefault(resource_type, resource_value)
        return result

    @asynchronous
    @engine
    def get(self, host_ip, resource_type):
        result = yield self.do(host_ip, resource_type)
        self.finish(result)

    @run_on_executor()
    @run_callback
    def do(self, host_ip, resource_type):
        return self.get_server_resource(host_ip, resource_type)


class GatherServerCpuHandler(ServerResHandler):

    def get(self, host_ip):
        super(GatherServerCpuHandler, self).get(host_ip, 'cpu')


class GatherServerMemoryHandler(ServerResHandler):

    def get(self, host_ip):
        super(GatherServerMemoryHandler, self).get(host_ip, 'memory')


class GatherServerDiskHandler(ServerResHandler):

    def get(self, host_ip):
        super(GatherServerDiskHandler, self).get(host_ip, 'disk')

