import re

with open("harvester.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("'limit': 1000", "'limit': 250")

with open("harvester.py", "w", encoding="utf-8") as f:
    f.write(code)
