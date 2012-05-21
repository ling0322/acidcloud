'''
Created on 2012-5-15

@author: ling0322
'''


import config
import ac_file
import os
import metadata
from lava_potion import log

def _local_file_metadata(path):
    file_stat = os.stat(path)
    size = file_stat.st_size 
    mtime = file_stat.st_mtime
    return dict(
        size = size,
        mtime = mtime)

def _local_created(local_path):
    md = metadata.Metadata.instance()
    abs_path = config.ROOT_PATH + local_path
    ac_file.upload(abs_path, local_path)
    md.update(local_path, _local_file_metadata(abs_path))
    log(config.SYNC_METHOD_LOG, 'local created {0}'.format(local_path))
    
def _local_deleted(local_path):
    ac_file.delete(local_path)
    md = metadata.Metadata.instance()
    md.delete(local_path)
    log(config.SYNC_METHOD_LOG, 'local deleted {0}'.format(local_path))

def _create_folder_for_path(path):
    head, tail = os.path.split(path)
    if os.path.exists(head) == True:
        return 
    _create_folder_for_path(head)
    os.mkdir(head)
        

def _remote_created(remote_path):
    meta, content = ac_file.fetch(remote_path)
    abs_path = config.ROOT_PATH + remote_path
    _create_folder_for_path(abs_path)
    with open(abs_path, 'wb') as fp:
        fp.write(content)
    mtime = meta['mtime']
    os.utime(abs_path, (mtime, mtime))
    md = metadata.Metadata.instance()
    md.update(remote_path, _local_file_metadata(abs_path))
    log(config.SYNC_METHOD_LOG, 'remote created {0}'.format(remote_path))
    
    
def _remote_deleted(remote_path):
    os.remove(config.ROOT_PATH + remote_path)
    md = metadata.Metadata.instance()
    md.delete(remote_path)
    log(config.SYNC_METHOD_LOG, 'remote deleted {0}'.format(remote_path))

UPDATE = 0
DELETE = 1

def push(path, event):
    if event == UPDATE:
        _local_created(path)
    elif event == DELETE:
        _local_deleted(path)
    
def pull():
    remote_list = ac_file.listfile()
    md = metadata.Metadata.instance()
    local_list = md.get_list()
    diff = metadata.diff(local_list, remote_list)
    for path in diff['missing']:
        _remote_created(path)
        
    for path in diff['remained']:
        _remote_deleted(path)
        
    for path in diff['outdated']:
        _remote_created(path)
        
def merge():
    remote_list = ac_file.listfile()
    local_list = metadata.local_list(config.ROOT_PATH)
    diff = metadata.diff(local_list, remote_list)
    for path in diff['missing']:
        _remote_created(path)
        
    for path in diff['remained']:
        _local_created(path)
        
    for path in diff['outdated']:
        _remote_created(path)

    for path in diff['modified']:
        _local_created(path)        

def init():
    md = metadata.Metadata.instance()
    last_list = md.get_list()
    if last_list == {}:
        merge()
        return 
    
    # PUSH
    
    local_list = metadata.local_list(config.ROOT_PATH)
    diff = metadata.diff(last_list, local_list)
    for path in diff['missing']:
        push(path, UPDATE)
        
    for path in diff['remained']:
        push(path, DELETE)
        
    for path in diff['outdated']:
        push(path, UPDATE)
        
    # PULL
    
    pull()

init()
    