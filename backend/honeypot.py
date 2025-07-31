import cv2
import pyautogui
import time
import os
import csv
import sys
import threading
import psycopg2
from datetime import datetime
from pynput import keyboard, mouse

SCREENSHOT_PATH = "../reports/screenshots/"
WEBCAM_PATH = "../reports/webcam/"
LOG_FILE = "../logs/intrusion.csv"

DB_NAME = "autocryptguard"
DB_USER = "postgres"
DB_PASSWORD = "Gauri14"
DB_HOST = "localhost"
DB_PORT = "5432"

os.makedirs(SCREENSHOT_PATH, exist_ok=True)
os.makedirs(WEBCAM_PATH, exist_ok=True)
os.makedirs("../logs", exist_ok=True)

last_log_time = 0
last_activity_time = time.time()
idle_printed = False
log_lock = threading.Lock()
stop_event = threading.Event()

def get_pg_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

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
            writer.writerow(['timestamp', 'event_type', 'screenshot', 'webcam'])
        writer.writerow([timestamp, "intrusion", screenshot_file, webcam_file])

    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO intrusion_logs (timestamp, event_type, screenshot_path, webcam_path)
                    VALUES (%s, %s, %s, %s)
                """, (timestamp, "intrusion", screenshot_file, webcam_file))
                conn.commit()
    except Exception as e:
        print(f"[PostgreSQL ERROR] Failed to insert log: {e}")

    print(f"[🚨] Intrusion logged at {timestamp}")

def trigger_intrusion(event_type):
    global last_log_time, last_activity_time, idle_printed
    now = time.time()
    last_activity_time = now
    idle_printed = False

    if now - last_log_time >= 1:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        print(f"[⚠️] Intrusion detected by {event_type} at {timestamp}")
        screenshot = take_screenshot(timestamp)
        webcam = capture_webcam(timestamp)
        log_intrusion(timestamp, screenshot, webcam)
        last_log_time = now

def log_exit():
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    with open(LOG_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, "EXITED", "None", "None"])

    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO intrusion_logs (timestamp, event_type, screenshot_path, webcam_path)
                    VALUES (%s, %s, %s, %s)
                """, (timestamp, "exit", None, None))
                conn.commit()
    except Exception as e:
        print(f"[PostgreSQL ERROR] Failed to insert exit log: {e}")
    print(f"[✔] Honeypot exited gracefully at {timestamp}")

def on_key_press(key):
    global last_activity_time
    last_activity_time = time.time()

    try:
        if key == keyboard.Key.esc:
            print("[!] ESC key pressed. Exiting...")
            stop_event.set()
            log_exit()
            return False  
        else:
            trigger_intrusion("keyboard")
    except AttributeError:
        trigger_intrusion("keyboard")

def on_mouse_click(x, y, button, pressed):
    if pressed and not stop_event.is_set():
        trigger_intrusion("mouse click")

def on_mouse_move(x, y):
    if not stop_event.is_set():
        trigger_intrusion("mouse move")

def idle_monitor():
    global idle_printed
    print("[*] System is idle.")
    idle_printed = True  
    while not stop_event.is_set():
        now = time.time()
        if now - last_activity_time >= 10 and not idle_printed:
            print("[*] System is idle.")
            idle_printed = True
        time.sleep(1)

def monitor_intrusion():
    print("[*] Honeypot armed. Monitoring for user interaction...")

    mouse_listener = mouse.Listener(on_click=on_mouse_click, on_move=on_mouse_move)
    keyboard_listener = keyboard.Listener(on_press=on_key_press)

    mouse_listener.start()
    keyboard_listener.start()

    idle_thread = threading.Thread(target=idle_monitor)
    idle_thread.start()

    keyboard_listener.join()
    mouse_listener.stop()   
    idle_thread.join()
    print("[✔] All monitoring stopped.")

if __name__ == "__main__":
    monitor_intrusion()
