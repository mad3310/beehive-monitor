'''
Created on Apr 5, 2015

@author: root
'''

import re

from docker_letv.dockerOpers import Docker_Opers
from container.container_model import Container_Model
from utils import calc_dir_size, get_container_type_from_container_name, disk_stat, timestamp
from componentProxy import component_mount_map


class StateOpers(object):

    docker_opers = Docker_Opers()

    def __init__(self, container_name):
        self.container_name = container_name
        self.container_id = ''
        if not self.container_id:
            self.container_id = self.get_container_id()
        self.used_mem_path = '/cgroup/memory/lxc/%s/memory.usage_in_bytes' % self.container_id
        self.limit_mem_path = '/cgroup/memory/lxc/%s/memory.limit_in_bytes' % self.container_id
        self.used_memsw_path = '/cgroup/memory/lxc/%s/memory.memsw.usage_in_bytes' % self.container_id
        self.limit_memsw_path = '/cgroup/memory/lxc/%s/memory.memsw.limit_in_bytes' % self.container_id
        self.under_oom_path = '/cgroup/memory/lxc/%s/memory.oom_control' % self.container_id
        self.root_mnt_path = '/srv/docker/devicemapper/mnt/%s' % self.container_id
        self.memory_stat_path = '/cgroup/memory/lxc/%s/memory.stat' % self.container_id
        self.cpuacct_stat_path = '/cgroup/cpuacct/lxc/%s/cpuacct.stat' % self.container_id
        self.cpushares_path = '/cgroup/cpu/lxc/%s/cpu.shares' % self.container_id
        self.cpuset_path = '/cgroup/cpu/lxc/%s/cpuset.cpus' % self.container_id
        self.mount_disk = self.get_container_mount_disk()

    '''
    @todo: need to add the mount list to track mulity volumns
    '''
    def get_container_mount_disk(self):
        container_type = get_container_type_from_container_name(self.container_name)
        return component_mount_map.get(container_type)

    def get_container_id(self):
        _inspect = self.docker_opers.inspect_container(self.container_name)
        con = Container_Model(_inspect)
        return con.id()

    def __get_file_value(self, file_path):
        with open(file_path, 'r') as f:
            value = f.read()
            f.close()

        return value

    def get_con_used_mem(self):
        return float(self.__get_file_value(self.used_mem_path))

    def get_con_used_memsw(self):
        return float(self.__get_file_value(self.used_memsw_path))

    def get_con_limit_mem(self):
        return float(self.__get_file_value(self.limit_mem_path))

    def get_con_limit_memsw(self):
        return float(self.__get_file_value(self.limit_memsw_path))

    def get_under_oom_value(self):
        value = self.__get_file_value(self.under_oom_path)
        under_oom_value = re.findall('.*under_oom (\d)$', value)[0]
        return int(under_oom_value)

    def get_memory_stat_value_list(self):
        value = self.__get_file_value(self.memory_stat_path)
        if value:
            return value.split('\n')
        return []

    def get_cpuacct_stat_value(self):
        value = self.__get_file_value(self.cpuacct_stat_path)
        return value.split('\n')

    def get_cpushares_value(self):
        return self.__get_file_value(self.cpushares_path)

    def get_cpuset_value(self):
        return self.__get_file_value(self.cpuset_path)

    def get_memory_stat_item(self):
        mem_stat_dict = {}
        mem_stat_items = self.get_memory_stat_value_list()
        for item in mem_stat_items:
            mem_stat_dict.setdefault('ctime', timestamp())
            if 'total_rss' in item:
                total_rss = item.split(' ')[1]
                mem_stat_dict.setdefault('total_rss', total_rss)
            elif 'total_swap ' in item:
                total_swap = item.split(' ')[1]
                mem_stat_dict.setdefault('total_swap', total_swap)
            elif 'total_cache ' in item:
                total_cache = item.split(' ')[1]
                mem_stat_dict.setdefault('total_cache', total_cache)
        return mem_stat_dict

    def get_oom_kill_disable_value(self):
        value = self.__get_file_value(self.under_oom_path)
        under_oom_value = re.findall(
            'oom_kill_disable (\d)\\nunder_oom.*', value)[0]
        return int(under_oom_value)

    def get_mem_load(self):
        mem_load_rate, mem_load_dict = 0, {}
        used_mem = self.get_con_used_mem()
        limit_mem = self.get_con_limit_mem()

        if used_mem and limit_mem:
            mem_load_rate = used_mem / limit_mem
            mem_load_dict.setdefault('used_mem', used_mem)
            mem_load_dict.setdefault('limit_mem', limit_mem)
            mem_load_dict.setdefault('mem_load_rate', mem_load_rate)
        return mem_load_dict

    def get_memsw_load(self):
        memsw_load_rate, memsw_load_dict = 0, {}
        used_memsw = self.get_con_used_memsw()
        limit_memsw = self.get_con_limit_memsw()

        if used_memsw and limit_memsw:
            memsw_load_rate = used_memsw / limit_memsw
            memsw_load_dict.setdefault('used_memsw', used_memsw)
            memsw_load_dict.setdefault('limit_memsw', limit_memsw)
            memsw_load_dict.setdefault('memsw_load_rate', memsw_load_rate)
        return memsw_load_dict

    def get_root_mnt_size(self):
        return calc_dir_size(self.root_mnt_path)

    def get_volume_mnt_size(self):
        volume_dir = 0
        _inspect = self.docker_opers.inspect_container(self.container_name)
        con = Container_Model(_inspect)
        volumes = con.inspect_volumes()
        if volumes:
            for _, server_dir in volumes.items():
                if self.mount_disk in server_dir:
                    volume_dir = int(calc_dir_size(server_dir))
        return volume_dir

    def __get_disk_total_size(self, _path):
        disk_detail = disk_stat(_path)
        return disk_detail.get('total')

    def get_sum_disk_usage(self):
        result = {}

        volume_mnt_size = self.get_volume_mnt_size()
        container_mount_diskusage = self.__get_disk_total_size(self.mount_disk)
        volume_ccupancy_ratio = float(volume_mnt_size) / container_mount_diskusage * 100
        volume_ccupancy_ratio = '%.2f%%' % volume_ccupancy_ratio
        result.setdefault('volumes_mount', volume_mnt_size)
        result.setdefault('volumes_total', container_mount_diskusage)
        result.setdefault('volumes_ratio', volume_ccupancy_ratio)
        result.setdefault('ctime', timestamp())
        return result
