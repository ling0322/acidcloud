'''
Created on 2012-5-15

@author: ling0322
'''


import config
import ac_file
import os
import metadata

def local_created(local_path):
    abs_path = config.ROOT_PATH + local_path
    ac_file.upload(abs_path, local_path)
    
def local_deleted(local_path):
    ac_file.delete(local_path)

def remote_created(remote_path):
    content = ac_file.fetch(remote_path)
    fp = open(config.ROOT_PATH + remote_path, 'wb')
    fp.write(content)
    
def remote_deleted(remote_path):
    os.remove(config.ROOT_PATH + remote_path)
    
def push(path):
    local_created(path)
    
def pull(path):
    remote_list = ac_file.list()
    md = metadata.Metadata.instance()
    diff = md.diff_remote(remote_list)
    for remote_path in diff['local_missing']:
        remote_created(remote_path)
        
    for remote_path in diff['local_created']:
        remote_deleted(remote_path)
        
    for remote_path in diff['local_outdated']:
        remote_created(remote_path)
        
    
    