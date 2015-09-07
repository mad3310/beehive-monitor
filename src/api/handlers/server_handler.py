'''
Created on Sep 8, 2014

@author: root
'''
import logging

from tornado.web import asynchronous
from base import APIHandler
from container.containerOpers import Container_Opers
from server.serverOpers import Server_Opers
from resource_letv.serverResourceOpers import Server_Res_Opers
from utils.exceptions import HTTPAPIError
from tornado_letv.tornado_basic_auth import require_basic_auth


class ServerResHandler(APIHandler):

    _server_res_opers = Server_Res_Opers()
    _server_opers = Server_Opers()


class CollectServerResHandler(ServerResHandler):
    # eg. curl http://localhost:8888/server/resource
    def get(self):
        server_res = self._server_res_opers.retrieve_host_stat()
        self.finish(server_res)


class GatherServerCpuacctHandler(ServerResHandler):

    def get(self):
        cpu_info=self._server_res_opers.cpu_info()
        self.finish({"cpu":cpu_info})


class GatherServerMemoryHandler(ServerResHandler):

    def get(self):
        mem_res=self._server_res_opers.memory_stat()
        self.finish({"memory":mem_res})


class GatherServerDiskHandler(ServerResHandler):

    def get(self):
        server_disk=self._server_res_opers.disk_stat()
        self.finish({"disk":server_disk})


@require_basic_auth
class GatherServerContainersDiskLoadHandler(APIHandler):
    """get the disk container use server 
    
    """
    
    server_opers = Container_Opers()
    
    # eg. curl --user root:root -d "containerNameList=d-mcl-4_zabbix2-n-2" http://localhost:8888/server/containers/disk
    @asynchronous
    def post(self):
        args = self.get_all_arguments()
        containers = args.get('containerNameList')
        container_name_list = containers.split(',')
        if not (container_name_list and isinstance(container_name_list, list)):
            raise HTTPAPIError(status_code=417, error_detail="containerNameList is illegal!",\
                                notification = "direct", \
                                log_message= "containerNameList is illegal!",\
                                response =  "please check params!")
        
        host_ip = self.request.remote_ip
        
        result = self.server_opers.get_containers_disk_load(container_name_list)
        logging.debug('get disk load on this server:%s, result:%s' %( host_ip, str(result)) )
        self.finish(result)

