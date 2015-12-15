#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
Created on Sep 8, 2014

@author: Wangzhen
'''

import os
import logging

from tornado.options import options
from utils.invokeCommand import InvokeCommand
from docker_letv.dockerOpers import Docker_Opers
from container.containerOpers import Container_Opers
from zk.zkOpers import Common_ZkOpers, Scheduler_ZkOpers
from utils import getHostIp, disk_stat
from daemon.serverResource import CPURatio


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

    def disk_io(self):
        result={}
        iops={}
        ivk_cmd=InvokeCommand()
        cmd = "sh %s %s" % (options.disk_io_sh,"/srv/docker/vfs")
        content=ivk_cmd._runSysCmd(cmd)[0]
        iopses=content.split()
        if len(iopses)==2:
            iops['read']=float(iopses[0])
            iops['write']=float(iopses[1])
        else:
            iops['read']=iops['write']=0
        result['iops']=iops
        return result

    def srv_disk_stat(self):
        """
        @todo:  need to fix, make sure which path
        """
        result = disk_stat("/srv") / (1024*1024)
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


"""
@todo: server diskio 
"""
class ServerDiskioHandler(ServerResourceHandler):

    def gather(self):
        disk_stat = self.server_res_opers.disk_io()
        self.write_to_zookeeper("diskio", disk_stat)


class ContainerCountHandler(ServerResourceHandler):

    def gather(self):
        container_count = self.server_res_opers.container_count()
        self.write_to_zookeeper("container_count", container_count)
