'''
Created on 2012-5-21

@author: ling0322
'''

from google.appengine.ext import db
from uuid import uuid4 as random_uuid
import acidcloud
import control

class Fetch(db.Model):
    fetch_id = db.StringProperty(required = True)
    user = db.StringProperty(required = True)
    path = db.TextProperty(required = True)
    
def init_fetch(user, path):
    if control.file_metadata(user, path) == None:
        raise acidcloud.ItemNotFoundException('file', path)
    fetch_id = random_uuid()
    fetch = Fetch(
        fetch_id = fetch_id,
        user = user,
        path = path)
    fetch.put()
    return fetch_id

def do_fetch(fetch_id):
    q = Fetch.all()
    q.filter("fetch_id =", fetch_id)
    fet = q.get()
    if fet == None:
        raise acidcloud.ItemNotFoundException('fetch_id')
    user = fet.user
    path = fet.path
    fet.delete()
    return user, path
    
