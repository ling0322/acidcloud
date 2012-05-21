'''
Created on 2012-5-9

@author: ling0322
'''

from hashlib import md5

def _hash_password(original_password):
    if isinstance(original_password, unicode):
        original_password = original_password.encode('utf8')
    m = md5(MAGIC_STRING + original_password)
    return m.hexdigest()

MAGIC_STRING = 'A.c-1d::cI0u.D'
UPLOAD_BLOCK_SIZE = 2 * 1024 * 1024
USER_NAME = 'root'
PASSOWRD = _hash_password('1')
RETRY_TIMES = 1
DEBUG = True
AC_URL = "http://localhost:8080"
ROOT_PATH = r'e:\ac_test'
CONSUMER_KEY = 'lava_potion'
CONSUMER_SECRET = 'lava_potion'

SYNC_METHOD_LOG = True
METADATA_LOG = True