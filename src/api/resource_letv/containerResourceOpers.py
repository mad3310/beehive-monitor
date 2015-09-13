__author__ = 'mazheng'

from collections import namedtuple

from container.containerOpers import Container_Opers
from docker_letv.dockerOpers import Docker_Opers
from zk.zkOpers import Scheduler_ZkOpers
from state.stateOpers import StateOpers
from utils import get_containerClusterName_from_containerName
from daemon.containerResource import NetworkIO, DiskIO, CPURatio


class ContainerResourceHandler(object):

    ContainerNode = namedtuple(
        'ContainerNode', ['cluster_name', 'container_name', 'node_name', 'container_id'])
    con_op = Container_Opers()
    doker_op = Docker_Opers()

    containers_diskio = {}
    containers_networkio = {}
    containers_cpuratio = {}

    def get_container_nodes(self, is_all=False):
        containers = self.doker_op.containers(is_all)
        container_nodes = []
        for container in containers:
            container_name = container.get('Names')[0].replace('/', '')
            container_id = container.get('Id').replace('/', '')
            cluster_name = get_containerClusterName_from_containerName(
                container_name)
            node_name = self.con_op.get_container_node_from_container_name(
                cluster_name, container_name)
            container_nodes.append(self.ContainerNode._make(
                (cluster_name, container_name, node_name, container_id)))
        return container_nodes

    def write_to_zookeeper(self, cluster_name, container_node, resource_type, resource_value):
        zk_op = Scheduler_ZkOpers()
        zk_op.write_container_resource(
            cluster_name, container_node, resource_type, resource_value)

    def gather(self):
        raise NotImplemented("this gather method should be implemented")


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
                self.containers_diskio[container_id] = DiskIO(container_id)
            disk_iops = self.containers_diskio[container_id].get_result()
            self.write_to_zookeeper(
                container_node.cluster_name, container_node.node_name, 'diskiops', disk_iops)


class ContainerDiskLoadHandler(ContainerResourceHandler):

    def gather(self):
        container_nodes = self.get_container_nodes()
        for container_node in container_nodes:
            state_op = StateOpers(container_node.container_name)
            disk_iops = state_op.get_sum_disk_load()
            self.write_to_zookeeper(
                container_node.cluster_name, container_node.node_name, 'diskload', disk_iops)


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
