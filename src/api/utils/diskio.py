#!/usr/bin/env python
# encoding: utf-8
from collections import namedtuple

import shlex
import subprocess
import sys

try:
    # for python3.2+
    from functools import lru_cache
except:
    # for python3.2-
    from utils.func_tool import lru_cache

sdiskio = namedtuple('sdiskio', ['read_count', 'write_count',
                                 'read_bytes', 'write_bytes',
                                 'read_time', 'write_time',
                                 'read_merged_count', 'write_merged_count',
                                 'busy_time'])

sdiskpart = namedtuple('sdiskpart', ['device', 'mountpoint', 'fstype', 'opts'])


@lru_cache(maxsize=10080)
def get_sector_size():
    try:
        with open(b"/sys/block/sda/queue/hw_sector_size") as f:
            return int(f.read())
    except (IOError, ValueError):
        # 默认情况下是512 bytes
        return 512

SECTOR_SIZE = get_sector_size()


@lru_cache(maxsize=10080)
def parse_lsblk():
    """通过lsblk命令获取磁盘名称、磁盘内核名称、挂载点的对应信息."""
    cmd = 'lsblk -P -o name,kname,mountpoint'
    try:
        p = subprocess.Popen(shlex.split(cmd),
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retstr = p.stdout.readlines()
    except OSError as e:
        print>>sys.stderr, 'Execution failed:', e
    retdic = {}
    for line in retstr:
        dic = dict((k.lower(), v.replace('"', '')) for k, v in
                   (x.split('=') for x in line.strip().split()))
        retdic[dic['kname']] = dic
    return retdic


@lru_cache(maxsize=10080)
def get_partitions():
    """获取所有已安装的分区, 与fdisk -l 得到的分区相同，区别是名字
    显示的格式不同。
    """
    partitions = []
    with open("/proc/partitions", "r") as f:
        lines = f.readlines()[2:]
    for line in reversed(lines):
        # 存在sda-1这样带数字的分区时则忽略sda，各个子分区单独统计
        _, _, _, name = line.split()
        if name[-1].isdigit():
            partitions.append(name)
        else:
            # 不存在sda-1这样带数字的子分区时，则获取sda整个分区
            if not partitions or not partitions[-1].startswith(name):
                partitions.append(name)
    return partitions


def stats():
    """获取系统中所有已安装磁盘的io统计情况。"""

    retdict = {}
    partitions = get_partitions()
    with open("/proc/diskstats", "r") as f:
        lines = f.readlines()
    for line in lines:
        # https://www.kernel.org/doc/Documentation/iostats.txt
        # https://www.kernel.org/doc/Documentation/ABI/testing/procfs-diskstats
        fields = line.split()
        fields_len = len(fields)
        if fields_len == 15:
            # Linux 2.4
            name = fields[3]
            reads = int(fields[2])
            (reads_merged, rbytes, rtime, writes, writes_merged,
                wbytes, wtime, _, busy_time, _) = map(int, fields[4:14])
        elif fields_len == 14:
            # Linux 2.6+, line referring to a disk
            name = fields[2]
            (reads, reads_merged, rbytes, rtime, writes, writes_merged,
                wbytes, wtime, _, busy_time, _) = map(int, fields[3:14])
        elif fields_len == 7:
            # Linux 2.6+, line referring to a partition
            name = fields[2]
            reads, rbytes, writes, wbytes = map(int, fields[3:])
            rtime = wtime = reads_merged = writes_merged = busy_time = 0
        else:
            raise ValueError("not sure how to interpret line %r" % line)

        if name in partitions:
            rbytes = rbytes * SECTOR_SIZE
            wbytes = wbytes * SECTOR_SIZE
            retdict[name] = sdiskio(reads, writes, rbytes, wbytes,
                                    rtime, wtime, reads_merged, writes_merged,
                                    busy_time)
    return retdict


@lru_cache(maxsize=10080)
def disk_partitions(all=False):
    """返回已挂载的分区, 同df 命令看到的分区"""
    retlst = []
    with open("/etc/mtab", 'r') as f:
        for line in f:
            if not all and not line.startswith("/"):
                continue
            line = line.split()[:-2]
            ntuple = sdiskpart(*line)
            retlst.append(ntuple)
    return retlst


@lru_cache(maxsize=10080)
def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9.8 K/s'
    >>> bytes2human(100001221)
    '95.4 M/s'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f %s/s' % (value, s)
    return '%.2f B/s' % (n)


if __name__ == '__main__':
    print stats()
    print disk_partitions()
    print parse_lsblk()
