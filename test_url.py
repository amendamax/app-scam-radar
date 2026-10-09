import urllib.request
try:
    r = urllib.request.urlopen('https://app-scam-radar.onrender.com/sitemap.xml')
    print("WITH HYPHENS:", r.getcode())
except Exception as e:
    print("WITH HYPHENS ERROR:", e)

try:
    r = urllib.request.urlopen('https://appscamradar.onrender.com/sitemap.xml')
    print("WITHOUT HYPHENS:", r.getcode())
except Exception as e:
    print("WITHOUT HYPHENS ERROR:", e)
