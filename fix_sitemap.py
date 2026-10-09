import re

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

# Fix sitemap to use dynamic URL
code = code.replace('def sitemap():', 'def sitemap(request: Request):')
code = code.replace('https://app-scam-radar.onrender.com/', '{request.base_url}')
code = code.replace('https://app-scam-radar.onrender.com/report/', '{request.base_url}report/')

with open("server.py", "w", encoding="utf-8") as f:
    f.write(code)
