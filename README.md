# Seedbox Stack

Docker Compose stack for a self-hosted seedbox behind a VPN, featuring automated media management (Radarr/Sonarr) and cross-drive library support.

## Services

| Service | Description | Web UI |
|---|---|---|
| **Gluetun** | VPN client (WireGuard) — the gateway for all torrent traffic | - |
| **qBittorrent** | Torrent client (runs inside Gluetun's network) | `:8080` |
| **Prowlarr** | Indexer manager (syncs C411, etc., to Radarr/Sonarr) | `:9696` |
| **FlareSolverr** | Cloudflare bypass proxy for Prowlarr | `:8191` |
| **Radarr** | Movie collection manager | `:7878` |
| **Sonarr** | TV Series collection manager | `:8989` |
| **Radarr Cleaner** | Python script to auto-remove stalled/warning downloads | - |

---

## Setup

### 1. Configure environment

```sh
cp .env.example .env
```

Edit `.env` with these essential values:

| Variable | How to find it |
|---|---|
| `WIREGUARD_PRIVATE_KEY` | `grep "PrivateKey" wg0.conf` (from your VPN provider) |
| `PUID` / `PGID` | Run `id` in your terminal (usually `1000`) |
| `APPS_DATA_PATH` | Path for configs (e.g. `/home/john/seedbox`) |
| `STORAGE_PATH` | Your drive for active seeding (e.g. `/mnt/stockage`) |
| `NAS_PATH` | Path where your old NAS is mounted (e.g. `/mnt/nas`) |
| `RADARR_API_KEY` | Radarr > Settings > General |

### 2. Permissions & directories

```sh
# Ensure the stack can write to your storage
sudo chown -R $USER:$USER /mnt/stockage
mkdir -p $APPS_DATA_PATH/{qbittorrent,prowlarr,radarr,sonarr}/config
```

### 3. Start the stack

```sh
docker compose up -d
```

---

## Critical connections

- **qBittorrent in Radarr/Sonarr**: Use host `172.17.0.1` (Docker bridge) and port `8080`.
- **Indexer sync**: In Prowlarr, add Radarr/Sonarr apps via their API keys to sync trackers automatically.
- **VPN binding**: In qBittorrent > Options > Advanced:
  - **Network Interface**: Set to `tun0` (critical for kill switch).
  - **Optional IP**: Set to the `172.x.x.x` address.

---

## Storage & hardlinks

Both qBittorrent and Radarr/Sonarr mount `STORAGE_PATH` at `/data`. This allows hardlinks (instant move, zero extra space).

Recommended directory structure:

```
/data/
  ├── Downloads_Temp/   # Active torrents (keep in qBittorrent)
  └── Videos/
      ├── Films/        # Radarr library
      └── Series/       # Sonarr library
```

> **Note:** To manage your old NAS files, add `NAS_PATH` as a second Root Folder in Radarr/Sonarr settings. Hardlinks won't work between `/data` and `/nas`, but management will.

---

## Maintenance & security

### Verify VPN leak

```sh
# Must return your VPN's IP, not your ISP's
docker exec qbittorrent curl https://ifconfig.me
```

### Verify hardlink (same inode)

```sh
# If the first numbers match, it's a hardlink!
ls -i "/data/Downloads_Temp/Movie.mkv" "/data/Videos/Films/Movie (2025)/Movie.mkv"
```

### Script logs (cleaner)

```sh
# Check why a torrent was removed
docker logs radarr-cleaner
```

---

## Pro tips

- **Original titles**: In Radarr > Settings > Media Management, check *Use Movie Origin Title* to keep French titles.
- **Import existing**: Use *Library Import* in Radarr/Sonarr to scan your NAS without moving files. Set them to *Unmonitored* if you don't want the apps to upgrade them automatically.
