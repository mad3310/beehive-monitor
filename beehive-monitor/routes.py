#!/usr/bin/env python
#-*- coding: utf-8 -*-

from handlers.containerCluster_handler import *
from handlers.container_handler import *
from handlers.server_handler import *
from handlers.monitor_handler import ContainerStatus
from handlers.admin import AdminConf, AdminUser

handlers = [

    (r"/admin/conf", AdminConf),
    (r"/admin/user", AdminUser),

    (r"/containerCluster/sync", CheckClusterSyncHandler),
    (r"/containerCluster/status/(.*)", CheckContainerClusterStatusHandler),
    (r"/containerCluster/stat/(.*)/memory", GatherClusterMemeoyHandler),
    (r"/containerCluster/stat/(.*)/cpuacct", GatherClusterCpuacctHandler),
    (r"/containerCluster/stat/(.*)/networkio", GatherClusterNetworkioHandler),
    (r"/containerCluster/stat/(.*)/diskiops", GatherClusterDiskiopsHandler),
    (r"/containerCluster/stat/(.*)/diskusage", GatherClusterDiskusageHandler),

    (r"/container/status/(.*)", CheckContainerStatusHandler),
    (r"/container/stat/(.*)/memory", GatherContainerMemeoyHandler),
    (r"/container/stat/(.*)/cpuacct", GatherContainerCpuacctHandler),
    (r"/container/stat/(.*)/networkio", GatherContainerNetworkioHandler),
    (r"/container/stat/(.*)/diskiops", GatherContainerDiskIopsHandler),
    (r"/container/stat/(.*)/diskusage", GatherContainerDiskusageHandler),

    (r"/server/resource/(.*)/cpu", GatherServerCpuHandler),
    (r"/server/resource/(.*)/memory", GatherServerMemoryHandler),
    (r"/server/resource/(.*)/diskusage", GatherServerDiskusageHandler),
    (r"/server/resource/(.*)/diskiops", GatherServerDiskiopsHandler),

    (r"/monitor/status", ContainerStatus),
]
