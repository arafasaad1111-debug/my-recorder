import os
import time
import requests
import math

BOT_TOKEN = "8992382338:AAFVgtp5cSnEqHh7pHMyvGYh0FYbRTs831I"
CHAT_ID = "973785378"

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

def send_telegram_video(file_path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    try:
        with open(file_path, 'rb') as video_file:
            files = {'video': video_file}
            data = {'chat_id': CHAT_ID, 'caption': caption}
            response = requests.post(url, data=data, files=files)
            return response.status_code == 200
    except Exception as e:
        print(f"Error sending video: {e}")
        return False

def split_and_send_video(file_path, group_name):
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    if file_size_mb <= 48:
        send_telegram_message(f"Uploading video for {group_name} to Telegram...")
        send_telegram_video(file_path, f"Live video for {group_name} full version")
        return

    send_telegram_message(f"Video size is large ({file_size_mb:.1f}MB). Splitting into parts and sending...")
    
    duration_cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {file_path}"
    try:
        duration = float(os.popen(duration_cmd).read().strip())
    except:
        duration = 0
        
    if duration == 0:
        send_telegram_message("Error: Could not calculate video duration for splitting.")
        return

    chunk_size_mb = 45
    num_chunks = math.ceil(file_size_mb / chunk_size_mb)
    chunk_duration = duration / num_chunks

    for i in range(num_chunks):
        start_time = i * chunk_duration
        output_part = f"part_{i+1}_{file_path}"
        
        split_cmd = f'ffmpeg -y -ss {start_time} -i "{file_path}" -t {chunk_duration} -c copy "{output_part}"'
        os.system(split_cmd)
        
        if os.path.exists(output_part):
            part_size = os.path.getsize(output_part) / (1024 * 1024)
            caption = f"Live {group_name} - Part {i+1} of {num_chunks} ({part_size:.1f}MB)"
            send_telegram_message(f"Sending part {i+1} of {num_chunks}...")
            send_telegram_video(output_part, caption)
            
            try:
                os.remove(output_part)
            except:
                pass
            time.sleep(2)

def check_live_status(url):
    try:
        response = requests.get(url)
        if "live" in response.text.lower():
            return True
        return False
    except Exception as e:
        print(f"Connection error for {url}: {e}")
        return False

send_telegram_message("Bot is now running and monitoring 9 groups with auto-split feature...")

while True:
    for url in TARGET_URLS:
        if "LINK_" in url:
            continue
            
        if check_live_status(url):
            group_name = url.split("/")[-1] if "/" in url else "group"
            send_telegram_message(f"Live started in {group_name}! Recording...")
            
            output_filename = f"recorded_{group_name}.mp4"
            os.system(f"streamlink {url} best -o {output_filename}")
            
            send_telegram_message(f"Recording finished for {group_name}!")
            
            if os.path.exists(output_filename):
                split_and_send_video(output_filename, group_name)
                try:
                    os.remove(output_filename)
                except:
                    pass
            
    print("Checked all groups. Waiting 5 minutes for next check...")
    time.sleep(300)
  
