import sqlite3

conn = sqlite3.connect("logs/intrusion.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS intrusion_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        screenshot_path TEXT,
        webcam_path TEXT
    );
""")

conn.commit()
conn.close()
