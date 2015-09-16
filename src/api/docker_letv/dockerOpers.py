'''
Created on Sep 8, 2014

@author: root
'''
import json
import logging

from utils import _get_property_dict
from docker import Client as client
from utils.exceptions import CommonException


class Docker_Opers(client):
    '''
    classdocs
    '''
    client = client()

    def __init__(self):
        super(Docker_Opers, self).__init__(
            base_url='unix://var/run/docker.sock')
        self.image_cache = []
        self.log = logging.getLogger(__name__)

    def containers(self, quiet=False, all=False, trunc=True, latest=False,
                   since=None, before=None, limit=-1, size=False):
        return self.client.containers(quiet,
                                      all,
                                      trunc,
                                      latest,
                                      since,
                                      before,
                                      limit,
                                      size)

    def inspect_container(self, container):
        return self.client.inspect_container(container)

    '''
    @todo: need test
    '''

    def retrieve_containers_ids(self):
        containers_info = self.containers()
        id_list = []
        for container_iter in containers_info:
            id_list.append(container_iter['Id'])
        return id_list

    '''
    @todo: need test
    '''

    def retrieve_containers_ips(self):
        container_id_list = self.retrieve_containers_ids()
        ip_list = []
        for container_id_iter in container_id_list:
            env = self.inspect_container(container_id_iter)['Config']['Env']
            for item in env:
                if item.startswith("IP="):
                    ip_list.append(item.split("=")[1])
        return ip_list

    def image_name_list(self):
        image_list = []
        images = self.client.images()
        for image in images:
            for k, v in image.items():
                if k == 'RepoTags':
                    image_list.extend(v)
        return image_list

    def image_id_list(self):
        return self.client.images(quiet=True)

    def image_exist(self, image):
        image_list = self.image_name_list()
        return image in image_list

    def tag(self, image):
        parts = image.split(':')
        if len(parts) == 1:
            repo = parts[0]
            tag = 'latest'
        elif len(parts) == 2:
            repo = parts[0]
            tag = parts[1]
        else:
            repo = ':'.join(parts[:-1])
            tag = parts[-1]
        return (repo, tag)

if __name__ == '__main__':
    d = Docker_Opers()
    print d.inspect_container('d-mcl-djimlwy-n-1')
