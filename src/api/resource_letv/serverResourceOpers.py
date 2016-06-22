#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
Created on Sep 8, 2014

@author: Wangzhen
'''
from datetime import datetime
import logging

from tornado.options import options

from componentProxy import component_mount_map
from container.containerOpers import Container_Opers
from daemon.serverResource import CPURatio
from docker_letv.dockerOpers import Docker_Opers
from utils import diskio
from utils.invokeCommand import InvokeCommand
from utils import getHostIp, disk_stat
from utils.es_utils import es_test_cluster
from zk.zkOpers import Common_ZkOpers, Scheduler_ZkOpers


class Server_Res_Opers():
    '''
    # TODO: 资源采集与写入分离，规划好接口， 重构一下?
    classdocs
    '''

    _logger = logging.getLogger("process_info")
    _logger.setLevel(logging.INFO)

    docker_opers = Docker_Opers()
    container_opers = Container_Opers()
    _server_cpu_ratio = CPURatio()

    def __init__(self, container_name=""):
        self.name = container_name
        if self.name != "":
            self.matrix_list = self.get_top_cmd_ret()
            self.id_pid_dict = self.get_container_id_pid_dict(self.name)

    def container_count(self):
        return len(self.container_opers.get_all_containers())

    def memory_stat(self):
        mem, stat = {}, {}
        f = open("/proc/meminfo", "r")
        lines = f.readlines()
        f.close()
        for line in lines:
            if len(line) < 2:
                continue
            name = line.split(':')[0]
            var = line.split(':')[1].split()[0]
            mem[name] = long(var) * 1024.0
        stat['total'] = int(mem['MemTotal'] / (1024 * 1024))
        stat['used'] = int(mem['MemTotal'] - mem['MemFree'] -
                           mem['Buffers'] - mem['Cached']) / (1024 * 1024)
        stat['free'] = int(mem['MemFree'] + mem['Buffers'] +
                           mem['Cached']) / (1024 * 1024)
        return stat

    def disk_iops(self):
        mountpoints = ('/srv/docker/vfs', '/srv')
        result = diskio.iops(mountpoints)
        return result

    def srv_disk_stat(self):
        """
        @todo:  监控所有磁盘和分区
        """
        result = disk_stat('/srv/docker/vfs')
        return result

    def disk_loadavg(self):
        loadavg = {}
        f = open("/proc/loadavg", "r")
        con = f.read().split()
        f.close()
        loadavg['lavg_1'] = con[0]
        loadavg['lavg_5'] = con[1]
        loadavg['lavg_15'] = con[2]
        loadavg['nr'] = con[3]
        loadavg['last_pid'] = con[4]
        self._logger.info("disk io information: " + str(loadavg))
        return loadavg

    def cpu_ratio(self):
        return self._server_cpu_ratio.get_result()

    @property
    def server_cpu_ratio(self):
        return self._server_cpu_ratio


class ServerResourceHandler(object):

    ip = getHostIp()
    server_res_opers = Server_Res_Opers()

    def gather(self):
        raise NotImplementedError("the gather method must be implemented")

    def write_to_zookeeper(self, tp, value):
        zk_op = Scheduler_ZkOpers()
        zk_op.write_server_resource(self.ip, tp, value)

    def write_to_es(self, resource_type, doc, es=es_test_cluster):
        _now = datetime.now()
        _date = _now.strftime('%Y%m%d')
        _index = "monitor_server_resource_{0}_{1}".format(resource_type, _date)
        doc.update({
            'ip': self.ip,
            'timestamp': _now
        })
        res = es.index(index=_index, doc_type=resource_type, body=doc)


class ServerCPUHandler(ServerResourceHandler):

    def gather(self):
        cpu_ratio = self.server_res_opers.cpu_ratio()
        self.write_to_zookeeper("cpu", cpu_ratio)
        self.write_to_es("cpu", cpu_ratio)


class ServerMemoryHandler(ServerResourceHandler):

    def gather(self):
        memory_stat = self.server_res_opers.memory_stat()
        self.write_to_zookeeper("memory", memory_stat)
        self.write_to_es("memory", memory_stat)


"""
    @todo: server disk
"""
class ServerDiskusageHandler(ServerResourceHandler):

    def gather(self):
        disk_stat = self.server_res_opers.srv_disk_stat()
        self.write_to_zookeeper("diskusage", disk_stat)
        self.write_to_es("diskusage", disk_stat)


class ServerDiskiopsHandler(ServerResourceHandler):

    def gather(self):
        disk_iops = self.server_res_opers.disk_iops()
        self.write_to_zookeeper("diskiops", disk_iops)
        self.write_to_es("diskiops", disk_iops)


class ContainerCountHandler(ServerResourceHandler):

    def gather(self):
        container_count = self.server_res_opers.container_count()
        self.write_to_zookeeper("container_count", container_count)
        self.write_to_es("container_count", {'container_count': container_count})
