'''
Created on 2012-5-2

@author: ling0322
'''

from google.appengine.ext import db
import userinfo
import hashlib

def _on_upload_finished(user, path, metadata):
    
    put_metadata(
        user_name = user, 
        path = path, 
        size = metadata['size'],
        mtime = metadata['mtime'],
        sha1 = metadata['sha1'])

def _on_user_deleted(user_name):
    q = MetadataModel.all()
    q.filter("user =", user_name.lower())
    for f in q.run():
        f.delete()

class MetadataModel(db.Model):
    user = db.StringProperty(required = True)
    path = db.TextProperty(required = True)
    md5_path = db.StringProperty(required = True)
    size = db.IntegerProperty(required = True)
    mtime = db.FloatProperty(required = True)
    sha1 = db.StringProperty(required = True)


def put_metadata(user_name, path, size, mtime, sha1):
    remove_metadata(user_name, path)
    
    user_key = userinfo.get_user_key(user_name)
    if user_key == None:
        raise Exception('user not exist')
    
    mm = MetadataModel(
        user = user_name,
        path = path,
        md5_path = hashlib.md5(path).hexdigest(),
        size = size,
        mtime = mtime,
        sha1 = sha1)
    mm.put()
    userinfo._on_file_created(_dict_metadata(mm))

def remove_metadata(user_name, path):
    user_key = userinfo.get_user_key(user_name)
    if user_key == None:
        raise Exception('user not exist')
    
    q = MetadataModel.all()
    q.filter('user =', user_name)
    q.filter("md5_path =", hashlib.md5(path).hexdigest())
    for item in q.run():
        item.delete()
        userinfo._on_file_removed(_dict_metadata(item))

def _dict_metadata(item):
    return dict(
        user = item.user,
        path = item.path,
        size = item.size,
        mtime = item.mtime,
        sha1 = item.sha1)   
     
def list_metadata(user_name):
    user_key = userinfo.get_user_key(user_name)
    if user_key == None:
        raise Exception('user not exist')
    
    q = MetadataModel.all()
    q.filter('user =', user_name)
    metadata_list = {}
    for metadata in q.run():
        metadata_list[metadata.path] = _dict_metadata(metadata)
    
    return metadata_list

def get_metadata(user_name, path):
    user_key = userinfo.get_user_key(user_name)
    if user_key == None:
        raise Exception('user not exist')
    
    q = MetadataModel.all()
    q.filter('user =', user_name) 
    q.filter("md5_path =", hashlib.md5(path).hexdigest())
    
    r = q.get()
    if r != None:
        return _dict_metadata(r)
    else:
        return None