__author__ = 'mazheng'

import re

from tornado.options import options

from utils.invokeCommand import InvokeCommand
from daemonResource import ContainerResource
from server.serverOpers import Server_Res_Opers


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
        if denominator == 0:
            return 0.0
        return 1.0 * numerator / denominator

    def statistic(self):
        ivk_cmd = InvokeCommand()
        cmd = 'cat %s' % self.file
        content = ivk_cmd._runSysCmd(cmd)[0]
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
        result = {}
        result['total'] = {"user": self.user_cpu_ratio,
                           "system": self.system_cpu_ratio}
        return result


class NetworkIO(ContainerResource):

    def __init__(self, container_id):
        super(NetworkIO, self).__init__(container_id)
        self._total_rx = 0
        self._total_tx = 0
        self._rx = 0
        self._tx = 0

    def statistic(self):
        RX_SUM, TX_SUM = 0, 0
        ivk_cmd = InvokeCommand()
        cmd = "sh %s %s" % (options.network_io_sh, self._container_id)
        content = ivk_cmd._runSysCmd(cmd)[0]
        trx_list = re.findall(
            '.*pbond0\s+\d+\s+\d+\s+(\d+)\s+\d+\s+\d+\s+\d+\s+(\d+).*', content)
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
        result = {}
        self.statistic()
        result['rx'] = self.rx
        result['tx'] = self.tx
        return result


class DiskIO(ContainerResource):

    type_dir_map = {
        "ngx": "/srv",
        "mcl": "/srv/docker/vfs",
        "gbl": "/srv",
        "jty": "/srv",
        "gbc": "/srv",
        "cbs": "/srv",
        "lgs": "/srv"
    }

    def __init__(self, container_id, container_type):
        super(DiskIO, self).__init__(container_id)
        self.file = "/cgroup/blkio/lxc/%s/blkio.throttle.io_service_bytes"
        self.dev_number = self._dev_number(container_type)
        self._read_iops = 0
        self._write_iops = 0
        self._total_read_bytes = 0
        self._total_write_bytes = 0

    def get_mount_dir_by_container_type(self, container_type):
        return self.type_dir_map.get(container_type, "/srv")

    def _dev_number(self, container_type):
        mount_dir = self.get_mount_dir_by_container_type(container_type)
        ivk_cmd = InvokeCommand()
        cmd = "sh %s %s" % (options.disk_number_sh, mount_dir)
        return ivk_cmd._runSysCmd(cmd)[0]

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
        _file = self.file % self._container_id
        cmd = "cat %s | grep %s" % (_file, self.dev_number)
        ivk_cmd = InvokeCommand()
        content = ivk_cmd._runSysCmd(cmd)[0]
        if self.data_valid(content):
            sread = re.findall('Read (\d+)', content)[0]
            swrite = re.findall('Write (\d+)', content)[0]
        else:
            sread = 0
            swrite = 0
        read = int(sread)
        write = int(swrite)
        if self._total_read_bytes and self._total_write_bytes:
            self._read_iops = read - self._total_read_bytes
            self._write_iops = write - self._total_write_bytes
        self._total_read_bytes = read
        self._total_write_bytes = write

    def get_result(self):
        result = {}
        self.statistic()
        result['read'] = self.read_iops
        result['write'] = self.write_iops
        return result
