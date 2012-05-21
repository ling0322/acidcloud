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

class ac_request_handler(webapp2.RequestHandler):
    def getusr(self):
        return get_user_from_request(self.request)

class MainPage(ac_request_handler):
    def get(self):
        pass
    
    def post(self, user):
        while True:
            self.response.out.write('Hello, webapp World!')
            self.response.out.flush()

class StartUpload(ac_request_handler):  
    
    def post(self, user, path):
        metadata = json.loads(self.request.body)
        upload_id = control.upload_file(user, path, metadata)
        self.response.body = 'OK' if upload_id == None else str(upload_id)
        
class Upload(ac_request_handler):  
    
    def post(self, upload_id, block_index):
        upload.append_block(int(upload_id), int(block_index), 
                            self.request.body)

class FinishUpload(ac_request_handler):  
    
    def get(self, upload_id):
        upload.finish_upload(int(upload_id))

class CreateUser(ac_request_handler):
    def get(self):
        name = self.request.GET['name']
        password = self.request.GET['password']
        control.create_user(name, password)

class List(ac_request_handler):
    
    def get(self):
        self.response.body = json.dumps(control.get_list(self.getusr()))

class Delete(ac_request_handler):
    
    def get(self, path):
        control.delete_file(self.getusr(), path)    

class FilesHandler(blobstore_handlers.BlobstoreDownloadHandler, ac_request_handler):
    
    def get(self, path):
        gspath = control.get_file_gspath(self.getusr(), path)
        size = control.file_metadata(self.getusr(), path)['size']
        self.response.headers.add('Content-Length', str(size))
        self.response.headers.add('x-acidcloud-metadata', json.dumps(control.file_metadata(self.getusr(), path)))
        self.send_blob(blobstore.create_gs_key(gspath))
    
    def delete(self, path):
        control.delete_file(self.getusr(), path)
        

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/start-upload/([^/]+)(/.+)', StartUpload),
                               ('/upload/([0-9]+)/([0-9]+)', Upload),
                               ('/finish-upload/([0-9]+)', FinishUpload),
                               ('/list', List),
                               ('/files(/.+)', FilesHandler),
                               ('/create-user', CreateUser),
                               ],
                              debug=True)