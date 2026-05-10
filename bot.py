import requests
import time
import os
from datetime import datetime

# ================== CONFIG ==================
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
CIK = "0001181412"          # SpaceX
COMPANY_NAME = "SpaceX"
CHECK_INTERVAL = 45         # seconds
# ===========================================

last_seen = None

headers = {
    "User-Agent": "SpaceX Bot (your.email@example.com)"   # SEC requires this
}

def send_discord_alert(filing):
    form = filing.get('form', 'Unknown')
    filed_date = filing.get('filingDate', 'Unknown')
    accession = filing.get('accessionNumber', '')
    
    link = f"https://www.sec.gov/Archives/edgar/data/{CIK.lstrip('0')}/{accession.replace('-','')}/{filing.get('primaryDocument', 'index.htm')}"
    
    embed = {
        "title": f"🚨 SpaceX Filing Detected!",
        "description": f"**{COMPANY_NAME}** just filed a **{form}**",
        "url": link,
        "color": 0x00ff00,
        "timestamp": datetime.utcnow().isoformat(),
        "fields": [
            {"name": "Form", "value": form, "inline": True},
            {"name": "Filed At", "value": filed_date, "inline": True},
            {"name": "Accession", "value": accession, "inline": False}
        ]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})
        print(f"✅ Alert sent for {form}")
    except Exception as e:
        print("Failed to send Discord alert:", e)

def check_filings():
    global last_seen
    url = f"https://data.sec.gov/submissions/CIK{CIK}.json"
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        recent = data.get('filings', {}).get('recent', {})
        if not recent:
            print("No recent filings data")
            return
            
        # Check the newest filings
        for i in range(min(5, len(recent.get('accessionNumber', [])))):
            acc_no = recent['accessionNumber'][i]
            
            if last_seen is None:
                last_seen = acc_no
                print("Initialized last_seen")
                return
                
            if acc_no == last_seen:
                break
                
            # New filing found
            filing = {
                'accessionNumber': acc_no,
                'filingDate': recent['filingDate'][i],
                'form': recent['form'][i],
                'primaryDocument': recent['primaryDocument'][i]
            }
            
            print(f"🆕 New filing detected: {filing['form']} - {filing['filingDate']}")
            send_discord_alert(filing)
            
            # Update to the newest one
            last_seen = recent['accessionNumber'][0]
            break
            
    except Exception as e:
        print(f"Error checking filings: {e}")

# ================== MAIN LOOP ==================
print("🚀 Free SpaceX Polling Bot Started - Checking every 45 seconds")
print("Monitoring for new filings (including S-1)")

while True:
    check_filings()
    time.sleep(CHECK_INTERVAL)
