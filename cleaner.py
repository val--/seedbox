import requests
import time
import os

RADARR_URL = "http://localhost:7878"
API_KEY = "b57....changewithradarrapikey"
CHECK_INTERVAL = 300 # 5 minutes

def check_and_clean():
    try:
        # Récupération de la file d'attente (Queue)
        response = requests.get(f"{RADARR_URL}/api/v3/queue?apikey={API_KEY}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        records = data.get('records', [])
        print(f"🔍 Scan de la file : {len(records)} film(s) en cours.")
        
        for item in records:
            title = item.get('title')
            item_id = item.get('id')
            status = str(item.get('status', '')).lower()
            tracked_status = str(item.get('trackedDownloadStatus', '')).lower()
                        print(f"➡️ Analysé : {title} | Status: {status} | Tracked: {tracked_status}")
            
            # CONDITION DE SUPPRESSION :
            # Si le mot 'warning' ou 'stalled' apparaît dans l'un des deux champs
            if 'warning' in status or 'stalled' in status or 'warning' in tracked_status or 'stalled' in tracked_status:
                print(f"⚠️ BLOCAGE DÉTECTÉ pour : {title}")
                
                # Suppression : removeFromClient=true (vire de qBit) & blocklist=true (cherche un autre)
                del_url = f"{RADARR_URL}/api/v3/queue/{item_id}?apikey={API_KEY}&removeFromClient=true&blocklist=true"
                r = requests.delete(del_url, timeout=10)
                
                if r.status_code == 200:
                    print(f"✅ Succès : {title} supprimé et blacklisté.")
                else:
                    print(f"❌ Erreur lors de la suppression (Code: {r.status_code})")
                    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion à Radarr : {e}")
    except Exception as e:
        print(f"❌ Une erreur imprévue est survenue : {e}")

if __name__ == "__main__":
    print("🚀 Nettoyeur Radarr V3 (Anti-Stalled) démarré...")
    # Premier check immédiat au démarrage
    check_and_clean()
    
    while True:
        print(f"😴 Prochain scan dans {CHECK_INTERVAL//60} minutes...")
        time.sleep(CHECK_INTERVAL)
        check_and_clean()
