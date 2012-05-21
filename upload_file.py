'''
Created on 2012-5-9

@author: ling0322
'''


import config
import os
import json
import logging
import hashlib
from urllib import quote

from ac_request import ac_request
logging.getLogger().setLevel(logging.DEBUG)

def _sha1_file(path):
    sha1 = hashlib.sha1()
    with open(path, 'rb') as fp:
        data = fp.read(1000000)
        while data:
            sha1.update(data)
            data = fp.read(1000000)
            
    return sha1.hexdigest()

def block_iterator(path):
    with open(path, 'rb') as fp:
        content = None
        i = 0
        while True:
            content = fp.read(config.UPLOAD_BLOCK_SIZE)
            if content == '':
                break
            yield content, i
            i += 1

def prepare_file_metadata(path):
    file_stat = os.stat(path)
    sha1 = _sha1_file(path)
    size = file_stat.st_size 
    modified = file_stat.st_mtime
    return dict(
        sha1 = sha1,
        size = size,
        mtime = modified)
            
def upload_block(upload_id, content, index):
    url = "{0}/upload/{1}/{2}".format(config.AC_URL, upload_id, index)
    ac_request(url, content)

def start_upload(user, upload_path, metadata):  
    json_metadata = json.dumps(metadata)
    
    url = "{0}/start-upload/{1}{2}".format(config.AC_URL, user, quote(upload_path))
    resp, result = ac_request(url, json_metadata)
    if result == 'OK':
        return None
    upload_id = int(result)
    return upload_id

def finish_upload(upload_id):
    url = "{0}/finish-upload/{1}".format(config.AC_URL, upload_id)
    ac_request(url)
    
def upload_file(path, upload_path):
    metadata = prepare_file_metadata(path)
    upload_id = start_upload(config.USER_NAME, upload_path, metadata)
    
    if upload_id == None:
        # this file already exists in server, so there is no need to upload content
        
        return 
    for block, index in block_iterator(path):
        logging.info('upload {0} - block {1}'.format(path, index))
        upload_block(upload_id, block, index)
    finish_upload(upload_id)


    