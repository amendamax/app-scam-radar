import os
import requests
import sqlite3
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DB_PATH = "/var/data/app_scams.db" if os.path.exists("/var/data/app_scams.db") else "app_scams.db"
API_KEY = "7eaa21edbe53473a6989b6d989fcc99de41363183847c1c0"


def run_harvester():
    print("Starting MalwareBazaar Harvester...")
    url = "https://mb-api.abuse.ch/api/v1/"
    data = {'query': 'get_taginfo', 'tag': 'apk', 'limit': 250}
    headers = {'Auth-Key': API_KEY}

    try:
        r = requests.post(url, data=data, headers=headers, verify=False, timeout=25)
        result = r.json()

        if result.get('query_status') != 'ok':
            print(f"API Error: {result.get('query_status')}")
            return

        payloads = result.get('data', [])
        print(f"Found {len(payloads)} APKs. Injecting into DB ({DB_PATH})...")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        inserted = 0
        for p in payloads:
            signature = p.get('signature') or "Android Banking Trojan / Dropper"
            if signature.lower() == "unknown":
                signature = "Android Banking Trojan / Dropper"

            file_name = p.get('file_name', '')
            sha256 = p.get('sha256_hash', '')
            first_seen = (p.get('first_seen', '') or '')[:10]
            hash_short = sha256[:6].upper()

            raw_name = file_name.replace('.apk', '').strip("._- ")
            if (
                not raw_name
                or len(raw_name) > 28
                or re.fullmatch(r"[0-9a-fA-F]{12,}", raw_name)
                or any(ord(ch) > 127 for ch in raw_name)
                or raw_name.lower() in ("app", "release", "v6", "payload", "base_temp", "wrapper")
            ):
                family_label = signature.split("/")[0].strip()
                app_name = f"{family_label} APK [{hash_short}]"
            else:
                app_name = raw_name.capitalize()

            package_id = f"sha256:{sha256[:15]}..."
            threat_type = signature

            slug = f"{signature}-{sha256[:8]}".lower()
            slug = re.sub(r'[^a-z0-9-]', '-', slug)
            slug = re.sub(r'-+', '-', slug).strip('-')

            desc = f"Malicious APK identified as {signature}. Originally distributed as {file_name}. Tracked by Abuse.ch MalwareBazaar."

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
