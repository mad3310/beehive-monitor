#-*- coding: utf-8 -*-
import base64

from utils.configFileOpers import ConfigFileOpers
from base import APIHandler
from tornado.options import options


class AdminConf(APIHandler):

    confOpers = ConfigFileOpers()

    def post(self):
        '''
        function: admin conf
        url example: curl -d "zkAddress=127.0.0.1&zkPort=2181" "http://localhost:8888/admin/conf"
        '''
        requestParam = self.get_all_arguments()
        if requestParam != {}:
            self.confOpers.setValue(
                options.container_manager_property, requestParam)

        result = {}
        result.setdefault("message", "admin conf successful!")
        self.finish(result)


# create admin user
# eg. curl -d "adminUser=root&adminPassword=root"
# "http://localhost:8888/admin/user"
class AdminUser(APIHandler):

    confOpers = ConfigFileOpers()

    def post(self):
        requestParam = {}
        args = self.request.arguments
        for key in args:
            value = args[key][0]
            if key == 'adminPassword':
                value = base64.encodestring(value).strip('\n')
            requestParam.setdefault(key, value)

        if requestParam != {}:
            self.confOpers.setValue(
                options.server_cluster_property, requestParam)

        return_message = {}
        return_message.setdefault("message", "creating admin user successful!")
        self.finish(return_message)
