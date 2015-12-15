__author__ = 'mazheng'

from collections import namedtuple

from container.containerOpers import Container_Opers
from docker_letv.dockerOpers import Docker_Opers
from zk.zkOpers import Scheduler_ZkOpers
from state.stateOpers import StateOpers
from utils import get_containerClusterName_from_containerName, get_container_type_from_container_name
from daemon.containerResource import NetworkIO, DiskIO, CPURatio


ContainerNode = namedtuple(
    'ContainerNode', ['cluster_name', 'container_name', 'node_name', 'container_id'])


class ContainerCache(object):

    def __init__(self):
        self.init()
        self.from_cache = set()
        self.to_cache = set()
        self.docker_op = Docker_Opers()
        self.con_op = Container_Opers()
        self.db = {}

    def init(self):
        current_container_ids = self.current_container_ids
        self.from_cache.update(current_container_ids)
        self.to_cache.update(current_container_ids)

    def get_container_detail_by_id(self, container_id):
        return self.db.get(container_id)

    @property
    def current_container_ids(self, is_all=False):
        containers_list = []
        containers = self.docker_op.containers(is_all)
        for container in containers:
            container_id = container.get('Id').replace('/', '')
            container_name = container.get('Names')[0].replace('/', '')
            cluster_name = get_containerClusterName_from_containerName(
                container_name)
            node_name = self.con_op.get_container_node_from_container_name(
                cluster_name, container_name)
            containers_list.append(container_id)
            self.db.update({container_id: ContainerNode._make(
                (cluster_name, container_name, node_name, container_id))})
        return containers_list

    @property
    def new_container_ids(self):
        return self.from_cache - self.to_cache

    def update(self):
        self.update_from_cache()
        self.update_to_cache()

    def update_from_cache(self):
        self.from_cache = set()
        self.from_cache.update(self.current_container_ids)

    def update_to_cache(self):
        self.to_cache = self.to_cache - (self.to_cache - self.from_cache)

    def add_valid_id(self, container_id):
        self.to_cache.add(container_id)

    @property
    def current_valid_ids(self):
        return self.to_cache


class ContainerResourceHandler(object):

    con_op = Container_Opers()

    container_cache = ContainerCache()

    containers_diskio = {}
    containers_networkio = {}
    containers_cpuratio = {}


    def add_container_node_condition(self, container_node_detail):
        is_cluster_start = self.con_op.cluster_start(container_node_detail.cluster_name)
        is_container_name_legal = self.con_op.check_container_name_legal(container_node_detail.container_name)
        return container_node_detail and is_cluster_start and is_container_name_legal

    def get_container_nodes(self):
        container_nodes = []
        for container_id in self.container_cache.current_valid_ids:
            container_node_detail = self.container_cache.get_container_detail_by_id(
                container_id)
            container_nodes.append(container_node_detail)

        for container_id in self.container_cache.new_container_ids:
            container_node_detail = self.container_cache.get_container_detail_by_id(
                container_id)
            if self.add_container_node_condition(container_node_detail):
                self.container_cache.add_valid_id(container_id)
                container_nodes.append(container_node_detail)

        return container_nodes

    def write_to_zookeeper(self, cluster_name, container_node, resource_type, resource_value):
        zk_op = Scheduler_ZkOpers()
        zk_op.write_container_resource(
            cluster_name, container_node, resource_type, resource_value)

    def gather(self):
        raise NotImplemented("this gather method should be implemented")


class ContainerCacheHandler(ContainerResourceHandler):

    def gather(self):
        self.container_cache.update()


class ContainerCPUAcctHandler(ContainerResourceHandler):

    def gather(self):
        container_nodes = self.get_container_nodes()
        for container_node in container_nodes:
            container_id = container_node.container_id
            if container_id not in self.containers_cpuratio:
                self.containers_cpuratio[container_id] = CPURatio(container_id)
            cpu_ratio = self.containers_cpuratio[container_id].get_result()
            self.write_to_zookeeper(
                container_node.cluster_name, container_node.node_name, 'cpuacct', cpu_ratio)


class ContainerMemoryHandler(ContainerResourceHandler):

    def gather(self):
        container_nodes = self.get_container_nodes()
        for container_node in container_nodes:
            state_op = StateOpers(container_node.container_name)
            memory = state_op.get_memory_stat_item()
            self.write_to_zookeeper(
                container_node.cluster_name, container_node.node_name, 'memory', memory)


class ContainerDiskIOPSHandler(ContainerResourceHandler):

    def gather(self):
        container_nodes = self.get_container_nodes()
        for container_node in container_nodes:
            container_id = container_node.container_id
            if container_id not in self.containers_diskio:
                container_type = get_container_type_from_container_name(container_node.container_name)
                self.containers_diskio[container_id] = DiskIO(container_id, container_type)
            disk_iops = self.containers_diskio[container_id].get_result()
            self.write_to_zookeeper(
                container_node.cluster_name, container_node.node_name, 'diskiops', disk_iops)


class ContainerDiskUsageHandler(ContainerResourceHandler):

    def gather(self):
        container_nodes = self.get_container_nodes()
        for container_node in container_nodes:
            state_op = StateOpers(container_node.container_name)
            disk_usage = state_op.get_sum_disk_usage()
            self.write_to_zookeeper(
                container_node.cluster_name, container_node.node_name, 'diskload', disk_usage)


class ContainerNetworkIOHandler(ContainerResourceHandler):

    def gather(self):
        container_nodes = self.get_container_nodes()
        for container_node in container_nodes:
            container_id = container_node.container_id
            if container_id not in self.containers_networkio:
                self.containers_networkio[
                    container_id] = NetworkIO(container_id)
            network_io = self.containers_networkio[container_id].get_result()
            self.write_to_zookeeper(
                container_node.cluster_name, container_node.node_name, 'networkio', network_io)
