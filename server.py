from fastapi import FastAPI, Request

from fastapi.responses import HTMLResponse, JSONResponse



from fastapi.staticfiles import StaticFiles

import sqlite3

import os



app = FastAPI()

import urllib.request

@app.get("/admin/force-sync-db")
async def force_sync_db(secret: str):
    if secret != "vasile2026":
        return {"error": "Unauthorized"}
    try:
        url = "https://raw.githubusercontent.com/amendamax/app-scam-radar/main/app_scams.db"
        urllib.request.urlretrieve(url, DB_PATH)
        return {"status": "Success", "message": "app_scams.db downloaded and overwritten from GitHub raw!"}
    except Exception as e:
        return {"error": str(e)}


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

def sitemap(request: Request):

    conn = sqlite3.connect(DB_PATH)

    c = conn.cursor()

    c.execute("SELECT slug FROM malicious_apps ORDER BY id DESC")

    rows = c.fetchall()

    

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'

    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    

    # Base URL

    xml += '<url>\n'

    xml += '  <loc>https://appscamradar.com/</loc>\n'

    xml += '  <changefreq>daily</changefreq>\n'

    xml += '  <priority>1.0</priority>\n'

    xml += '</url>\n'

    

    for row in rows:

        xml += '<url>\n'

        xml += f'  <loc>https://appscamradar.com/report/{row[0]}</loc>\n'

        xml += '  <changefreq>monthly</changefreq>\n'

        xml += '  <priority>0.8</priority>\n'

        xml += '</url>\n'

        

    xml += '</urlset>'

    return HTMLResponse(content=xml, media_type="application/xml")



@app.get("/report/{slug}", response_class=HTMLResponse)

def get_report(slug: str):

    conn = sqlite3.connect(DB_PATH)

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

        <meta name="google-site-verification" content="_UoEuIcslAcPkg7YgpdYmWhmlpWW0M3t97xdHm27z38" />

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

    

<!-- Google tag (gtag.js) -->

<script async src="https://www.googletagmanager.com/gtag/js?id=G-6V4XM02QDM"></script>

<script>

  window.dataLayer = window.dataLayer || [];

  function gtag(){{dataLayer.push(arguments);}}

  gtag('js', new Date());



  gtag('config', 'G-6V4XM02QDM');

</script>

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

    

        <footer class="vasiledev-ecosystem-footer" style="background: #03060a; border-top: 1px solid rgba(255, 255, 255, 0.1); padding: 50px 20px 24px; font-family: 'Inter', system-ui, -apple-system, sans-serif; color: #94a3b8; font-size: 0.85rem; line-height: 1.6; text-align: left; margin-top: 60px;">
        <div style="max-width: 1140px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 36px; margin-bottom: 36px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                    <span style="display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; border-radius: 8px; background: rgba(56, 189, 248, 0.15); color: #38bdf8; font-size: 16px;">
                        <i class="fa-solid fa-bug"></i>
                    </span>
                    <span style="font-family: 'Outfit', sans-serif; font-size: 18px; font-weight: 800; color: #ffffff; letter-spacing: -0.3px;">
                        APPSCAM<strong style="color: #38bdf8;">RADAR</strong>
                    </span>
                </div>
                <p style="color: #94a3b8; font-size: 0.85rem; line-height: 1.5; margin: 0 0 12px 0;">
                    Global mobile threat intelligence. Scanning and exposing malicious Android & iOS applications to protect user data.
                </p>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span style="background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px;">✔️ VIES Verified EU</span>
                    <span style="background: rgba(56, 189, 248, 0.12); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px;">🛡️ 100% Free Public Utility</span>
                </div>
            </div>
            <div>
                <h4 style="font-family: 'Outfit', sans-serif; font-size: 1rem; font-weight: 700; color: #38bdf8; margin: 0 0 14px 0;">VasileDev Group Ecosystem</h4>
                <p style="margin: 0 0 8px 0; color: #cbd5e1; font-size: 0.85rem;">VAT / P.IVA: <code style="background: rgba(255, 255, 255, 0.1); color: #38bdf8; padding: 2px 6px; border-radius: 4px; font-family: monospace;">IT04226190041</code></p>
                <p style="margin: 0 0 8px 0; color: #94a3b8; font-size: 0.85rem;">Locations: Garessio (CN), Italy &amp; Odobești, Romania</p>
                <p style="margin: 0; color: #94a3b8; font-size: 0.85rem;">Direct: <a href="mailto:amendamax@vasiledev.com" style="color: #cbd5e1; text-decoration: none;">amendamax@vasiledev.com</a></p>
            </div>
            <div>
                <h4 style="font-family: 'Outfit', sans-serif; font-size: 1rem; font-weight: 700; color: #38bdf8; margin: 0 0 14px 0;">Official Network</h4>
                <p style="margin: 0 0 8px 0;"><a href="https://isbrokersafe.com" target="_blank" rel="noopener" style="color: #cbd5e1; font-weight: 400; text-decoration: none;">⚖️ IsBrokerSafe.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://jobscamradar.com" target="_blank" rel="noopener" style="color: #cbd5e1; font-weight: 400; text-decoration: none;">🛡️ JobScamRadar.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://pillscamradar.com" target="_blank" rel="noopener" style="color: #cbd5e1; font-weight: 400; text-decoration: none;">💊 PillScamRadar.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://verifydating.net" target="_blank" rel="noopener" style="color: #cbd5e1; font-weight: 400; text-decoration: none;">🛡️ VerifyDating.net</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://appscamradar.com" target="_blank" rel="noopener" style="color: #38bdf8; font-weight: 700; text-decoration: none;">👾 AppScamRadar.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://dreamcarhunt.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">🏎️ DreamCarHunt.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://airparkrefund.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">✈️ AirParkRefund.com</a></p>
                <p style="margin: 0;"><a href="https://vasiledev.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">👨‍💻 VasileDev.com</a></p>
            </div>
        </div>
        <div style="max-width: 1140px; margin: 0 auto; border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 20px; text-align: center; font-size: 0.8rem; color: #64748b;">
            <p style="margin: 0;">&copy; 2026 AppScamRadar™ by VasileDev Group. All rights reserved. Powered globally by Cloudflare Edge Network.</p>
        </div>
    </footer>

