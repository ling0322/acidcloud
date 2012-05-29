'''
Created on 2012-5-22

@author: ling0322
'''
from __future__ import unicode_literals
import tornado.ioloop
import sync_method
import fswatch
import time
import config
import init


def origin():
    try:
        sync_method.init()
    except:
        raise 
    fwtch.start()
    ioloop.add_callback(interval)

def interval():
    ioloop.add_timeout(time.time() + config.PULL_REQUEST_INTERVALS, interval)
    sync_method.pull()
    

init.init()
fwtch = fswatch.FS_Watch.instance()
ioloop = tornado.ioloop.IOLoop.instance()
ioloop.add_callback(origin)
ioloop.start()