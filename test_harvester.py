import requests

API_KEY = "7eaa21edbe53473a6989b6d989fcc99de41363183847c1c0"
url = "https://mb-api.abuse.ch/api/v1/"
data = {'query': 'get_taginfo', 'tag': 'apk', 'limit': 1000}
headers = {'Auth-Key': API_KEY}
r = requests.post(url, data=data, headers=headers, verify=False)
print(r.status_code)
print(r.text[:500])
