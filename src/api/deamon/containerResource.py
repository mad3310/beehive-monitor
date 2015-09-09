__author__ = 'mazheng'

import re
from tornado.options import options
from utils.invokeCommand import InvokeCommand
from common.abstractScheduler import AbstractScheduler


class ResourceScheduler(AbstractScheduler):

    def statistic(self, *args):
        raise NotImplemented("statistic should be implemented!")

    def run_cycle_time(self, period, *args):
        return super(ResourceScheduler, self).run_cycle_time(self.statistic, period, *args)

    def run_fixed_time(self, delay, *args):
        return super(ResourceScheduler, self).run_fixed_time(self.statistic, delay, *args)


class NetworkIO(ResourceScheduler):

    def __init__(self):
        super(NetworkIO, self).__init__()
        self._total_rx = 0  # KB
        self._total_tx = 0  # KB
        self._rx = 0  # KB
        self._tx = 0  # KB

    def statistic(self, container_id):
        RX_SUM, TX_SUM = 0, 0
        ivk_cmd = InvokeCommand()
        cmd = "sh %s %s" % (options.network_io_sh, container_id)
        content = ivk_cmd._runSysCmd(cmd)[0]
        trx_list = re.findall(
            '.*peth0\s+\d+\s+\d+\s+(\d+)\s+\d+\s+\d+\s+\d+\s+(\d+).*', content)
        for RX, TX in trx_list:
            RX_SUM += int(RX)
            TX_SUM += int(TX)
        rx_sum = RX_SUM / 1024
        tx_sum = TX_SUM / 1024
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


class DiskIO(ResourceScheduler):

    def __init__(self):
        super(DiskIO, self).__init__()
        self.file = "/cgroup/blkio/lxc/%s/blkio.throttle.io_service_bytes"
        self._read_iops = 0  # KB
        self._write_iops = 0  # KB
        self._total_read_bytes = 0  # KB
        self._total_write_bytes = 0  # KB

    @property
    def read_iops(self):
        return self._read_iops

    @property
    def write_iops(self):
        return self._write_iops

    def statistic(self, dev_number, container_id):
        _file = self.file % container_id
        cmd = "cat %s | grep %s" % (_file, dev_number)
        ivk_cmd = InvokeCommand()
        content = ivk_cmd._runSysCmd(cmd)[0]
        if content:
            sread = re.findall('Read (\d+)', content)[0]
            swrite = re.findall('Write (\d+)', content)[0]
        else:
            sread = 0
            swrite = 0
        read = int(sread) / 1024
        write = int(swrite) / 1024
        if self._total_read_bytes and self._total_write_bytes:
            self._read_iops = read - self._total_read_bytes
            self._write_iops = write - self._total_write_bytes
        self._total_read_bytes = read
        self._total_write_bytes = write


class Test(ResourceScheduler):

    def statistic(self, name, work):
        print name, work


if __name__ == "__main__":
    test = Test()
    test.run_cycle_time(1, 'xsank', 'code')
    print 'hello'
