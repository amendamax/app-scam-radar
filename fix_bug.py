import re

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

fixed_get_apps = """
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
"""

code = re.sub(r'# API for frontend.*?return {"total": total, "results": results}', fixed_get_apps, code, flags=re.DOTALL)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(code)
