
_path = {
    "nginx": "componentProxy.webcontainer",
    "mcluster": "componentProxy.db",
    "gbalancer": "componentProxy.loadbalance",
    "jetty": "componentProxy.webcontainer",
    "gbalancerCluster": "componentProxy.loadbalance",
    "cbase": "componentProxy.store",
    "logstash": "componentProxy.webcontainer",
}


component_mount_map = {
    "ngx": "/var/log",
    "mcl": "/srv/docker/vfs",
    "gbl": "/srv",
    "jty": "/var/log",
    "gbc": "/srv",
    "cbs": "/opt/letv",
    "lgs": "/var/log",
    "zkp": "/srv",
    "kbn": "/var/log",
    "esh": "/srv/docker/vfs",
}
