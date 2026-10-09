import requests

url = "https://mb-api.abuse.ch/api/v1/"
data = {'query': 'get_recent', 'selector': 'time'}
try:
    r = requests.post(url, data=data, verify=False)
    print(r.status_code)
    print(r.text[:200])
except Exception as e:
    print(e)
