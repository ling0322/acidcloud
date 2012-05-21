'''
Created on 2012-5-14

@author: ling0322
'''

from ac_request import ac_request
import config
import json
import upload_file
import httplib

def listfile():
    user_name = config.USER_NAME
    url = "{0}/list/{1}".format(config.AC_URL, user_name)
    json_meta = ac_request(url)
    return json.loads(json_meta)

def fetch(path):
    conn = httplib.HTTPConnection(config.AC_URL)
    conn.request("GET", '/fetch'path)
    url = '{0}/fetch{1}'.format(config.AC_URL, path)
    content = ac_request(url)
    return content

def upload(loacl_path, target_path):
    upload_file.upload_file(loacl_path, target_path)

def delete(path):
    url = "{0}/delete{1}".format(config.AC_URL, path)
    ac_request(url)