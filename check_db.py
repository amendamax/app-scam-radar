import sqlite3
try:
    conn = sqlite3.connect("app_scams.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM malicious_apps")
    print(f"Total apps in LOCAL DB: {c.fetchone()[0]}")
except Exception as e:
    print(e)
