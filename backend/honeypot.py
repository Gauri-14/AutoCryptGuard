import cv2
import pyautogui
import time
import os
import csv
import sqlite3
import signal
import sys
from datetime import datetime
from pynput import keyboard, mouse

SCREENSHOT_PATH = "../reports/screenshots/"
WEBCAM_PATH = "../reports/webcam/"
LOG_FILE = "../logs/intrusion.csv"
SQLITE_DB = "../logs/intrusion.db"

os.makedirs(SCREENSHOT_PATH, exist_ok=True)
os.makedirs(WEBCAM_PATH, exist_ok=True)
os.makedirs("../logs", exist_ok=True)

last_detection_time = 0
DETECTION_GAP = 5
last_print_time = 0

def take_screenshot(timestamp):
    filename = f"{SCREENSHOT_PATH}screenshot_{timestamp}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    return filename

def capture_webcam(timestamp):
    filename = f"{WEBCAM_PATH}intruder_{timestamp}.jpg"
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(filename, frame)
    cap.release()
    return filename

def log_intrusion(timestamp, screenshot_file, webcam_file):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['timestamp', 'screenshot', 'webcam'])
        writer.writerow([timestamp, screenshot_file, webcam_file])

    try:
        conn = sqlite3.connect(SQLITE_DB)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO intrusion_logs (timestamp, event_type, screenshot_path, webcam_path)
            VALUES (?, ?, ?, ?)
        """, (timestamp, "intrusion", screenshot_file, webcam_file))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[SQLite ERROR] Failed to insert log: {e}")

    print(f"[+] Logged intrusion at {timestamp}")

def log_exit():
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    with open(LOG_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, "EXITED", "None"])

    try:
        conn = sqlite3.connect(SQLITE_DB)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO intrusion_logs (timestamp, event_type, screenshot_path, webcam_path)
            VALUES (?, ?, ?, ?)
        """, (timestamp, "exit", None, None))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[SQLite ERROR] Failed to insert exit log: {e}")

    print(f"[!] Exit time logged at {timestamp}")

def trigger_intrusion(event_type):
    global last_detection_time
    now = time.time()
    if now - last_detection_time > DETECTION_GAP:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        print(f"[⚠️] Intrusion triggered by {event_type} at {timestamp}")
        screenshot = take_screenshot(timestamp)
        webcam = capture_webcam(timestamp)
        log_intrusion(timestamp, screenshot, webcam)
        last_detection_time = now

def on_key_press(key):
    trigger_intrusion("keyboard")

def on_mouse_click(x, y, button, pressed):
    if pressed:
        trigger_intrusion("mouse click")

def on_mouse_move(x, y):
    trigger_intrusion("mouse move")

def exit_gracefully(sig, frame):
    print("\n[!] Ctrl+C detected. Exiting honeypot...")
    log_exit()
    sys.exit(0)

def monitor_intrusion():
    print("[*] Honeypot armed. Monitoring for user interaction...")
    signal.signal(signal.SIGINT, exit_gracefully)

    mouse_listener = mouse.Listener(on_click=on_mouse_click, on_move=on_mouse_move)
    keyboard_listener = keyboard.Listener(on_press=on_key_press)

    mouse_listener.start()
    keyboard_listener.start()

    mouse_listener.join()
    keyboard_listener.join()

if __name__ == "__main__":
    monitor_intrusion()
