import urllib.request
import urllib.parse
import json

url = "https://urlhaus-api.abuse.ch/v1/payloads/recent/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"Status: {result.get('query_status')}")
        if result.get('payloads'):
            print(f"Total payloads: {len(result['payloads'])}")
            apks = [p for p in result['payloads'] if p.get('file_type') == 'apk']
            print(f"Found {len(apks)} APK payloads.")
except Exception as e:
    print(f"Error: {e}")
