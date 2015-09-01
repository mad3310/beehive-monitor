#!/usr/bin/env python
#-*- coding: utf-8 -*-

from handlers.containerCluster_handler import *
from handlers.container_handler import *
from handlers.monitor_handler import *
from handlers.server_handler import *
from handlers.serverCluster_handler import *
from handlers.admin import AdminConf, AdminUser

handlers = [
    
    (r"/admin/conf", AdminConf),
    (r"/admin/user", AdminUser),

    (r"/containerCluster/sync", CheckClusterSyncHandler),
    (r"/containerCluster/status/(.*)", CheckContainerClusterStatusHandler),
    (r"/containerCluster/stat/(.*)/memory", GatherClusterMemeoyHandler),
    (r"/containerCluster/stat/(.*)/cpuacct", GatherClusterCpuacctHandler),
    (r"/containerCluster/stat/(.*)/networkio", GatherClusterNetworkioHandler),
    (r"/containerCluster/stat/(.*)/disk", GatherClusterDiskHandler),

    (r"/container/status/(.*)", CheckContainerStatusHandler),
    (r"/container/stat/(.*)/memory", GatherContainerMemeoyHandler),
    (r"/container/stat/(.*)/cpuacct", GatherContainerCpuacctHandler),
    (r"/container/stat/(.*)/networkio", GatherContainerNetworkioHandler),

    (r"/server/resource", CollectServerResHandler),
    (r"/server/containers/disk", GatherServerContainersDiskLoadHandler),

    (r"/serverCluster/containers/disk", GatherServersContainersDiskLoadHandler),
]
