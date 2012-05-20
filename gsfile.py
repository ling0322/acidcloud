from google.appengine.ext import db
from uuid import uuid4 as random_uuid
from google.appengine.api import files
import hashlib

READ_SIZE_MAX = 24 * 1024 * 1024

class File(db.Model):
    read_path = db.TextProperty(required = True)
    write_path = db.TextProperty(required = True)
    size = db.IntegerProperty(required = True)
    sha1 = db.StringProperty(required = True)
    upload_time = db.DateTimeProperty(auto_now_add = True)
    access_time = db.DateTimeProperty(auto_now = True)
    visit_count = db.IntegerProperty(required = True)
    upload_finished = db.BooleanProperty(required = True)
    current_size = db.IntegerProperty(required = True)
    
def start_upload(sha1, size):
    file_path = '/gs/acid-cloud/' + str(random_uuid()) + '.block'
    gs_path = files.gs.create(file_path)
    file_item = File(
        read_path = file_path,
        write_path = gs_path,
        size = size,
        sha1 = sha1.lower(),
        visit_count = 0,
        upload_finished = False,
        current_size = 0)
    file_item.put()
    return file_item.key().id()

def append(file_id, content, pos):
    
    # pos should be current_size
    
    file_item = File.get_by_id(file_id)
    size = file_item.size
    current_size = file_item.current_size
    
    if current_size + len(content) > size:
        raise Exception('file size error')
    
    if pos != current_size:
        raise Exception('invaild position')
        
    write_path = file_item.write_path
    with files.open(write_path, 'a') as fp:
        fp.write(content)
        
    file_item.current_size = pos + len(content)
    file_item.put()
        
    
def finish_upload(file_id):
    file_item = File.get_by_id(file_id)
    size = file_item.size
    current_size = file_item.current_size
    write_path = file_item.write_path
    files.finalize(write_path)
    
    if size != current_size:
        file_item.delete()
        raise Exception('file size error')
    
    # check sha1 
    
    sh = hashlib.sha1()
    with files.open(file_item.read_path, 'r') as fp:
        buf = fp.read(1000000)
        while buf:
            sh.update(buf)
            buf = fp.read(1000000)
        
    sha1_value = sh.hexdigest()
    if sha1_value != file_item.sha1:
        file_item.delete()
        raise Exception('file size error')
    
    file_item.upload_finished = True
    file_item.put()

def exists(sha1):
    q = File.all()
    q.filter("sha1 =", sha1.lower())
    file_item = q.get()
    return True if file_item != None else False    
 
def get_gs_path(sha1):
    q = File.all()
    q.filter("sha1 =", sha1)
    file_item = q.get()
    if file_item == None or file_item.upload_finished == False:
        raise Exception('file not exists')
    
    return file_item.read_path
       
    
    
    
    
    