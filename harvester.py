import requests
import sqlite3
import datetime
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DB_PATH = "app_scams.db"
API_KEY = "7eaa21edbe53473a6989b6d989fcc99de41363183847c1c0"

def run_harvester():
    print("Starting MalwareBazaar Harvester...")
    
    url = "https://mb-api.abuse.ch/api/v1/"
    data = {'query': 'get_taginfo', 'tag': 'apk', 'limit': 1000}
    headers = {'Auth-Key': API_KEY}
    
    try:
        r = requests.post(url, data=data, headers=headers, verify=False)
        result = r.json()
        
        if result.get('query_status') != 'ok':
            print(f"API Error: {result.get('query_status')}")
            return
            
        payloads = result.get('data', [])
        print(f"Found {len(payloads)} APKs. Injecting into DB...")
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        inserted = 0
        for p in payloads:
            signature = p.get('signature') or "Unknown Malware"
            if signature.lower() == "unknown": signature = "Android Trojan"
                
            file_name = p.get('file_name', '')
            sha256 = p.get('sha256_hash', '')
            first_seen = p.get('first_seen', '')[:10]
            
            # Clean up app name
            app_name = file_name.replace('.apk', '')
            if len(app_name) > 30:
                app_name = f"{signature} Threat"
            else:
                app_name = app_name.capitalize()
                
            package_id = f"sha256:{sha256[:15]}..."
            threat_type = signature
            
            slug = f"{signature}-{sha256[:8]}".lower()
            slug = re.sub(r'[^a-z0-9-]', '-', slug)
            
            desc = f"Malicious APK identified as {signature}. Originally distributed as {file_name}. Tracked by Abuse.ch."
            
            try:
                c.execute('''
                    INSERT INTO malicious_apps 
                    (slug, app_name, package_id, platform, threat_type, risk_level, status, description, added_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (slug, app_name, package_id, "Android", threat_type, "Critical", "Active", desc, first_seen))
                inserted += 1
            except sqlite3.IntegrityError:
                pass
                
        conn.commit()
        conn.close()
        print(f"Harvester finished! Inserted {inserted} real malware records.")
        
    except Exception as e:
        print(f"Harvester failed: {e}")

if __name__ == "__main__":
    run_harvester()
