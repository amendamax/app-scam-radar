from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from fastapi.staticfiles import StaticFiles
import sqlite3
import os

app = FastAPI()
DB_PATH = "app_scams.db"
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS malicious_apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE,
            app_name TEXT,
            package_id TEXT,
            platform TEXT,
            threat_type TEXT,
            risk_level TEXT,
            status TEXT,
            description TEXT,
            added_date TEXT
        )
    """)

    conn.commit()
    
    # Check if empty, then seed
    c.execute("SELECT COUNT(*) FROM malicious_apps")
    if c.fetchone()[0] == 0:
        import seed_db
        seed_db.seed_demo_malware()
    
    conn.close()


init_db()

# Read index.html
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


# API for frontend
@app.get("/api/v1/apps")
def get_apps(search: str = "", page: int = 1, limit: int = 50):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    offset = (page - 1) * limit
    
    if search:
        search_term = f"%{search}%"
        c.execute('''
            SELECT slug, app_name, package_id, platform, threat_type, risk_level, status
            FROM malicious_apps
            WHERE app_name LIKE ? OR package_id LIKE ? OR threat_type LIKE ?
            ORDER BY id DESC LIMIT ? OFFSET ?
        ''', (search_term, search_term, search_term, limit, offset))
        rows = c.fetchall()
        
        c.execute('''
            SELECT COUNT(*) FROM malicious_apps
            WHERE app_name LIKE ? OR package_id LIKE ? OR threat_type LIKE ?
        ''', (search_term, search_term, search_term))
        total = c.fetchone()[0]
    else:
        c.execute('''
            SELECT slug, app_name, package_id, platform, threat_type, risk_level, status
            FROM malicious_apps
            ORDER BY id DESC LIMIT ? OFFSET ?
        ''', (limit, offset))
        rows = c.fetchall()
        
        c.execute("SELECT COUNT(*) FROM malicious_apps")
        total = c.fetchone()[0]
        
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "slug": r[0],
            "app_name": r[1],
            "package_id": r[2],
            "platform": r[3],
            "threat_type": r[4],
            "risk_level": r[5],
            "status": r[6]
        })
        
    return {"total": total, "results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)

import asyncio
import subprocess

async def daily_harvester():
    while True:
        try:
            print("Running daily MalwareBazaar harvester...")
            subprocess.run(["python", "harvester.py"], check=False)
        except Exception as e:
            print(f"Harvester error: {e}")
        # Run every 24 hours
        await asyncio.sleep(86400)

@app.on_event("startup")
async def start_harvester():
    asyncio.create_task(daily_harvester())
