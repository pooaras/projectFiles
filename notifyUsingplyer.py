import os
import sys
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        print(f"New file created: {file_path}")
        notification.notify(
            title="New File Created",
            message=f"A new file has been created: {os.path.basename(file_path)}",
            app_name="File Watcher",
        )

def watch_directory(path):
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py /path/to/directory")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory.")
        sys.exit(1)

    watch_directory(directory)

