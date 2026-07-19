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
    "https://www.tango.me/hanm2",
    "https://www.tango.me/albrnsyst-53",
    "https://sprlv.link/u/oGDQ8ECgIAA",
    "https://superlive.chat/ar/profile/44367210",
    "https://sprlv.link/u/EJAAwLDAIAA",
    "https://www.tango.me/mlk23",
    "https://sprlv.link/u/0KAgMNBQEAA",
    
]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending message: {e}")

def send_telegram_video(file_path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    try:
        if not os.path.exists(file_path):
            print(f"File not found for sending: {file_path}")
            return False
            
        with open(file_path, 'rb') as video_file:
            files = {'video': video_file}
            data = {'chat_id': CHAT_ID, 'caption': caption}
            response = requests.post(url, data=data, files=files, timeout=120)
            return response.status_code == 200
    except Exception as e:
        print(f"Error sending video: {e}")
        return False

def split_and_send_video(file_path, group_name):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        send_telegram_message(f"Error: Video file for {group_name} is empty or missing.")
        return

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    if file_size_mb <= 48:
        send_telegram_message(f"Uploading video for {group_name} ({file_size_mb:.1f}MB) to Telegram...")
        success = send_telegram_video(file_path, f"Live video for {group_name} full version")
        if success:
            send_telegram_message(f"Successfully uploaded full video for {group_name}!")
        else:
            send_telegram_message(f"Failed to upload video for {group_name} via Telegram API.")
        return

    send_telegram_message(f"Video size is large ({file_size_mb:.1f}MB). Splitting into parts...")
    
    duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
    try:
        duration = float(os.popen(duration_cmd).read().strip())
    except Exception as e:
        print(f"FFprobe error: {e}")
        duration = 0
        
    if duration == 0:
        send_telegram_message("Error: Could not calculate video duration. Sending file as is might fail.")
        return

    chunk_size_mb = 45
    num_chunks = math.ceil(file_size_mb / chunk_size_mb)
    chunk_duration = duration / num_chunks

    base_dir = os.path.dirname(os.path.abspath(file_path))

    for i in range(num_chunks):
        start_time = i * chunk_duration
        output_part = os.path.join(base_dir, f"part_{i+1}_{os.path.basename(file_path)}")
        
        split_cmd = f'ffmpeg -y -ss {start_time} -i "{file_path}" -t {chunk_duration} -c copy "{output_part}"'
        os.system(split_cmd)
        
        if os.path.exists(output_part) and os.path.getsize(output_part) > 0:
            part_size = os.path.getsize(output_part) / (1024 * 1024)
            caption = f"Live {group_name} - Part {i+1} of {num_chunks} ({part_size:.1f}MB)"
            send_telegram_message(f"Sending part {i+1} of {num_chunks}...")
            
            send_telegram_video(output_part, caption)
            
            try:
                os.remove(output_part)
            except:
                pass
            time.sleep(3)
        else:
            send_telegram_message(f"Error creating part {i+1} of {num_chunks}")

def check_live_status(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        response = requests.get(url, headers=headers, timeout=15)
        html_content = response.text.lower()
        if "live" in html_content or '"islive":true' in html_content or 'is_live' in html_content:
            return True
        return False
    except Exception as e:
        print(f"Connection error for {url}: {e}")
        return False

send_telegram_message("Bot is now running and monitoring 9 groups with auto-split & max-duration feature...")

while True:
    try:
        try:
    current_files = os.listdir('.')
    files_text = "\n".join([f"File: {f} ({os.path.getsize(f)/(1024*1024):.1f}MB)" for f in current_files if f.endswith('.mp4')])
    if not files_text:
        files_text = "No recorded video files found in directory right now."
    send_telegram_message(f"--- Current Directory Report ---\n{files_text}")
except Exception as e:
    print(f"Error checking directory: {e}")

for url in TARGET_URLS:
    if "LINK_" in url:
        continue
        
    group_name = url.split("/")[-1] if "/" in url else "group"
    
    if check_live_status(url):
        send_telegram_message(f"Live started in {group_name}! Recording 20 mins slice via Streamlink...")
        
        output_filename = f"recorded_{group_name}.mp4"
        
        os.system(f'streamlink "{url}" best -o "{output_filename}" --max-duration 20m')
        
        send_telegram_message(f"Recording finished/sliced for {group_name}! Checking file...")
        
        if os.path.exists(output_filename) and os.path.getsize(output_filename) > 1024*1024:
            split_and_send_video(output_filename, group_name)
            try:
                os.remove(output_filename)
            except:
                pass
        else:
            send_telegram_message(f"Failed: No valid video file created for {group_name}. Live might be protected or too short.")
    
    time.sleep(2)
        
print("Checked all groups. Job finished.")
send_telegram_message("All groups checked. Current cycle finished.")
