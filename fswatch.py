import time
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import logging
logging.getLogger().setLevel(logging.DEBUG)
if __name__ == "__main__":
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=r'd:\test', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        observer.stop()
    # observer.join()