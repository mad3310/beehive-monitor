'''
Created on Dec 12, 2015

@author: root
'''
import unittest

from state.stateOpers import StateOpers


class Test(unittest.TestCase):
    
    '''
    @summary: tool
    '''
    def test_get_container_id(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_container_id()
        print "get_container_id: %s" % result
        
    '''
    @summary: memory
    '''
    def test_get_con_used_mem(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_con_used_mem()
        print "get_con_used_mem: %s" % result
        
    def test_get_con_used_memsw(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_con_used_memsw()
        print "get_con_used_memsw: %s" % result
        
    def test_get_con_limit_mem(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_con_limit_mem()
        print "get_con_limit_mem: %s" % result
        
    def test_get_con_limit_memsw(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_con_limit_memsw()
        print "get_con_limit_memsw: %s" % result
        
    def test_get_mem_load(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_mem_load()
        print "get_mem_load: %s" % result
        
    def test_get_memsw_load(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_memsw_load()
        print "get_memsw_load: %s" % result
        
    def test_get_memory_stat_value_list(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_memory_stat_value_list()
        print "get_memory_stat_value_list %s" % result
        
        
    def test_get_memory_stat_item(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_memory_stat_item()
        print "get_memory_stat_item: %s" % result
        
        
    '''
    @summary: cpu
    '''
    def test_get_cpushares_value(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_cpushares_value()
        print "get_cpushares_value: %s" % result
        
    def test_get_cpuset_value(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_cpuset_value()
        print "get_cpuset_value: %s" % result
        
    def test_get_cpuacct_stat_value(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_cpuacct_stat_value()
        print "get_cpuacct_stat_value: %s" % result
        
        
        
        
    '''
    @summary: oom
    '''
    def test_get_under_oom_value(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_under_oom_value()
        print "get_under_oom_value: %s" % result
        
    def test_get_oom_kill_disable_value(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_oom_kill_disable_value()
        print "get_oom_kill_disable_value: %s" % result
        
    
    '''
    @summary: disk usage
    '''    
    def test_get_root_mnt_size(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_root_mnt_size()
        print "get_root_mnt_size: %s" % result
        
    def test_get_volume_mnt_size(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_volume_mnt_size()
        print "get_volume_mnt_size: %s" % result
        
    def test_get_sum_disk_usage(self):
        stateOpers = StateOpers('d-mcl-mcluster-manager-test-n-3')
        result = stateOpers.get_sum_disk_usage()
        print "get_sum_disk_usage: %s" % result
        self.assertNotEqual(result, None, "result not none")
        self.assertNotEqual(result.get('root_mount'), 0, "root_mount > 0") 
        self.assertNotEqual(result.get('volumes_mount'), 0, "volumes_mount > 0") 
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()