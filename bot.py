import requests
import time
import os
from datetime import datetime

# ================== CONFIG ==================
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
CIK = "0001181412"
COMPANY_NAME = "SpaceX"
CHECK_INTERVAL = 45
# ===========================================

last_seen = None
headers = {"User-Agent": "SpaceX Bot (your.email@example.com)"}

def send_discord_alert(filing, is_test=False):
    form = filing.get('form', 'Unknown')
    filed_date = filing.get('filingDate', 'Unknown')
    accession = filing.get('accessionNumber', '')
    
    link = f"https://www.sec.gov/Archives/edgar/data/{CIK.lstrip('0')}/{accession.replace('-','')}/{filing.get('primaryDocument', 'index.htm')}"
    
    title = "🧪 TEST ALERT - Bot is Working!" if is_test else "🚨 SpaceX Filing Detected!"
    
    embed = {
        "title": title,
        "description": f"**{COMPANY_NAME}** just filed a **{form}**",
        "url": link,
        "color": 0x00ff00 if not is_test else 0xFFFF00,
        "timestamp": datetime.utcnow().isoformat(),
        "fields": [
            {"name": "Form", "value": form, "inline": True},
            {"name": "Filed At", "value": filed_date, "inline": True},
            {"name": "Accession", "value": accession, "inline": False}
        ]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})
        print(f"✅ {'Test' if is_test else 'Real'} alert sent for {form}")
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
            return
            
        for i in range(min(5, len(recent.get('accessionNumber', [])))):
            acc_no = recent['accessionNumber'][i]
            
            if last_seen is None:
                last_seen = acc_no
                return
                
            if acc_no == last_seen:
                break
                
            filing = {
                'accessionNumber': acc_no,
                'filingDate': recent['filingDate'][i],
                'form': recent['form'][i],
                'primaryDocument': recent['primaryDocument'][i]
            }
            
            print(f"🆕 New filing: {filing['form']}")
            send_discord_alert(filing)
            last_seen = recent['accessionNumber'][0]
            break
            
    except Exception as e:
        print(f"Error checking filings: {e}")

# ================== MAIN ==================
print("🚀 Free SpaceX Polling Bot Started")
print("Type 'TEST' in the next redeploy to trigger a test alert")

# Send test alert on startup (you control it by redeploying)
send_discord_alert({
    'form': 'TEST-S1',
    'filingDate': datetime.utcnow().strftime('%Y-%m-%d'),
    'accessionNumber': 'TEST-FILING-123456789',
    'primaryDocument': 'index.htm'
}, is_test=True)

print("Monitoring for real filings every 45 seconds...")

while True:
    check_filings()
    time.sleep(CHECK_INTERVAL)
