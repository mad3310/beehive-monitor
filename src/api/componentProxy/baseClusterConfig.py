'''
Created on 2015-2-5

@author: asus
'''

class BaseContainerClusterConfig(object):
    '''
    classdocs
    '''

    def __init__(self, params={}):
        '''
        Constructor
        '''
        
        self.is_res_verify = True
        self.need_validate_manager_status = True
        

        '''
            ---------------------if not supplied, use default value------------------
        '''
        
        
        """
            default value stand for 10G
            server rest minimum memory 
        """       
        mem_free_limit = params.get('memFree')                          
        self.mem_free_limit = eval(mem_free_limit) if mem_free_limit else 10*1024*1024*1024
        
        """
            default value stand for 512M
            container memory limit
        """
        mem_limit = params.get('memory')                           
        self.mem_limit = eval(mem_limit) if mem_limit else 1024*1024*1024
        
        disk_usage = params.get('diskUsage')
        self.disk_usage = float(disk_usage) if disk_usage else 0.8
        
        lxc_conf = params.get('LxcConf')
        self.lxc_conf = dict(lxc_conf) if lxc_conf else {'lxc.cgroup.memory.oom_control':1}
        
        exclude_servers = params.get('exclude_servers')
        _exclude_servers = exclude_servers.split(',') if exclude_servers else []
        self.exclude_servers = [item.strip() for item in _exclude_servers]
        
        """
            if component need config itself, put self.resource_weight__score 
            in its config file
        """
        self.resource_weight__score = { 'memory': 20, 'disk': 20, 'load5': 20, 'load10': 10, 
                                        'load15': 5, 'container_number': 15 }
        
        
        '''
            ---------------------params  must be supplied------------------------------
        '''
        
        container_cluster_name = params.get('containerClusterName')
        self.container_cluster_name = container_cluster_name
        component_type = params.get('componentType')
        self.component_type = component_type
        network_mode = params.get('networkMode')
        self.network_mode = network_mode