# coding:utf-8

import re
import logging

from tornado.options import options
from utils.invokeCommand import InvokeCommand
from resourceForBeehive.serverResourceOpers import Server_Res_Opers
from utils.exceptions import UserVisiableException
from utils import get_dev_number_by_mount_dir, timestamp, open_with_error
from componentProxy import component_mount_map
from appdefine.appDefine import join


class ContainerResource(object):

    def __init__(self, container_id):
        self._container_id = container_id

    @property
    def container_id(self):
        return self._container_id


class CPURatio(ContainerResource):

    server_oprs = Server_Res_Opers()

    def __init__(self, container_id):
        super(CPURatio, self).__init__(container_id)
        self.file = "/cgroup/cpuacct/lxc/%s/cpuacct.stat" % self.container_id
        self.total_user_cpu = 0
        self.total_system_cpu = 0

        self.user_cpu_ratio = 0
        self.system_cpu_ratio = 0

    @staticmethod
    def _cal_ratio(numerator, denominator):
        result = 0.0
        if denominator > 0:
            result = float(numerator) / float(denominator)
        return result

    def statistic(self):

        with open_with_error(self.file) as (f, err):
            if not err:
                content = f.read()
            else:
                logging.error(err)
                return

        total_list = content.strip().split('\n')
        tmp_user = int(total_list[0].split()[1])
        tmp_system = int(total_list[1].split()[1])

        if self.total_user_cpu and self.total_system_cpu:
            cpu_inc = self.server_oprs.server_cpu_ratio.cpu_inc
            self.user_cpu_ratio = self._cal_ratio(
                tmp_user - self.total_user_cpu, cpu_inc)
            self.system_cpu_ratio = self._cal_ratio(
                tmp_system - self.total_system_cpu, cpu_inc)

        self.total_user_cpu = tmp_user
        self.total_system_cpu = tmp_system

    def get_result(self):
        self.statistic()
        result = {
            'total': {
                "user": self.user_cpu_ratio,
                "system": self.system_cpu_ratio
            }
        }
        return result


class NetworkIO(ContainerResource):

    def __init__(self, container_id):
        super(NetworkIO, self).__init__(container_id)
        self._total_rx = 0
        self._total_tx = 0
        self._rx = 0
        self._tx = 0

    def statistic(self):
        ivk_cmd = InvokeCommand()
        nsenter = options.nsenter % self._container_id
        cmd = join(nsenter, "netstat -i")
        content = ivk_cmd._runSysCmd(cmd)[0]
        trx_list = re.findall(
            '.*pbond0\s+\d+\s+\d+\s+(\d+)\s+\d+\s+\d+\s+\d+\s+(\d+).*', content)

        RX_SUM, TX_SUM = 0, 0
        for RX, TX in trx_list:
            RX_SUM += int(RX)
            TX_SUM += int(TX)

        rx_sum = RX_SUM
        tx_sum = TX_SUM

        if self._total_tx and self._total_rx:
            self._tx = tx_sum - self._total_tx
            self._rx = rx_sum - self._total_rx

        self._total_rx = rx_sum
        self._total_tx = tx_sum

    @property
    def rx(self):
        return self._rx

    @property
    def tx(self):
        return self._tx

    def get_result(self):
        self.statistic()
        result = {
            'ctime' : timestamp(),
            'rx' : self.rx,
            'tx' : self.tx
        }
        return result


class DiskIO(ContainerResource):

    def __init__(self, container_id, container_type):
        super(DiskIO, self).__init__(container_id)
        self.file = "/cgroup/blkio/lxc/%s/blkio.throttle.io_service_bytes"
        mount_dir = self.get_mount_dir_by_container_type(container_type)
        self.dev_number = get_dev_number_by_mount_dir(mount_dir)
        self._read_iops = 0
        self._write_iops = 0
        self._total_read_bytes = 0
        self._total_write_bytes = 0

    def get_mount_dir_by_container_type(self, container_type):
        return component_mount_map.get(container_type, "/srv")


    @property
    def read_iops(self):
        return self._read_iops

    @property
    def write_iops(self):
        return self._write_iops

    @staticmethod
    def data_valid(data):
        if data:
            return 'Read' in data and 'Write' in data
        return False

    def statistic(self):
        if not re.match("\d+\:\d+", self.dev_number):
            raise UserVisiableException('get device number wrong :%s' % self.dev_number)

        _file = self.file % self._container_id
        with open_with_error(_file) as (f, err):
            if not err:
                content = f.read()
            else:
                logging.error(err)
                return

        _read, _write = 0, 0
        _readpattern = '%s Read (\d+ ?)' % self.dev_number
        _writepattern = '%s Write (\d+ ?)' % self.dev_number
        if re.search(_readpattern, content) and \
           re.search(_writepattern, content):
            _read = re.findall(_readpattern, content)[0]
            _read = int(_read)
            _write = re.findall(_writepattern, content)[0]
            _write = int(_write)

        if self._total_read_bytes and self._total_write_bytes:
            self._read_iops = (_read - self._total_read_bytes)/options.container_gather_duration
            self._write_iops = (_write - self._total_write_bytes)/options.container_gather_duration

        self._total_read_bytes = _read
        self._total_write_bytes = _write

    def get_result(self):
        self.statistic()
        result = {
            'read': self.read_iops,
            'write': self.write_iops,
            'ctime': timestamp(),
        }
        return result
