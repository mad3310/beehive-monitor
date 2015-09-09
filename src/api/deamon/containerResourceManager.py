__author__ = 'mazheng'

from tornado.options import options

from utils.invokeCommand import InvokeCommand
from deamon.containerResource import NetworkIO, DiskIO
from docker_letv.dockerOpers import Docker_Opers


class ContainerResourceManager(object):

    def __init__(self):
        self.docker = Docker_Opers()
        self.container_ids = []
        self.network_ios = {}
        self.disk_ios = {}
        self.dev_number = 0
        self.initialize()

    def initialize(self):
        containers = self.docker.containers(all=False)
        for container in containers:
            _id = container.get('Id')
            self.container_ids.append(_id)

        for container_id in self.container_ids:
            self.add_container_resource(container_id)

    def add_container_resource(self, container_id):
        self.network_ios[container_id] = NetworkIO()
        self.disk_ios[container_id] = DiskIO()

    def init_dev_number(self):
        ivk_cmd = InvokeCommand()
        cmd = "sh %s %s" % (options.disk_number_sh, "/srv")
        self.dev_number = ivk_cmd._runSysCmd(cmd)[0]

    def start(self):
        self.init_dev_number()
        for _id in self.container_ids:
            self.start_container(_id)

    def start_container(self, container_id):
        self.network_ios[container_id].run_cycle_time(1, container_id)
        self.disk_ios[container_id].run_cycle_time(
            1, self.dev_number, container_id)

    def remove_container(self, container_id):
        self.container_ids.remove(container_id)
        del self.disk_ios[container_id]
        del self.network_ios[container_id]

    def close(self):
        self.network_ios.clear()
        self.disk_ios.clear()


containerResourceManager = ContainerResourceManager()


def get_disk_iops(container_id):
    result = {}
    disk_io = containerResourceManager.disk_ios[container_id]
    result['read'] = disk_io.read_iops
    result['write'] = disk_io.write_iops
    return result


def get_network_io(container_id):
    result = {}
    network_io = containerResourceManager.network_ios[container_id]
    result['rx'] = network_io.rx
    result['tx'] = network_io.tx
    return result
