# coding:utf-8
__author__ = 'mazheng'

from collections import namedtuple
from datetime import datetime

from container.containerOpers import Container_Opers
from docker_letv.dockerOpers import Docker_Opers
from zk.zkOpers import Scheduler_ZkOpers
from state.stateOpers import StateOpers
from utils import get_containerClusterName_from_containerName, get_container_type_from_container_name
from utils.es_utils import es_test_cluster as es_cluster
from daemon.containerResource import NetworkIO, DiskIO, CPURatio


class ContainerCache(dict):
    """
    加此Cache是为了避免资源采集任务频繁调用docker-py的接口从宿主机获取容器信息，
    由于决定一个容器是否需要采集有前置检查条件，前置检查需要连接zookeeper等开销
    较大的操作，借助此Cache可避免对检查过的容器进行再次检查。
    """
    __current_ids = set()
    old_ids = set()
    docker_op = Docker_Opers()
    Detail = namedtuple(
        'Detail', ['cluster_name', 'container_name', 'container_id'])

    def put(self, detail):
        self[detail.container_id] = detail

    def find_detail_by_id(self, container_id):
        return self.get(container_id)

    @property
    def current_ids(self):
        if not self.__current_ids:
            self.refresh()
        return self.__current_ids

    def refresh(self):
        self.old_ids = self.__current_ids
        self.__current_ids.clear()
        containers =  self.docker_op.containers()
        for c in containers:
            con_id = c.get('Id')
            # e.g. u'Names': [u'/d-esh-23_6_dwl_010-n-1']
            con_name = c.get('Names', ['/NoName'])[0][1:]
            clu_name = get_containerClusterName_from_containerName(con_name)
            self.__current_ids.add(con_id)
            self.put(self.Detail(clu_name, con_name, con_id))


class ContainerResourceHandler(object):

    con_op = Container_Opers()
    con_cache = ContainerCache()
    containers_diskio = {}
    containers_networkio = {}
    containers_cpuratio = {}

    def check_container_node_condition(self, container_node_detail):
        is_cluster_start = self.con_op.cluster_start(container_node_detail.cluster_name)
        is_container_name_legal = self.con_op.check_container_name_legal(container_node_detail.container_name)
        return container_node_detail and is_cluster_start and is_container_name_legal

    def get_container_nodes(self):
        """
        获取需要资源采集的容器信息。此处曾可能导致内存溢出，张增排查后并未
        改进代码。现移除原来的局部变量 container_nodes = [], 换用yield。
        """
        current_ids = self.con_cache.current_ids.copy()
        for con_id in current_ids:
            detail = self.con_cache.find_detail_by_id(con_id)
            # 若当前id不在上一次缓存列表中, 则进行检查
            # 否则在上一次缓存中，表示上一次已经检查过了
            # 此次不再进行检查，降低连接zookeeper等消耗
            if con_id not in self.con_cache.old_ids:
                # 则进行采集前置条件检查
                check_passed = self.check_container_node_condition(detail)
                # 若检查不通过, 将容器信息置为 None
                if not check_passed:
                    detail = None
            if detail is not None:
                yield detail
        del current_ids

    def write_to_es(self, resource_type, doc, es=es_cluster):
        _now = datetime.utcnow()
        _date = _now.strftime('%Y%m%d')
        _index = "monitor_container_resource_{0}_{1}".format(resource_type, _date)
        doc.update({
            'timestamp': _now
        })
        res = es.index(index=_index, doc_type=resource_type, body=doc)

    def gather(self):
        raise NotImplemented("this gather method should be implemented")


class ContainerCacheHandler(ContainerResourceHandler):

    def gather(self):
        self.con_cache.refresh()


class ContainerCPUAcctHandler(ContainerResourceHandler):

    def gather(self):
        container_nodes = self.get_container_nodes()
        res_type = 'cpuacct'
        for container_node in container_nodes:
            container_id = container_node.container_id
            if container_id not in self.containers_cpuratio:
                self.containers_cpuratio[container_id] = CPURatio(container_id)
            cpu_ratio = self.containers_cpuratio[container_id].get_result()
            node_name = self.con_op.get_container_node_from_container_name(
                        container_node.cluster_name, container_node.container_name)
            cpu_ratio.update({
                'cluster_name': container_node.cluster_name,
                'node_name': node_name
            })
            self.write_to_es(res_type, cpu_ratio)


class ContainerMemoryHandler(ContainerResourceHandler):

    def gather(self):
        container_nodes = self.get_container_nodes()
        res_type = 'memory'
        for container_node in container_nodes:
            state_op = StateOpers(container_node.container_name)
            memory = state_op.get_memory_stat_item()
            node_name = self.con_op.get_container_node_from_container_name(
                        container_node.cluster_name, container_node.container_name)
            memory.update({
                'cluster_name': container_node.cluster_name,
                'node_name': node_name
            })
            self.write_to_es(res_type, memory)


class ContainerDiskIOPSHandler(ContainerResourceHandler):

    def gather(self):
        container_nodes = self.get_container_nodes()
        res_type = 'diskiops'
        for container_node in container_nodes:
            is_vip_node = self.con_op.is_container_vip(container_node.container_name)
            if is_vip_node:
                continue
            container_id = container_node.container_id
            if container_id not in self.containers_diskio:
                container_type = get_container_type_from_container_name(container_node.container_name)
                self.containers_diskio[container_id] = DiskIO(container_id, container_type)
            disk_iops = self.containers_diskio[container_id].get_result()
            node_name = self.con_op.get_container_node_from_container_name(
                        container_node.cluster_name, container_node.container_name)
            disk_iops.update({
                'cluster_name': container_node.cluster_name,
                'node_name': node_name
            })
            self.write_to_es(res_type, disk_iops)


class ContainerDiskUsageHandler(ContainerResourceHandler):

    def gather(self):
        container_nodes = self.get_container_nodes()
        res_type = 'diskusage'
        for container_node in container_nodes:
            state_op = StateOpers(container_node.container_name)
            disk_usage = state_op.get_sum_disk_usage()
            node_name = self.con_op.get_container_node_from_container_name(
                        container_node.cluster_name, container_node.container_name)
            disk_usage.update({
                'cluster_name': container_node.cluster_name,
                'node_name': node_name
            })
            self.write_to_es(res_type, disk_usage)


class ContainerNetworkIOHandler(ContainerResourceHandler):

    def gather(self):
        container_nodes = self.get_container_nodes()
        res_type = 'networkio'
        for container_node in container_nodes:
            container_id = container_node.container_id
            if container_id not in self.containers_networkio:
                self.containers_networkio[
                    container_id] = NetworkIO(container_id)
            network_io = self.containers_networkio[container_id].get_result()
            node_name = self.con_op.get_container_node_from_container_name(
                        container_node.cluster_name, container_node.container_name)
            network_io.update({
                'cluster_name': container_node.cluster_name,
                'node_name': node_name
            })
            self.write_to_es(res_type, network_io)
