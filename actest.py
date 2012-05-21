'''
Created on 2012-5-13

@author: ling0322
'''

import urllib2
import config
import upload_file
import ac_file
import json

try:
    fp = urllib2.urlopen(config.AC_URL + '/create-user?name=root&password=1')
    fp.close()
except:
    pass

upload_file.upload_file(r'e:\1.txt', '/my_folder/1.txt')
upload_file.upload_file(r'e:\3.mdx', '/my_folder/1/1/1/1/1/2.txt')
upload_file.upload_file(r'e:\3.mdx', '/my_folder/3.txt')

print json.dumps(ac_file.listfile())
print json.dumps(ac_file.fetch('/my_folder/1.txt'))

ac_file.delete('/my_folder/1.txt')
print json.dumps(ac_file.listfile())