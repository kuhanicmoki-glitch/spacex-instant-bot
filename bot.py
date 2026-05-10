import asyncio
import websockets
import json
import requests
import os
from datetime import datetime

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
API_KEY = os.getenv("SEC_API_KEY")
TARGET_CIK = "0001181412"
TARGET_FORM = "S-1"

def send_discord_alert(filing):
    company = filing.get("companyName", "SpaceX")
    form = filing.get("formType", "Unknown")
    filed_at = filing.get("filedAt", datetime.utcnow().isoformat())
    accession = filing.get("accessionNo", "")
    cik = filing.get("cik", TARGET_CIK)

    link = f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{accession.replace('-','')}/{filing.get('primaryDocument', 'index.htm')}"

    embed = {
        "title": f"🚨 INSTANT SpaceX S-1 ALERT!",
        "description": f"**{company}** just filed a {form}",
        "url": link,
        "color": 0x00ff00,
        "timestamp": datetime.utcnow().isoformat(),
        "fields": [
            {"name": "Form", "value": form, "inline": True},
            {"name": "Filed At", "value": filed_at[:19] + " UTC", "inline": True},
            {"name": "Accession", "value": accession, "inline": False}
        ]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})
    except:
        pass

async def connect_with_retry():
    while True:
        try:
            url = f"wss://stream.sec-api.io?apiKey={API_KEY}"
            print("🔌 Connecting to real-time SEC stream...")
            
            async with websockets.connect(url, ping_interval=25, ping_timeout=30) as ws:
                print("✅ Connected! Watching for SpaceX S-1 filings (instant)")
                
                async for message in ws:
                    try:
                        data = json.loads(message)
                        if data.get("cik") == TARGET_CIK and data.get("formType") == TARGET_FORM:
                            print("🎯 SPACE X S-1 DETECTED!")
                            send_discord_alert(data)
                    except:
                        pass
                        
        except Exception as e:
            print(f"⚠️ Connection lost: {type(e).__name__} - {e}")
            print("🔄 Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(connect_with_retry())
