'''
Created on 2012-5-15

@author: ling0322
'''

import logging

def log(log_switch, msg):
    if log_switch == True:
        logging.warning(msg)