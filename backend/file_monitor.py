import os
import time
import csv
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

MONITOR_FOLDER = r"C:\Users\Admin\OneDrive\Desktop"  
LOG_FILE = "../logs/file_monitor.csv"

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

hash_cache = {}
event_cache = {}
FOLDER_EVENT_CACHE = {}

EVENT_TTL = 10  
IGNORED_FILES = {'desktop.ini', 'Thumbs.db'}

def calculate_hash(file_path):
    try:
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                sha256 = hashlib.sha256()
                while chunk := f.read(4096):
                    sha256.update(chunk)
                return sha256.hexdigest()
    except Exception:
        pass
    return ""

def should_log(event_type, path, file_hash):
    now = time.time()
    key = (event_type, path)

    if os.path.basename(path) in IGNORED_FILES:
        return False

    last_event_time = event_cache.get(key)
    if last_event_time and now - last_event_time < EVENT_TTL:
        return False

    if event_type == "MODIFIED" and os.path.isdir(path):
        try:
            folder_files = [
                os.path.join(path, f)
                for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))
            ]
            for file in folder_files:
                file_hash_now = calculate_hash(file)
                if hash_cache.get(file) != file_hash_now:
                    hash_cache[file] = file_hash_now
                    FOLDER_EVENT_CACHE[path] = now
                    break
            else:
                last_time = FOLDER_EVENT_CACHE.get(path)
                if last_time and now - last_time < EVENT_TTL:
                    return False
                return False
        except Exception:
            return False

    if os.path.isfile(path) and event_type == "MODIFIED":
        if hash_cache.get(path) == file_hash:
            return False
        hash_cache[path] = file_hash

    event_cache[key] = now
    return True

def log_event(event_type, path):
    is_dir = "FOLDER" if os.path.isdir(path) else "FILE"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_hash = ""

    if is_dir == "FILE" and os.path.exists(path):
        file_hash = calculate_hash(path)

    if not should_log(event_type, path, file_hash):
        return

    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, event_type, is_dir, path, file_hash])

    print(f"[{event_type}] {is_dir}: {path}")

class FileEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        log_event("CREATED", event.src_path)

    def on_modified(self, event):
        log_event("MODIFIED", event.src_path)

    def on_deleted(self, event):
        log_event("DELETED", event.src_path)
        hash_cache.pop(event.src_path, None)

    def on_moved(self, event):
        log_event("MOVED_FROM", event.src_path)
        log_event("MOVED_TO", event.dest_path)
        if event.src_path in hash_cache:
            hash_cache[event.dest_path] = hash_cache.pop(event.src_path)

def start_monitoring():
    print(f"📂 Monitoring folder: {MONITOR_FOLDER}... Press Ctrl+C to stop.")
    event_handler = FileEventHandler()
    observer = Observer()
    observer.schedule(event_handler, MONITOR_FOLDER, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("❌ Stopped monitoring.")
    observer.join()

if __name__ == "__main__":
    start_monitoring()
