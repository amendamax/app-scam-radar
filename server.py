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


@app.get("/sitemap.xml", response_class=HTMLResponse)
def sitemap():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT slug FROM malicious_apps ORDER BY id DESC")
    rows = c.fetchall()
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Base URL
    xml += '<url>\n'
    xml += '  <loc>https://app-scam-radar.onrender.com/</loc>\n'
    xml += '  <changefreq>daily</changefreq>\n'
    xml += '  <priority>1.0</priority>\n'
    xml += '</url>\n'
    
    for row in rows:
        xml += '<url>\n'
        xml += f'  <loc>https://app-scam-radar.onrender.com/report/{row[0]}</loc>\n'
        xml += '  <changefreq>monthly</changefreq>\n'
        xml += '  <priority>0.8</priority>\n'
        xml += '</url>\n'
        
    xml += '</urlset>'
    return HTMLResponse(content=xml, media_type="application/xml")

@app.get("/report/{slug}", response_class=HTMLResponse)
def get_report(slug: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT app_name, package_id, platform, threat_type, risk_level, status, description, added_date FROM malicious_apps WHERE slug = ?", (slug,))
    row = c.fetchone()
    
    if not row:
        return HTMLResponse("<h1>404 - Report not found</h1>", status_code=404)
        
    app_name, package_id, platform, threat_type, risk_level, status, description, added_date = row
    
    color = "#ef4444" if risk_level == "Critical" else "#fbbf24"
    
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{app_name} - Malware Analysis & Removal Guide | AppScamRadar</title>
        <meta name="description" content="Security report for {app_name} ({package_id}). Detected as {threat_type}. Read our full analysis and learn how to remove this {risk_level} threat.">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{
                background-color: #03060a;
                background-image: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, transparent 100%);
                color: #f8fafc;
                font-family: 'Outfit', sans-serif;
                margin: 0; padding: 40px 20px;
            }}
            .container {{ max-width: 800px; margin: 0 auto; background: rgba(15, 23, 42, 0.6); padding: 40px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); backdrop-filter: blur(12px); }}
            h1 {{ font-size: 32px; margin-top: 0; color: #fff; }}
            .badge {{ display: inline-block; padding: 6px 12px; border-radius: 6px; font-weight: 700; font-size: 14px; background: rgba(239, 68, 68, 0.2); color: {color}; border: 1px solid {color}; margin-bottom: 20px; }}
            .detail-group {{ margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 20px; }}
            .label {{ color: #94a3b8; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-bottom: 8px; }}
            .value {{ font-size: 18px; font-weight: 600; font-family: 'JetBrains Mono', monospace; }}
            .desc {{ font-size: 18px; line-height: 1.6; color: #cbd5e1; }}
            .back-btn {{ display: inline-block; margin-bottom: 30px; color: #38bdf8; text-decoration: none; font-weight: 600; }}
            .back-btn:hover {{ text-decoration: underline; }}
            .monetize-box {{ margin-top: 40px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); padding: 25px; border-radius: 12px; text-align: center; }}
            .monetize-btn {{ display: inline-block; background: #10b981; color: #000; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 18px; margin-top: 15px; transition: transform 0.2s; }}
            .monetize-btn:hover {{ transform: scale(1.05); }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-btn"><i class="fa-solid fa-arrow-left"></i> Back to Radar</a>
            <div class="badge">{risk_level} THREAT</div>
            <h1>{app_name}</h1>
            
            <div class="detail-group">
                <div class="label">Technical Analysis</div>
                <div class="desc">{description}</div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="detail-group">
                    <div class="label">Package ID / Hash</div>
                    <div class="value">{package_id}</div>
                </div>
                <div class="detail-group">
                    <div class="label">Threat Family</div>
                    <div class="value">{threat_type}</div>
                </div>
                <div class="detail-group">
                    <div class="label">Platform</div>
                    <div class="value">{platform}</div>
                </div>
                <div class="detail-group">
                    <div class="label">Date Logged</div>
                    <div class="value">{added_date}</div>
                </div>
            </div>
            
            <div class="monetize-box">
                <h3 style="margin-top: 0; color: #34d399;"><i class="fa-solid fa-shield-virus"></i> Device Compromised?</h3>
                <p style="color: #9ca3af; margin-bottom: 20px;">If you installed this application, your financial data is at risk. We recommend trading in a secure sandbox environment.</p>
                <a href="https://isbrokersafe.com" class="monetize-btn">Protect Your Funds Now</a>
            </div>
        </div>
    </body>
    </html>
    '''
    return html



@app.on_event("startup")
async def start_harvester():
    asyncio.create_task(daily_harvester())
