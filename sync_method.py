'''
Created on 2012-5-15

@author: ling0322
'''

from __future__ import unicode_literals
import config
import ac_file
import os
import metadata
from lava_potion import log
import functools
import tornado.ioloop
import time
from lava_potion import encode_if_necessary

def _local_file_metadata(path):
    file_stat = os.stat(path)
    size = file_stat.st_size 
    mtime = file_stat.st_mtime
    return dict(
        size = size,
        mtime = mtime)

def _local_created(local_path):
    md = metadata.Metadata.instance()
    li = md.get_list()
    
    # if the metadata of file is already updated in metadata_list, do not do anything
    abs_path = config.ROOT_PATH + local_path
    
    if local_path in li and li[local_path]['mtime'] == _local_file_metadata(abs_path)['mtime']:
        log(config.SYNC_METHOD_LOG, 'reject update request {0}'.format(local_path))
        return 
    
    ac_file.upload(abs_path, local_path)
    md.update(local_path, _local_file_metadata(abs_path))
    log(config.SYNC_METHOD_LOG, 'called local created method {0}'.format(local_path))
    
def _local_deleted(local_path):
    md = metadata.Metadata.instance()
    li = md.get_list()
    if local_path not in li:
        log(config.SYNC_METHOD_LOG, 'reject delete request {0}'.format(local_path), 'sync_method')
        return 
            
    ac_file.delete(local_path)
    md = metadata.Metadata.instance()
    md.delete(local_path)
    log(config.SYNC_METHOD_LOG, 'called local deleted method {0}'.format(local_path))

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
    abs_path = config.ROOT_PATH + remote_path
    md = metadata.Metadata.instance()
    metacnt = _local_file_metadata(abs_path)
    locallist = md.get_list()
    if remote_path not in locallist or locallist[remote_path]['mtime'] != metacnt['mtime']:
        # if modify of this file has not yet to push to server, ignore delete command
        log(config.SYNC_METHOD_LOG, 'delete file "{0}" not yet to push to server, ignore it'.format(remote_path))
        
        return 
    
    
    os.remove(abs_path)
    
    md.delete(remote_path)
    log(config.SYNC_METHOD_LOG, 'remote deleted {0}'.format(remote_path))

UPDATE = 0
DELETE = 1

def push(path, event, retry_times = config.PUSH_RETRY_TIMES):
    log(config.SYNC_METHOD_LOG, 'push request', __name__)
    
    try:
        if event == UPDATE:
            _local_created(path)
        elif event == DELETE:
            _local_deleted(path)
    except:
        if retry_times == 0:
            raise
        
        log(
            config.SYNC_METHOD_LOG, 
            'push request failed, try to push again in {0} seconds ({1})'.format(config.PUSH_RETRY_INTERVALS, retry_times), 
            __name__)
        
        callback = functools.partial(push, path, event, retry_times - 1)
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.add_timeout(time.time() + config.PUSH_RETRY_INTERVALS, callback)
        
def pull():
    log(config.SYNC_METHOD_LOG, 'pull request', __name__)
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
    log(config.SYNC_METHOD_LOG, 'merge request', __name__)
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
    log(config.SYNC_METHOD_LOG, 'init request', __name__)
    md = metadata.Metadata.instance()
    last_list = md.get_list()
    if last_list == {}:
        merge()
        return 
    
    # PUSH
    
    try:
        local_list = metadata.local_list(config.ROOT_PATH)
        diff = metadata.diff(last_list, local_list)
        for path in diff['missing']:
            push(path, UPDATE)
        
        for path in diff['remained']:
            push(path, DELETE)
        
        for path in diff['outdated']:
            push(path, UPDATE)
    except: 
        merge()
        return 
    
    pull()
