import re

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

injection = """
    conn.commit()
    
    # Check if empty, then seed
    c.execute("SELECT COUNT(*) FROM malicious_apps")
    if c.fetchone()[0] == 0:
        import seed_db
        seed_db.seed_demo_malware()
    
    conn.close()
"""

code = code.replace("    conn.commit()\n    conn.close()", injection)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(code)
