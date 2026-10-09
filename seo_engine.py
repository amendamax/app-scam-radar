import re

# 1. UPDATE index.html
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Make the table rows clickable
html = html.replace('<tr class="table-row">', '<tr class="table-row" onclick="window.location.href=\'/report/${item.slug}\'" style="cursor: pointer;">')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

# 2. UPDATE server.py
with open("server.py", "r", encoding="utf-8") as f:
    server = f.read()

seo_routes = """
@app.get("/sitemap.xml", response_class=HTMLResponse)
def sitemap():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT slug FROM malicious_apps ORDER BY id DESC")
    rows = c.fetchall()
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\\n'
    
    # Base URL
    xml += '<url>\\n'
    xml += '  <loc>https://app-scam-radar.onrender.com/</loc>\\n'
    xml += '  <changefreq>daily</changefreq>\\n'
    xml += '  <priority>1.0</priority>\\n'
    xml += '</url>\\n'
    
    for row in rows:
        xml += '<url>\\n'
        xml += f'  <loc>https://app-scam-radar.onrender.com/report/{row[0]}</loc>\\n'
        xml += '  <changefreq>monthly</changefreq>\\n'
        xml += '  <priority>0.8</priority>\\n'
        xml += '</url>\\n'
        
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

"""

if "def sitemap" not in server:
    server = server.replace("@app.on_event", seo_routes + "\n\n@app.on_event")
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(server)

print("SEO Engine injected!")
