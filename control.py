'''
Created on 2012-5-9

@author: ling0322
'''

import userinfo
import gsfile
import metadata
import upload

def delete_file(user_name, path):
    user = user_name.lower()
    metadata.remove_metadata(user, path)
    
def is_sha1_block_exist(sha1):
    return gsfile.exists(sha1)

def upload_file(user, path, meta):
    if False == is_sha1_block_exist(meta['sha1']):
        return upload.start_upload(user, path, meta)
    else:
        metadata.put_metadata(
            user_name = user.lower(), 
            path = path, 
            size = meta['size'], 
            mtime = meta['mtime'],
            sha1 = meta['sha1'])
        return None

def upload_block(upload_id, index, block):
    upload.append_block(upload_id, index, block)

def finish_upload_file(upload_id):
    upload.finish_upload(upload_id)

def get_list(user):
    return metadata.list_metadata(user)

def file_metadata(user, path):
    ''' if file not exists, return None '''
    return metadata.get_metadata(user, path)

def get_file_gspath(user, path):
    sha1 = metadata.get_metadata(user, path)['sha1']
    return gsfile.get_gs_path(sha1)

def create_user(user_name, password):
    userinfo.create_user(user_name, password)

def delete_user(user_name):
    userinfo.delete_user(user_name)
