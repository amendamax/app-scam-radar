import re

with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# Make table rows transparent
code = code.replace("background: var(--bg-secondary);", "background: rgba(11, 18, 30, 0.6); backdrop-filter: blur(8px);")

# Also the search box
code = code.replace("background: rgba(11, 18, 30, 0.6);", "background: rgba(11, 18, 30, 0.4); backdrop-filter: blur(12px);")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)
