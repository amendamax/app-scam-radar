import re

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

scheduler_code = """
import asyncio
import os
import subprocess

async def daily_harvester():
    while True:
        try:
            print("Running daily MalwareBazaar harvester...")
            subprocess.run(["python", "harvester.py"], check=False)
        except Exception as e:
            print(f"Harvester error: {e}")
        # Run every 24 hours
        await asyncio.sleep(86400)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(daily_harvester())
"""

if "daily_harvester" not in code:
    code = code.replace('from fastapi.responses import HTMLResponse, JSONResponse', 'from fastapi.responses import HTMLResponse, JSONResponse\n' + scheduler_code)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(code)
print("Scheduler added!")
