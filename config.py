'''
Created on 2012-5-9

@author: ling0322
'''

from hashlib import md5

def hash_password(original_password):
    if isinstance(original_password, unicode):
        original_password = original_password.encode('utf8')
    m = md5(MAGIC_STRING + original_password)
    return m.hexdigest()

MAGIC_STRING = 'A.c-1d::cI0u.D'
UPLOAD_BLOCK_SIZE = 2 * 1024 * 1024
USER_NAME = None
PASSOWRD = None

DEBUG = False

ROOT_PATH = None
CONSUMER_KEY = 'lava_potion'
CONSUMER_SECRET = 'lava_potion'
PULL_REQUEST_INTERVALS = 30
PUSH_RETRY_INTERVALS = 10
CONFIG_PATH = 'lavapotion.conf'

if DEBUG == True:
    RETRY_TIMES = 1
    AC_URL = "http://localhost:8080"
    PUSH_RETRY_TIMES = 1
    ENABLE_LOG = True
else:
    RETRY_TIMES = 1
    AC_URL = "http://localhost:8082"
    PUSH_RETRY_TIMES = 1    
    ENABLE_LOG = True



SYNC_METHOD_LOG = True
METADATA_LOG = True
FSWATCH_LOG = True
UPLOAD_FILE_LOG = True
ACREQUEST_LOG = True
INIT_LOG = True