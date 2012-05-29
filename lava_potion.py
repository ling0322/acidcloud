'''
Created on 2012-5-15

@author: ling0322
'''

import logging
import os
import config

def log(log_switch, msg, category = 'lava_potion'):
    if log_switch == True and config.ENABLE_LOG == True:
        logging.warning(category + ': ' + msg)

def relpath(abs_path):
    return '/' + os.path.relpath(abs_path, config.ROOT_PATH).replace('\\', '/')

class ItemNotFoundException(Exception):
    def __init__(self, item_name, item_desc = ""):
        self.item_name = item_name
        self.item_desc = item_desc
    def __str__(self):
        return self.item_name + ' not found.'
    
def encode_if_necessary(s):
    if isinstance(s, unicode):
        return s.encode('utf-8')
    return s