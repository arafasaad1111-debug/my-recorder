import os
import time
import requests

# Your bot credentials
BOT_TOKEN = "8992382338:AAFVgtp5cSnEqHh7pHMyvGYh0FYbRTs831I"
CHAT_ID = "973785378"

# Put your 9 group links here inside the quotes
TARGET_URLS = [
     "https://stripchat.com/Doodqueen",
    "https://stripchat.com/Lillylolo",
    "https://stripchat.com/Yasmin_Oh",
    "https://ar.stripchat.com/sexy-mariya",
    "https://ar.stripchat.com/Lubnna",
    "https://ar.stripchat.com/Notila-68",
    "https://ar.stripchat.com/Capitana-arab",
    "https://stripchat.com/Zouzou_sexy",
    "https://stripchat.com/Miss_dou3ae",
]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error: {e}")

def check_live_status(url):
    try:
        response = requests.get(url)
        if "live" in response.text.lower():
            return True
        return False
    except Exception as e:
        print(f"Connection error for {url}: {e}")
        return False

send_telegram_message("🤖 Bot is now running and monitoring 9 groups...")

while True:
    for url in TARGET_URLS:
        if "LINK_" in url:
            continue
            
        if check_live_status(url):
            group_name = url.split("/")[-1] if "/" in url else "group"
            send_telegram_message(f"🔴 Live started in ({group_name})! Starting recording...")
            os.system(f"streamlink {url} best -o recorded_{group_name}.mp4")
            send_telegram_message(f"✅ Recording finished for {group_name} and saved!")
            
    print("Checked all groups. Waiting 5 minutes for next check...")
    time.sleep(300)
      
