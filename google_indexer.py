import json
import sqlite3
import requests
import time
import glob
from google.oauth2 import service_account
import google.auth.transport.requests

BASE_URL = "https://appscamradar.com/report/"
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPES = ["https://www.googleapis.com/auth/indexing"]

def get_access_token(key_file):
    creds = service_account.Credentials.from_service_account_file(key_file, scopes=SCOPES)
    request = google.auth.transport.requests.Request()
    creds.refresh(request)
    return creds.token

def get_urls_from_db(limit):
    conn = sqlite3.connect("app_scams.db")
    cursor = conn.cursor()
    cursor.execute("SELECT slug FROM malicious_apps WHERE is_indexed = 0 LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    urls = []
    for row in rows:
        urls.append(BASE_URL + row[0])
    return urls

def mark_url_as_indexed(url):
    slug = url.replace(BASE_URL, "")
    conn = sqlite3.connect("app_scams.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE malicious_apps SET is_indexed = 1 WHERE slug = ?", (slug,))
    conn.commit()
    conn.close()

def main():
    service_accounts = glob.glob("../pill-scam-radar/*.json")
    if not service_accounts:
        print("No service account keys found in ../pill-scam-radar/")
        return
        
    print(f"Found {len(service_accounts)} service accounts. Ready to index.")
    
    # 200 quota per service account
    limit = len(service_accounts) * 200 
    
    urls = get_urls_from_db(limit)
    if not urls:
        print("No new URLs to index.")
        return
        
    print(f"Loaded {len(urls)} URLs to submit.")
    
    submitted = 0
    sa_idx = 0
    token = get_access_token(service_accounts[sa_idx])
    
    for i, url in enumerate(urls):
        if i > 0 and i % 200 == 0:
            sa_idx += 1
            if sa_idx >= len(service_accounts):
                print("All service accounts reached their 200 quota limit.")
                break
            print(f"Switching to next service account: {service_accounts[sa_idx]}")
            token = get_access_token(service_accounts[sa_idx])
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        body = {
            "url": url,
            "type": "URL_UPDATED"
        }
        
        resp = requests.post(ENDPOINT, headers=headers, json=body)
        
        if resp.status_code == 200:
            print(f"[OK] {url}")
            mark_url_as_indexed(url)
            submitted += 1
        elif resp.status_code == 429:
            print(f"[429] Quota Exceeded on {service_accounts[sa_idx]}. Switching accounts early...")
            sa_idx += 1
            if sa_idx >= len(service_accounts):
                print("No more service accounts available.")
                break
            token = get_access_token(service_accounts[sa_idx])
            
            # retry once
            headers["Authorization"] = f"Bearer {token}"
            resp = requests.post(ENDPOINT, headers=headers, json=body)
            if resp.status_code == 200:
                print(f"[OK - RETRY] {url}")
                mark_url_as_indexed(url)
                submitted += 1
        else:
            print(f"[ERROR {resp.status_code}] {url} -> {resp.text}")
            
        time.sleep(1)
        
    print(f"Successfully submitted {submitted} URLs for indexing.")

if __name__ == '__main__':
    main()
