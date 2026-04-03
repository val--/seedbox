import requests
import time
import os

RADARR_URL = os.environ["RADARR_URL"]
API_KEY = os.environ["RADARR_API_KEY"]
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "300"))

def check_and_clean():
    try:
        # Fetch the download queue
        response = requests.get(f"{RADARR_URL}/api/v3/queue?apikey={API_KEY}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        records = data.get('records', [])
        print(f"🔍 Queue scan: {len(records)} movie(s) in progress.")
        
        for item in records:
            title = item.get('title')
            item_id = item.get('id')
            
            # Get statuses and lowercase them for comparison
            status = str(item.get('status', '')).lower()
            tracked_status = str(item.get('trackedDownloadStatus', '')).lower()
            print(f"➡️ Checked: {title} | Status: {status} | Tracked: {tracked_status}")
            
            if 'warning' in status or 'stalled' in status or 'warning' in tracked_status or 'stalled' in tracked_status:
                print(f"⚠️ STALL DETECTED: {title}")
                
                # Remove from qBittorrent and blocklist so Radarr searches for another release
                del_url = f"{RADARR_URL}/api/v3/queue/{item_id}?apikey={API_KEY}&removeFromClient=true&blocklist=true"
                r = requests.delete(del_url, timeout=10)
                
                if r.status_code == 200:
                    print(f"✅ Success: {title} removed and blocklisted.")
                else:
                    print(f"❌ Deletion failed (Code: {r.status_code})")
                    
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error to Radarr: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🚀 Radarr Cleaner V3 (Anti-Stalled) started...")
    # Run immediately on startup
    check_and_clean()
    
    while True:
        print(f"😴 Next scan in {CHECK_INTERVAL//60} minutes...")
        time.sleep(CHECK_INTERVAL)
        check_and_clean()
