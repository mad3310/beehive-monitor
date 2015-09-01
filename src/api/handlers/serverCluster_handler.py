#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
Created on Sep 8, 2014

@author: root
'''
import json
import logging
import urllib

from tornado.options import options
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.web import asynchronous
from tornado.gen import engine, Task
from tornado_letv.tornado_basic_auth import require_basic_auth
from utils import _retrieve_userName_passwd
from utils.exceptions import HTTPAPIError
from base import APIHandler
from zk.zkOpers import Requests_ZkOpers


@require_basic_auth
class GatherServersContainersDiskLoadHandler(APIHandler):
    
    @asynchronous
    @engine
    def post(self):
        args = self.get_all_arguments()
        containers = args.get('containerNameList')
        logging.info('get servers containers disk load method, containerNameList:%s' % str(containers) )
        container_name_list = containers.split(',')
        if not (container_name_list and isinstance(container_name_list, list)):
            raise HTTPAPIError(status_code=417, error_detail="containerNameList is illegal!",\
                                notification = "direct", \
                                log_message= "containerNameList is illegal!",\
                                response =  "please check params!")
        
        zkOper = Requests_ZkOpers()
        server_list = zkOper.retrieve_servers_white_list()
        auth_username, auth_password = _retrieve_userName_passwd()
        async_client = AsyncHTTPClient()
        servers_cons_disk_load, cons_disk_load = {}, {}
        try:
            for server in server_list:
                requesturi = 'http://%s:%s/server/containers/disk' % (server, options.port)
                logging.info('server requesturi: %s' % str(requesturi))
                request = HTTPRequest(url=requesturi, method='POST', body=urllib.urlencode(args), connect_timeout=40, \
                                      request_timeout=40, auth_username = auth_username, auth_password = auth_password)
                
                response = yield Task(async_client.fetch, request)
                body = json.loads(response.body.strip())
                logging.info('response body : %s' % str(body))
                cons_disk_load = body.get('response')
                servers_cons_disk_load.update(cons_disk_load)
        finally:
            async_client.close()
        
        except_cons = list(set(container_name_list) - set(servers_cons_disk_load.keys()))
        for con in except_cons:
            servers_cons_disk_load.setdefault(con, 'no such container or code exception')
        self.finish( servers_cons_disk_load )