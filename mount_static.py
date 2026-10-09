import re

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

if "StaticFiles" not in code:
    code = code.replace("from fastapi.responses", "from fastapi.staticfiles import StaticFiles\nfrom fastapi.responses")

if "app.mount" not in code:
    code = code.replace("DB_PATH = \"app_scams.db\"", "DB_PATH = \"app_scams.db\"\napp.mount(\"/static\", StaticFiles(directory=\"static\"), name=\"static\")")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(code)