</body>

    </html>

    '''

    return html







@app.on_event("startup")

async def start_harvester():

    asyncio.create_task(daily_harvester())



@app.get("/directory/apps/{page}", response_class=HTMLResponse)
async def get_seo_directory(page: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM malicious_apps")
    total = c.fetchone()[0]
    total_pages = (total // 50) + (1 if total % 50 > 0 else 0)
    
    if page < 1: page = 1
    if page > total_pages and total_pages > 0: page = total_pages
    
    offset = (page - 1) * 50
    c.execute("SELECT slug, app_name, package_id, platform, threat_type, risk_level, status, added_date FROM malicious_apps ORDER BY id DESC LIMIT 50 OFFSET ?", (offset,))
    rows = c.fetchall()
    conn.close()
    
    items_html = ""
    for r in rows:
        color = "#ef4444" if r[5] == "Critical" else "#fbbf24"
        items_html += f"""
        <div style="background: rgba(11, 18, 30, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; margin-bottom: 15px; cursor: pointer; transition: all 0.3s ease;" onclick="window.location.href='/report/{r[0]}'" onmouseover="this.style.background='rgba(17, 27, 43, 0.6)'; this.style.borderColor='rgba(239, 68, 68, 0.3)';" onmouseout="this.style.background='rgba(11, 18, 30, 0.4)'; this.style.borderColor='rgba(255,255,255,0.05)';">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                <div>
                    <div style="font-size: 18px; font-weight: 700; color: white;">{r[1]}</div>
                    <div style="font-size: 13px; color: #94a3b8;">{r[2]}</div>
                </div>
                <div style="color: {color}; font-weight: 700;">{r[5]}</div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 14px; color: #cbd5e1;">
                <div>{r[3]}</div>
                <span style="background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; font-size: 12px;">{r[4]}</span>
            </div>
        </div>"""
        
    prev_link = f'<a href="/directory/apps/{page-1}" style="color: #3b82f6; text-decoration: none; padding: 10px 20px; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 6px; margin-right: 20px;">&larr; Previous</a>' if page > 1 else ''
    next_link = f'<a href="/directory/apps/{page+1}" style="color: #3b82f6; text-decoration: none; padding: 10px 20px; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 6px;">Next &rarr;</a>' if page < total_pages else ''
        
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Malicious App Directory - Page {page}</title>
        <style>
            body {{ font-family: system-ui, -apple-system, sans-serif; background-color: #03060a; background-image: linear-gradient(to bottom, rgba(3, 6, 10, 0.6), rgba(3, 6, 10, 0.8)), url('/static/bg.jpg'); background-attachment: fixed; background-size: cover; color: #f8fafc; margin: 0; padding: 0; }}
            header {{ background-color: rgba(11, 18, 30, 0.8); backdrop-filter: blur(12px); padding: 20px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.05); }}
            header h1 {{ margin: 0; font-size: 24px; color: #f8fafc; }}
            header a {{ color: inherit; text-decoration: none; }}
            .container {{ max-width: 800px; margin: 40px auto; padding: 0 20px; }}
            .pagination {{ display: flex; justify-content: center; margin-top: 40px; margin-bottom: 60px; }}
        </style>
    </head>
    <body>
        <header>
            <a href="/"><h1>AppScamRadar</h1></a>
        </header>
        <div class="container">
            <h2 style="margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">Scam App Directory - Page {page}</h2>
            {items_html}
            <div class="pagination">
                {prev_link}
                {next_link}
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
