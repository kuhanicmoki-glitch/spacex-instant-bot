import asyncio
import websockets
import json
import requests
import os
from datetime import datetime

# Get secrets from Railway environment variables
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
API_KEY = os.getenv("SEC_API_KEY")
TARGET_CIK = "0001181412"        # SpaceX
TARGET_FORM = "S-1"              # Change to "*" if you want ALL filings

def send_discord_alert(filing):
    company = filing.get("companyName", "SpaceX")
    form = filing.get("formType", "Unknown")
    filed_at = filing.get("filedAt", datetime.utcnow().isoformat())
    accession = filing.get("accessionNo", "")
    cik = filing.get("cik", TARGET_CIK)

    link = f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{accession.replace('-','')}/{filing.get('primaryDocument', 'index.htm')}"

    embed = {
        "title": f"🚨 INSTANT S-1 ALERT — SpaceX Filed!",
        "description": f"**{company}** just filed a {form}",
        "url": link,
        "color": 0x00ff00,
        "timestamp": datetime.utcnow().isoformat(),
        "fields": [
            {"name": "Form", "value": form, "inline": True},
            {"name": "Filed At", "value": filed_at[:19] + " UTC", "inline": True},
            {"name": "Accession #", "value": accession, "inline": False}
        ]
    }
    payload = {"embeds": [embed]}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

async def main():
    url = f"wss://stream.sec-api.io?apiKey={API_KEY}"
    print("🔌 Connecting to real-time SEC stream...")

    async with websockets.connect(url) as ws:
        print("✅ Connected! Now watching for SpaceX S-1 filings (instant detection)")
        async for message in ws:
            try:
                data = json.loads(message)
                if data.get("cik") == TARGET_CIK and data.get("formType") == TARGET_FORM:
                    print(f"🎯 SPACE X S-1 DETECTED!")
                    send_discord_alert(data)
            except:
                pass  # ignore any weird messages

if __name__ == "__main__":
    asyncio.run(main())
