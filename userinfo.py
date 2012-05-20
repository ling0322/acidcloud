'''
Created on 2012-5-10

@author: ling0322
'''

from google.appengine.ext import db
from hashlib import md5
import config
import metadata

@db.transactional
def _on_file_created(file_metadata):
    size = file_metadata['size']
    item = User.get_by_key_name(file_metadata['user'].lower())
    if item == None:
        return
    
    item.space_used += size
    item.sync_version += 1
    item.put()
    
@db.transactional
def _on_file_removed(file_metadata):
    size = file_metadata['size']
    item = User.get_by_key_name(file_metadata['user'].lower())
    if item == None:
        return
    
    item.space_used -= size
    item.sync_version += 1
    item.put()

class User(db.Model):
    password = db.StringProperty(required = True)
    space_used = db.IntegerProperty(required = True)
    space_limit = db.IntegerProperty(required = True)
    sync_version = db.IntegerProperty(required = True)
    
def _hash_password(original_password):
    if isinstance(original_password, unicode):
        original_password = original_password.encode('utf8')
    m = md5(config.MAGIC_STRING + original_password)
    return m.hexdigest()

def get_user_key(name):
    return User.get_by_key_name(name.lower())

def create_user(name, password):
    
    name = name.lower()
    u = User(
        key_name = name,
        password = _hash_password(password),
        space_used = 0,
        sync_version = 0,
        space_limit = config.USER_SPACE_LIMIT)
    u.put()
    
def delete_user(name):

    name = name.lower()
    u = User.get_by_key_name(name)
    if u == None:
        return
    metadata._on_user_deleted(u.name)
    u.delete()
        
def user_info(name):
    
    name = name.lower()
    u = User.get_by_key_name(name)
    return dict(
        name = u.key().name(),
        password = u.password,
        syncver = u.sync_version,
        space_used = u.space_used,
        space_limit = u.space_limit)