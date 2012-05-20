'''
Created on 2012-5-9

@author: ling0322
'''

from google.appengine.ext import db
from datetime import datetime
import config
from email.utils import parsedate
import gsfile
import metadata

event_finished = []

class UploadMetadata(db.Model):
    target_path = db.StringProperty(required = True)
    user = db.StringProperty(required = True)
    size = db.IntegerProperty(required = True)
    modified_time = db.DateTimeProperty(required = True)
    start_time = db.DateTimeProperty(required = True, auto_now_add = True)
    file_id = db.IntegerProperty(required = True)
    sha1 = db.StringProperty(required = True)

def start_upload(user, path, metadata):
    file_id = gsfile.start_upload(metadata['sha1'], metadata['size'])
    item = UploadMetadata(
        target_path = path,
        user = user,
        size = metadata['size'],
        modified_time = datetime(*parsedate(metadata['modified'])[:6]),
        file_id = file_id,
        sha1 = metadata['sha1'])
        
    item.put()
    return item.key().id()

def append_block(upload_id, index, content):
    up_item = UploadMetadata.get_by_id(upload_id)
    gsfile.append(up_item.file_id, content, index * config.UPLOAD_BLOCK_SIZE)

def finish_upload(upload_id):
    up_item = UploadMetadata.get_by_id(upload_id)
    gsfile.finish_upload(up_item.file_id)
    file_metadata = dict(
        size = up_item.size,
        modified = up_item.modified_time,
        sha1 = up_item.sha1)
    up_item.delete()
    metadata._on_upload_finished(up_item.user, up_item.target_path, file_metadata)

