import requests
import time
import os

CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "300"))

SERVICES = []

if os.environ.get("RADARR_URL") and os.environ.get("RADARR_API_KEY"):
    SERVICES.append({
        "name": "Radarr",
        "url": os.environ["RADARR_URL"],
        "api_key": os.environ["RADARR_API_KEY"],
        "label": "movie(s)",
    })

if os.environ.get("SONARR_URL") and os.environ.get("SONARR_API_KEY"):
    SERVICES.append({
        "name": "Sonarr",
        "url": os.environ["SONARR_URL"],
        "api_key": os.environ["SONARR_API_KEY"],
        "label": "episode(s)",
    })

def check_and_clean(service):
    name = service["name"]
    base_url = service["url"]
    api_key = service["api_key"]
    label = service["label"]

    try:
        response = requests.get(f"{base_url}/api/v3/queue?apikey={api_key}", timeout=10)
        response.raise_for_status()
        data = response.json()

        records = data.get('records', [])
        print(f"[{name}] Queue scan: {len(records)} {label} in progress.")

        for item in records:
            title = item.get('title')
            item_id = item.get('id')

            status = str(item.get('status', '')).lower()
            tracked_status = str(item.get('trackedDownloadStatus', '')).lower()
            print(f"[{name}] Checked: {title} | Status: {status} | Tracked: {tracked_status}")

            if 'warning' in status or 'stalled' in status or 'warning' in tracked_status or 'stalled' in tracked_status:
                print(f"[{name}] STALL DETECTED: {title}")

                del_url = f"{base_url}/api/v3/queue/{item_id}?apikey={api_key}&removeFromClient=true&blocklist=true"
                r = requests.delete(del_url, timeout=10)

                if r.status_code == 200:
                    print(f"[{name}] Success: {title} removed and blocklisted.")
                else:
                    print(f"[{name}] Deletion failed (Code: {r.status_code})")

    except requests.exceptions.RequestException as e:
        print(f"[{name}] Connection error: {e}")
    except Exception as e:
        print(f"[{name}] Unexpected error: {e}")

if __name__ == "__main__":
    if not SERVICES:
        print("No services configured. Set RADARR_URL/RADARR_API_KEY and/or SONARR_URL/SONARR_API_KEY.")
        exit(1)

    service_names = ", ".join(s["name"] for s in SERVICES)
    print(f"Arr Cleaner (Anti-Stalled) started for: {service_names}")

    for service in SERVICES:
        check_and_clean(service)

    while True:
        print(f"Next scan in {CHECK_INTERVAL // 60} minutes...")
        time.sleep(CHECK_INTERVAL)
        for service in SERVICES:
            check_and_clean(service)
