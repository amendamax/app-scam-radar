import re

# 1. UPDATE index.html
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

google_tag = '<meta name="google-site-verification" content="_UoEuIcslAcPkg7YgpdYmWhmlpWW0M3t97xdHm27z38" />'

if "google-site-verification" not in html:
    html = html.replace("<head>", f"<head>\n    {google_tag}")
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

# 2. UPDATE server.py
with open("server.py", "r", encoding="utf-8") as f:
    server = f.read()

if "google-site-verification" not in server:
    server = server.replace("<head>", f"<head>\n        {google_tag}")
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(server)

print("Google Tag Injected!")
