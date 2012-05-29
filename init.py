'''
Created on 2012-5-27

@author: ling0322
'''

import config
from ac_request import ac_request
import json
import os
from lava_potion import log

def account_info(user):
    url = "{0}/user".format(config.AC_URL)
    try:
        resp, json_userinfo = ac_request(url)
    except:
        return None
    return json.loads(json_userinfo)

def input_account():
    is_valid = False
    while is_valid == False:
        user = raw_input('Username: ')
        password = config.hash_password(raw_input('Password: '))
        config.PASSOWRD = password
        config.USER_NAME = user
        user_info = account_info(user)
        if user_info == None:
            print 'Invalid username or password!'
        else:
            print 'OK'
            is_valid = True

def init():
    print 'Lava_potion starting ...'
    conf = None
    try:
        conf = json.load(open(config.CONFIG_PATH, 'r'))
    except:
        if os.path.exists(config.CONFIG_PATH):
            os.remove(config.CONFIG_PATH)
        
    if conf == None:
        print 'Lava_Potion configuration'
        input_account()
        local_path = raw_input('local sync path: ')
        config.ROOT_PATH = local_path
        json.dump(dict(
            username = config.USER_NAME,
            password = config.PASSOWRD,
            local_path = config.ROOT_PATH), open(config.CONFIG_PATH, 'w'))
    else:
        config.USER_NAME = conf['username']
        config.PASSOWRD = conf['password']
        config.ROOT_PATH = conf['local_path']
        
    log(config.INIT_LOG, 'load configuration success', __name__)
    
        
    
        
        