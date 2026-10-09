import urllib.request
import json

url = "https://api.koodous.com/apks?search=detected:true"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        if result.get('results'):
            print(f"Found {len(result['results'])} entries in first page.")
            print(json.dumps(result['results'][0]['app'], indent=2))
except Exception as e:
    print(f"Error: {e}")
