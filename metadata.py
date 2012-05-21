'''
Created on 2012-5-15

@author: ling0322
'''

import pathtools.path
import os.path
import pickle
import config
import copy
from lava_potion import log
import json

def _cmp_time(t1, t2):
    if abs(t1 - t2) < 1.5:
        return 0
    elif t1 > t2:
        return 1
    else:
        return -1

def diff(list_1, list_2):
    list_1 = copy.copy(list_1)
    list_2 = copy.copy(list_2)
    diff = dict(
        remained = [],
        modified = [],
        outdated = [],
        missing = [])
        
    for key_1 in list_1.keys():
        if key_1 in list_2:
            if _cmp_time(list_1[key_1]['mtime'], list_2[key_1]['mtime']) > 0:
                diff['modified'].append(key_1)
            elif _cmp_time(list_1[key_1]['mtime'], list_2[key_1]['mtime']) < 0:
                diff['outdated'].append(key_1)
                    
            del list_1[key_1]
            del list_2[key_1]
        else:
            diff['remained'].append(key_1)
                
    diff['missing'] = list_2
        
    return diff

def local_list(root_path):
    mlist = {}
    for abs_path in pathtools.path.list_files(root_path):
        try:
            rel_path = '/' + os.path.relpath(abs_path, root_path).replace('\\', '/')
            file_stat = os.stat(abs_path)
            mlist[rel_path] = dict(
                size = file_stat.st_size,
                mtime = file_stat.st_mtime)
        except:
            raise 
    return mlist

class Metadata:
    pickle_path = 'pickle-metadata'
    inst = None
    
    @classmethod
    def instance(cls):
        if cls.inst == None:
            cls.inst = Metadata()
        
        return cls.inst
    
    def __init__(self):
        self.root = config.ROOT_PATH
        self._load()

    def update(self, path, metadata):
        self._local_list[path] = metadata
        self._flush()
        log(config.METADATA_LOG, 'metadata modified, updated {0} -> {1}'.format(path, json.dumps(metadata)))
        
    def delete(self, path):
        del self._local_list[path]
        self._flush()
        log(config.METADATA_LOG, 'metadata modified, deleted {0}'.format(path))
    
    def get_list(self):
        return self._local_list
    
    def _flush(self):
        pickle.dump(self._local_list, open(self.pickle_path, 'wb'))
        
    def _load(self):
        try:
            self._local_list = pickle.load(open(self.pickle_path, 'rb'))
        except:
            os.remove(self.pickle_path)
            pickle.dump({}, open(self.pickle_path, 'wb'))
            self._local_list = {}
    

            

                
        
                
        