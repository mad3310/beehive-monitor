'''
Created on 2015-12-11

@author: asus
'''
import unittest
import datetime

import os
import logging
from os.path import join, getsize
from stat import S_ISDIR, S_ISREG


class Test(unittest.TestCase):
    
    def get_dir_size(self, dir_name, exclude_dirs=[]):
        size = 0L
        for root, dirs, files in os.walk(dir_name):
            for exclude_dir in exclude_dirs:
                if exclude_dir in dirs:
                    dirs.remove(exclude_dir)
            size += sum([getsize(join(root, name)) for name in files])
            
        return size
    
    def _walk_dir(self, file_path, file_list=[]):

        for f in os.listdir(file_path):
            try:
                path_name = os.path.join(file_path, f)
            except UnicodeDecodeError:
                continue
            islink = os.path.islink(path_name)
            is_exists =  os.path.exists(path_name)   
            if not islink and is_exists:
                mode = os.stat(path_name).st_mode
                if S_ISDIR(mode):
                    self._walk_dir(path_name, file_list)
                elif S_ISREG(mode):
                    size = os.stat(path_name).st_size
                    file_list.append(size)
                else:
                    #pass
                    logging.info('invalid path: %s' % path_name)
    
    def calc_dir_size(self, file_path):
        files = []
        self._walk_dir(file_path, files)
        return sum(files)
    
    def test_calc_dir_size(self):
        d1 = datetime.datetime.now()
        dir_size = self.calc_dir_size(r'/')
        d2 = datetime.datetime.now()
        print 'There are %.3f' % (dir_size/1024/1024), 'Mbytes in /'
        print 'operation time diff is %s' % (d2-d1).seconds

    def test_get_dir_size(self):
        d1 = datetime.datetime.now()
        dir_size = self.get_dir_size(r'/', ['proc', 'data', 'dev', 'lib', 'bin', 'home'])
        d2 = datetime.datetime.now()
        print 'There are %.3f' % (dir_size/1024/1024), 'Mbytes in /'
        print 'operation time diff is %s' % (d2-d1).seconds
        
    
