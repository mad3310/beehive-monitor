#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
Created on Sep 8, 2014

@author: Wangzhen
'''

import os
import time
import logging
import docker

from utils.invokeCommand import InvokeCommand
from docker_letv.dockerOpers import Docker_Opers
from container.containerOpers import Container_Opers
from zk.zkOpers import Common_ZkOpers, Scheduler_ZkOpers
from utils import getHostIp
from daemon.serverResource import CPURatio


class Server_Res_Opers():
    '''
    classdocs
    '''

    docker_c = docker.Client(base_url='unix://var/run/docker.sock')
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

    def retrieve_host_stat(self):
        resource = {}

        mem_res_info = self.memory_stat()
        resource.setdefault("mem_res", mem_res_info)

        server_disk = self.disk_stat()
        resource.setdefault("server_disk", server_disk)

        containers = self.container_opers.get_all_containers()
        resource.setdefault("container_number", len(containers))

        zk_opers = Common_ZkOpers()
        host_ip = getHostIp()
        ports = zk_opers.get_ports_from_portPool(host_ip)
        resource.setdefault("port_number", len(ports))
        return resource

    def get_proc_stat_path(self, pid):
        _path = "/proc/%s/stat" % (str(pid))
        return _path

    def get_proc_net_path(self, pid):
        _path = "/proc/%s/net/netstat" % (str(pid))
        return _path

    def get_page_size(self):
        _path = "/proc/meminfo"
        f = open(_path, "r")
        lines = f.readlines()

        mapped_size = 0
        for line in lines:
            list = line.split(":")
            if list[0] == "Mapped":
                mapped_size = int(list[1].strip().replace("kB", ""))
                break
        f.close()

        _path = "/proc/vmstat"
        f = open(_path, "r")
        lines = f.readlines()

        # print lines
        nr_mapped = 0
        for line in lines:
            list = line.split(" ")
            if list[0] == "nr_mapped":
                nr_mapped = int(list[1].rstrip())
                break
        f.close()
        self._logger.info("Page size is %s" % str(mapped_size / nr_mapped))
        return mapped_size / nr_mapped



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

    def disk_stat(self):
        """
        just for container
        """
        hd = {}
        disk = os.statvfs("/srv")
        hd['free'] = disk.f_bsize * disk.f_bavail / (1024 * 1024)
        hd['total'] = disk.f_bsize * disk.f_blocks / (1024 * 1024)
        hd['used'] = hd['total'] - hd['free']
        return hd

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

    def get_dev_name(self):
        invokeCmd = InvokeCommand()
        _shell = "df -h"
        ret_sub_p = invokeCmd._runSysCmd(_shell)
        contents_list = ret_sub_p[0].split()
        self._logger.info(str(contents_list))
        srv_index = contents_list.index("/srv")

        dev_name = contents_list[srv_index - 5]
        self._logger.info(str(dev_name))

        return dev_name

    def disk_instant_load(self):
        mount_dev = self.get_dev_name()
        invokeCmd = InvokeCommand()
        _shell = "iostat -dxk %s 2 2" % (mount_dev)
        self._logger.info(str(_shell))
        ret_sub_p = invokeCmd._runSysCmd(_shell)
        contents_list = ret_sub_p[0].split()
        w_kb_s = float(contents_list[-6])
        r_kb_s = float(contents_list[-7])
        per_kb_s = (w_kb_s + r_kb_s)
        return per_kb_s

    def cpu_info(self):
        cpu = []
        cpuinfo = {}
        f = open("/proc/cpuinfo", "r")
        lines = f.readlines()
        f.close()
        for line in lines:
            if line == '\n':
                cpu.append(cpuinfo)
                cpuinfo = {}
            if len(line) < 2:
                continue
            name = line.split(':')[0].rstrip()
            var = line.split(':')[1].rstrip()
            cpuinfo[name] = var
        #self._logger.info("cpu information :" + str(cpu))
        return cpu

    def cpu_ratio(self):
        return self._server_cpu_ratio.get_result()

    @property
    def server_cpu_ratio(self):
        return self._server_cpu_ratio

    def _read_network_statics(self):
        """Read the current network statics from /proc/net/dev """
        try:
            fd = open("/proc/net/dev", "r")
            lines = fd.readlines()
        finally:
            if fd:
                fd.close()
        sum1 = 0.0
        for line in lines:
            list = line.split(':')
            if len(list) == 1:
                continue
            sum1 += long(list[1].split()[0])
            sum1 += long(list[1].split()[8])
        return sum1

    def get_top_cmd_ret(self):
        invokeCmd = InvokeCommand()
        # _shell = options.pid_children + " " + str(ppid)
        _shell = "top -b -n1 |sort -n "

        ret = invokeCmd._runSysCmd(_shell)
        set_str = ret[0]
        # print set_str
        set_list = set_str.split()
        # print set_list
        ave_p = [item for item in range(len(set_list)) if set_list[
            item] == 'average:']
        start_p = ave_p[0] + 4
        # print set_list[start_p]

        top_matrix_list = list(set_list[start_p:])
        # print matrix_list
        # print len(matrix_list)
        return top_matrix_list

    def search_pid_family_info(self, pid=1):
        children_pid_list = self.get_container_children_pid(pid)
        rss_mm = 0.0
        cpu_percent = 0.0

        info_dict = {}
        info_dict = (self.search_pid_info(int(pid)))
        rss_mm += info_dict["pid_rss_memory"]
        cpu_percent += info_dict["pid_cpu_usage"]

        for child in children_pid_list:
            # print self.search_pid_info(int(child))
            info_dict = (self.search_pid_info(int(child)))
            if info_dict != None:
                rss_mm += info_dict["pid_rss_memory"]
                cpu_percent += info_dict["pid_cpu_usage"]
            else:
                pass

        dict = {}
        dict.setdefault("total_rss", rss_mm)
        dict.setdefault("total_cpu_percent", cpu_percent)
        return dict

    def search_pid_info(self, pid=1):
        N = 12
        group_n = len(self.matrix_list) / 12

        start = 0
        middle = group_n / 2
        end = group_n - 1

        while (pid != int(self.matrix_list[middle * N]) and (middle != start) and (middle != end)):
            if pid < int(self.matrix_list[middle * N]):
                end = middle
                middle = (start + middle) / 2

            else:
                start = middle
                middle = (middle + end) / 2

        if pid != int(self.matrix_list[middle * N]):
            pass
        else:
            dict = {}

            name = "pid_%s" % str(pid)
            dict.setdefault(name, pid)
            str_rss = self.matrix_list[middle * N + 5]
            if "m" in str_rss:
                _rss = str_rss.replace("m", "")
                str_rss = str(float(_rss) * 1024)
            dict.setdefault("pid_rss_memory", float(str_rss))
            dict.setdefault("pid_cpu_usage", float(
                self.matrix_list[middle * N + 8]))

            return dict

    def get_cur_cpu_usage(self):
        invokeCmd = InvokeCommand()
        _shell = "vmstat 1 2"
        ret = invokeCmd._runSysCmd(_shell)
        pid_str = ret[0]
        pid_list = pid_str.strip().split()
        id = pid_list[-3]
        return id

    def get_cur_net_load(self):
        """
        get net average statics of work load in 2 seconds
        """
        n1 = self._read_network_statics()
        time.sleep(0.1)
        n2 = self._read_network_statics()
        avg_load = (n2 - n1) / 1024
        self._logger.info(
            "network load per second at this time:" + str(avg_load))
        return avg_load


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


class ServerDiskHandler(ServerResourceHandler):

    def gather(self):
        disk_stat = self.server_res_opers.disk_stat()
        self.write_to_zookeeper("disk", disk_stat)
