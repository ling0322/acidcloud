'''
Created on 2012-5-15

@author: ling0322
'''

import pathtools
import os.path
import pickle
import hashlib
import config
import ac_file
import copy

def _cmp_time(t1, t2):
    if abs(t1 - t2) < 1.5:
        return 0
    elif t1 > t2:
        return 1
    else:
        return -1
        
class FsSha1Val:
    pickle_path = 'pickle-sha1'
    def __init__(self):
        self.sha1_list = {} if not os.path.exists(self.pickle_path) else pickle.load(self.pickle_path)
    
    def _sha1_file(self, path):
        sha1 = hashlib.sha1()
        with open(path, 'rb') as fp:
            data = fp.read(1000000)
            while data:
                sha1.update(data)
                data = fp.read(1000000)
            
        return sha1.hexdigest()
    
    def _exist_in_list(self, path, size, modified_time):
        if path not in self.sha1_list.keys():
            return False
        
        old_size = self.sha1_list[path]['size']
        old_modified_time = self.sha1_list[path]['modified']
        
        if old_size != size:
            return False
        
        if _cmp_time(old_modified_time, modified_time) != 0:
            return False
        
        return True
    
    def get_sha1(self, path, size, modified_time):
        if self._exist_in_list(path, size, modified_time) == True:
            return self.sha1_list[path]['sha1']
        
        sha1 = self._sha1_file(path)
        self.sha1_list[path] = dict(
            size = size,
            modified = modified_time,
            sha1 = sha1)
        self.flush()
        
        return sha1
    
    def flush(self):
        pickle.dump(self.sha1_list, self.pickle_path)
        
    inst = None
    
    @classmethod
    def instance(cls):
        if cls.inst == None:
            cls.inst = FsSha1Val()
        
        return cls.inst
        


class Metadata:
    pickle_path = 'pickle-metadata'
    INIT = 0
    PULLING = 1
    RUNNING = 2
    MERGING = 3
    
    @classmethod
    def instance(cls):
        if cls.inst == None:
            cls.inst = Metadata()
        
        return cls.inst
    
    def __init__(self):
        self.sha1 = FsSha1Val.instance()
        self.root = config.ROOT_PATH
        self.local_list = self._load_local()
        self.state = self.INIT
        
        
    def update(self, path, metadata):
        self.local_list[path] = metadata
        self._flush()
    
    def _flush(self):
        pickle.dump(self.local_list, self.pickle_path)
    
    def _scan_local(self):
        mlist = {}
        for abs_path in pathtools.path.list_files(self.root):
            try:
                rel_path = '/' + os.path.relpath(abs_path, self.root)
                file_stat = os.stat(abs_path)
                mlist[rel_path] = dict(
                    size = file_stat.st_size,
                    modified = file_stat.st_mtime)
            except:
                raise 
            
    def diff_remote(self, remote_list_o):
        remote_list = copy.copy(remote_list_o)
        diff = dict(
            local_created = [],
            local_modified = [],
            local_outdated = [],
            local_missing = [])
        local_list = copy.copy(self.local_list)
        
        for local_key in local_list.keys():
            if local_key in remote_list:
                if _cmp_time(local_list[local_key]['modified'], remote_list[local_key]['size']) > 0:
                    diff['local_modified'].append(local_key)
                elif _cmp_time(local_list[local_key]['modified'], remote_list[local_key]['size']) < 0:
                    diff['local_outdated'].append(local_key)
                    
                del local_list[local_key]
                del remote_list[local_key]
            else:
                diff['local_created'].append(local_key)
                
        diff['local_missing'] = remote_list
        
        return diff
                
        
                
        