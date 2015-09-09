'''
Created on Sep 8, 2014

@author: root
'''
from base import APIHandler
from server.serverOpers import Server_Opers
from zk.zkOpers import Requests_ZkOpers


class ServerResHandler(APIHandler):

    server_opers = Server_Opers()
    zk_opers = Requests_ZkOpers()

    def get_server_resource(self, host_ip, resource_type):
        result = {}
        resource_value = self.zk_opers.retrieve_server_resource(
            host_ip, resource_type)
        result.setdefault(resource_type, resource_value)
        return result


class CollectServerResHandler(ServerResHandler):
    # eg. curl http://localhost:8888/server/resource

    def get(self):
        # not the method is deperacated
        #server_res = self.server_res_opers.retrieve_host_stat()
        # self.finish(server_res)
        pass


class GatherServerCpuacctHandler(ServerResHandler):

    def get(self, host_ip):
        result = self.get_server_resource(host_ip, 'cpu')
        self.finish(result)


class GatherServerMemoryHandler(ServerResHandler):

    def get(self, host_ip):
        result = self.get_server_resource(host_ip, 'memory')
        self.finish(result)


class GatherServerDiskHandler(ServerResHandler):

    def get(self, host_ip):
        result = self.get_server_resource(host_ip, 'disk')
        self.finish(result)
