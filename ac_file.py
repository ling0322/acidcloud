'''
Created on 2012-5-14

@author: ling0322
'''

from ac_request import ac_request
import config
import json
import upload_file

def listfile():
    user_name = config.USER_NAME
    url = "{0}/list".format(config.AC_URL)
    resp, json_meta = ac_request(url)
    return json.loads(json_meta)

def fetch(path):
    url = '{0}/files{1}'.format(config.AC_URL, path)
    resp, content = ac_request(url)
    metadata = json.loads(resp['x-acidcloud-metadata'])
    return metadata, content

def upload(loacl_path, target_path):
    upload_file.upload_file(loacl_path, target_path)

def delete(path):
    url = "{0}/files{1}".format(config.AC_URL, path)
    ac_request(url, method = 'DELETE')