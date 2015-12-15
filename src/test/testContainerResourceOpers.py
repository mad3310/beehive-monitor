'''
Created on Dec 15, 2015

@author: root
'''
import unittest

from resource_letv.containerResourceOpers import ContainerCacheHandler,ContainerCPUAcctHandler,ContainerMemoryHandler,\
ContainerDiskIOPSHandler,ContainerDiskUsageHandler,ContainerNetworkIOHandler


class Test(unittest.TestCase):
    
#     def (self):
#         self.confOpers.setValue(options.container_manager_property, requestParam)


    def test_ContainerCacheHandler_gather(self):
        containerCacheHandler = ContainerCacheHandler()
        containerCacheHandler.gather()
        
    def test_ContainerCPUAcctHandler_gather(self):
        containerCPUAcctHandler = ContainerCPUAcctHandler()
        containerCPUAcctHandler.gather()
        
    def test_ContainerMemoryHandler_gather(self):
        containerMemoryHandler = ContainerMemoryHandler()
        containerMemoryHandler.gather()
        
    def test_ContainerDiskIOPSHandler_gather(self):
        containerDiskIOPSHandler = ContainerDiskIOPSHandler()
        containerDiskIOPSHandler.gather()
        
    def test_ContainerDiskUsageHandler_gather(self):
        containerDiskUsageHandler = ContainerDiskUsageHandler()
        containerDiskUsageHandler.gather()
        
    def test_ContainerNetworkIOHandler_gather(self):
        containerNetworkIOHandler = ContainerNetworkIOHandler()
        containerNetworkIOHandler.gather()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_ContainerCacheHandler_gather']
    unittest.main()