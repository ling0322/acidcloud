from __future__ import unicode_literals
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tornado.ioloop
import functools
import sync_method
import config
from lava_potion import relpath, log

def ignore_exception(func):
    def _handler_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log(config.FSWATCH_LOG, "an Exception raised: {0}".format(str(e)), __name__)
            return None
    return _handler_function
    
class LavaPotionEventHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    @ignore_exception
    def on_moved(self, event):
        super(LavaPotionEventHandler, self).on_moved(event)

        if event.is_directory:
            return 
        
        ioloop = tornado.ioloop.IOLoop.instance()
        relpath_src = relpath(event.src_path)
        relpath_dest = relpath(event.dest_path)
        
        ioloop.add_callback(
            functools.partial(sync_method.push, relpath_src, sync_method.DELETE))
        ioloop.add_callback(
            functools.partial(sync_method.push, relpath_dest, sync_method.UPDATE))
        
        log(config.FSWATCH_LOG, "Moved file: from {0} to {1}".format(relpath_src, relpath_dest))

    @ignore_exception
    def on_created(self, event):
        super(LavaPotionEventHandler, self).on_created(event)

        if event.is_directory:
            return 

        ioloop = tornado.ioloop.IOLoop.instance()
        relpath_src = relpath(event.src_path)
        
        ioloop.add_callback(
            functools.partial(sync_method.push, relpath_src, sync_method.UPDATE))
        
        log(config.FSWATCH_LOG, "Created file: {0}".format(relpath_src))

    @ignore_exception
    def on_deleted(self, event):
        super(LavaPotionEventHandler, self).on_deleted(event)

        if event.is_directory:
            return 

        ioloop = tornado.ioloop.IOLoop.instance()
        relpath_src = relpath(event.src_path)

        ioloop.add_callback(
            functools.partial(sync_method.push, relpath_src, sync_method.DELETE))
        
        log(config.FSWATCH_LOG, "Deleted file: {0}".format(relpath_src))

    @ignore_exception
    def on_modified(self, event):
        super(LavaPotionEventHandler, self).on_modified(event)

        if event.is_directory:
            return 

        ioloop = tornado.ioloop.IOLoop.instance()
        relpath_src = relpath(event.src_path)

        ioloop.add_callback(
            functools.partial(sync_method.push, relpath_src, sync_method.UPDATE))
        
        log(config.FSWATCH_LOG, "Modified file: {0}".format(relpath_src))

class FS_Watch:
    inst = None
    
    @classmethod
    def instance(cls):
        if cls.inst == None:
            cls.inst = FS_Watch()
        return cls.inst
    
    def __init__(self):
        self.event_handler = LavaPotionEventHandler()
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path = config.ROOT_PATH, recursive = True)
        
    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()