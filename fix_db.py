import re

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("get_db_connection()", "sqlite3.connect(DB_PATH)")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(code)
