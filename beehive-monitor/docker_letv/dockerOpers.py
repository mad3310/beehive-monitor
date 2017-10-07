'''
Created on Sep 8, 2014

@author: root
'''

import logging

from docker import Client


class Docker_Opers(Client):
    '''
    classdocs
    '''
    def __init__(self):
        super(Docker_Opers, self).__init__(
            base_url='unix://var/run/docker.sock')
        self.image_cache = []
        self.log = logging.getLogger(__name__)

    def retrieve_containers_ids(self):
        return [c['Id'] for c in self.containers()]

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
        return [i for s in self.images() for i in s.get('RepoTags')]

    def image_id_list(self):
        return self.images(quiet=True)

    def image_exist(self, image_name):
        return image_name in self.image_name_list()

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
