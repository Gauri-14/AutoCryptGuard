# backend/usb_monitor.py

import wmi
import csv
from datetime import datetime
import time
import os
import threading
import pythoncom  # Required for COM initialization in threads

LOG_FILE = "../logs/usb.csv"
os.makedirs("../logs", exist_ok=True)

def log_usb_event(event_type, device_name):
    with open(LOG_FILE, mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), event_type, device_name])

def monitor_usb_insertions():
    pythoncom.CoInitialize()  # 👈 Required for WMI in threads
    c = wmi.WMI()
    watcher = c.Win32_USBControllerDevice.watch_for("creation")
    print("🔌 Monitoring USB insertions...")

    while True:
        try:
            usb_device = watcher()
            device_info = usb_device.Dependent
            log_usb_event("INSERT", str(device_info))
            print(f"[+] USB Inserted: {device_info}")
        except Exception:
            continue

def monitor_usb_removals():
    pythoncom.CoInitialize()  # 👈 Required for WMI in threads
    c = wmi.WMI()
    watcher = c.Win32_USBControllerDevice.watch_for("deletion")
    print("❌ Monitoring USB removals...")

    while True:
        try:
            usb_device = watcher()
            device_info = usb_device.Dependent
            log_usb_event("REMOVE", str(device_info))
            print(f"[-] USB Removed: {device_info}")
        except Exception:
            continue

if __name__ == "__main__":
    try:
        insert_thread = threading.Thread(target=monitor_usb_insertions, daemon=True)
        remove_thread = threading.Thread(target=monitor_usb_removals, daemon=True)

        insert_thread.start()
        remove_thread.start()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🚫 Stopped USB monitoring.")
