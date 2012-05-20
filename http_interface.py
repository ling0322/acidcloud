'''
Created on 2012-5-2

@author: ling0322
'''

import webapp2
import json
import upload
import control

from google.appengine.ext.webapp import blobstore_handlers
from check_request import checked_request, get_user_from_request
from google.appengine.ext import blobstore

class MainPage(webapp2.RequestHandler):
    def get(self):
        pass
    
    def post(self, user):
        while True:
            self.response.out.write('Hello, webapp World!')
            self.response.out.flush()

class StartUpload(webapp2.RequestHandler):  
    
    @checked_request
    def post(self, user, path):
        metadata = json.loads(self.request.body)
        upload_id = control.upload_file(user, path, metadata)
        self.response.body = 'OK' if upload_id == None else str(upload_id)
        
class Upload(webapp2.RequestHandler):  
    
    @checked_request
    def post(self, upload_id, block_index):
        upload.append_block(int(upload_id), int(block_index), 
                            self.request.body)

class FinishUpload(webapp2.RequestHandler):  
    
    @checked_request
    def get(self, upload_id):
        upload.finish_upload(int(upload_id))

class CreateUser(webapp2.RequestHandler):
    def get(self):
        name = self.request.GET['name']
        password = self.request.GET['password']
        control.create_user(name, password)

class List(webapp2.RequestHandler):
    
    @checked_request
    def get(self, user):
        self.response.body = json.dumps(control.get_list(user))

class Delete(webapp2.RequestHandler):
    
    @checked_request
    def get(self, path):
        control.delete_file(get_user_from_request(self.request), path)    

class Fetch(blobstore_handlers.BlobstoreDownloadHandler):
    
    @checked_request
    def get(self, path):
        user = get_user_from_request(self.request)
        gspath = control.get_file_gspath(user, path)
        size = control.file_metadata(user, path)['size']
        self.response.headers.add('Content-Length', str(size))
        self.send_blob(blobstore.create_gs_key(gspath))
    
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/start-upload/([^/]+)(/.+)', StartUpload),
                               ('/upload/([0-9]+)/([0-9]+)', Upload),
                               ('/finish-upload/([0-9]+)', FinishUpload),
                               ('/list/(.+)', List),
                               ('/fetch(/.+)', Fetch),
                               ('/create-user', CreateUser),
                               ('/delete(/.+)', Delete),
                               ],
                              debug=True)