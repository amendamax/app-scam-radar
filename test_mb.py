import requests

url = "https://mb-api.abuse.ch/api/v1/"
data = {'query': 'get_taginfo', 'tag': 'apk', 'limit': 100}
headers = {'Auth-Key': '7eaa21edbe53473a6989b6d989fcc99de41363183847c1c0'}
try:
    r = requests.post(url, data=data, headers=headers, verify=False)
    data = r.json()
    print("Status:", data.get('query_status'))
    if data.get('data'):
        print(f"Found {len(data['data'])} APKs.")
        print(data['data'][0].get('signature'), data['data'][0].get('file_name'))
except Exception as e:
    print(e)
