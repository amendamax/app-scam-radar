import re

with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("rgba(3, 6, 10, 0.9), rgba(3, 6, 10, 0.97)", "rgba(3, 6, 10, 0.6), rgba(3, 6, 10, 0.8)")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)
