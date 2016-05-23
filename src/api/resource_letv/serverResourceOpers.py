#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
Created on Sep 8, 2014

@author: Wangzhen
'''

import logging
import time

from tornado.options import options

from componentProxy import component_mount_map
from container.containerOpers import Container_Opers
from daemon.serverResource import CPURatio
from docker_letv.dockerOpers import Docker_Opers
from utils import diskio
from utils.invokeCommand import InvokeCommand
from utils import getHostIp, disk_stat
from zk.zkOpers import Common_ZkOpers, Scheduler_ZkOpers


class Server_Res_Opers():
    '''
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
        disks_before = diskio.stats()
        time.sleep(1)
        disks_after = diskio.stats()
        retdic = {}
        # mcluster组件所在的挂载点
        # TODO: 只获取mcluster组件的磁盘io而不是该服务器的所有磁盘io吗？
        mountponit = component_mount_map.get('mcl', '/srv/docker/vfs')
        partitions = diskio.parse_lsblk()
        # 根据挂载点获取磁盘内核名称
        part = None
        for p in partitions:
            if p.get('mountpoint', '') == mountponit:
                part = p.get('kname')
                break
        if part:
            disks_read_per_sec = disks_after[part].read_bytes - \
                disks_before[part].read_bytes
            disks_write_per_sec = disks_after[part].write_bytes - \
                disks_before[part].write_bytes
            io_read_for_human = diskio.bytes2human(disks_read_per_sec)
            io_write_for_human = diskio.bytes2human(disks_write_per_sec)
            retdic = {'read_iops': io_read_for_human,
                      'write_iops': io_write_for_human}
        return retdic

    def srv_disk_stat(self):
        """
        @todo:  need to fix, make sure which path
        """
        result = disk_stat("/srv")
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

#     def cpu_info(self):
#         cpu = []
#         cpuinfo = {}
#         f = open("/proc/cpuinfo", "r")
#         lines = f.readlines()
#         f.close()
#         for line in lines:
#             if line == '\n':
#                 cpu.append(cpuinfo)
#                 cpuinfo = {}
#             if len(line) < 2:
#                 continue
#             name = line.split(':')[0].rstrip()
#             var = line.split(':')[1].rstrip()
#             cpuinfo[name] = var
#         #self._logger.info("cpu information :" + str(cpu))
#         return cpu

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


class ServerCPUHandler(ServerResourceHandler):

    def gather(self):
        cpu_ratio = self.server_res_opers.cpu_ratio()
        self.write_to_zookeeper("cpu", cpu_ratio)


class ServerMemoryHandler(ServerResourceHandler):

    def gather(self):
        memory_stat = self.server_res_opers.memory_stat()
        self.write_to_zookeeper("memory", memory_stat)


"""
    @todo: server disk
"""
class ServerDiskHandler(ServerResourceHandler):

    def gather(self):
        disk_stat = self.server_res_opers.srv_disk_stat()
        self.write_to_zookeeper("disk", disk_stat)


class ServerDiskiopsHandler(ServerResourceHandler):

    def gather(self):
        disk_iops = self.server_res_opers.disk_iops()
        self.write_to_zookeeper("diskiops", disk_iops)


class ContainerCountHandler(ServerResourceHandler):

    def gather(self):
        container_count = self.server_res_opers.container_count()
        self.write_to_zookeeper("container_count", container_count)
