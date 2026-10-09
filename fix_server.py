import re

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

# Remove the incorrectly placed block
bad_block = """
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

code = code.replace(bad_block, "")

# Append it at the VERY END of the file where app is definitely defined
good_block = """
import asyncio
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
async def start_harvester():
    asyncio.create_task(daily_harvester())
"""

code += good_block

with open("server.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Fixed!")
