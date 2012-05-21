'''
Created on 2012-5-15

@author: ling0322
'''

import hashlib
import logging

def log(log_switch, msg):
    if log_switch == True:
        logging.warning(msg)

class ItemNotFoundException(Exception):
    def __init__(self, item_name, item_desc = ""):
        self.item_name = item_name
        self.item_desc = item_desc
    def __str__(self):
        return self.item_name + ' not found.'