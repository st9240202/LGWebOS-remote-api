# LG Remote API - Docker Guide

## Prerequisites
- OrbStack or Docker Desktop installed
- Your TV's IP address and MAC address

## Quick Start

### 1. Configuration
Copy `.env.example` to `.env` and update with your TV settings:

```bash
cp .env.example .env
```

Edit `.env`:
```
TV_IP=your-tv-ip-or-hostname
TV_MAC=xx-xx-xx-xx-xx-xx
STORE_PATH=store.json
```

### 2. Run in OrbStack (Docker Hub image, no build)

If you use **OrbStack** and want to run the pre-built image from Docker Hub:

```bash
# Ensure store.json exists (create empty if first time)
touch store.json

# Load .env and run (OrbStack uses Docker Compose)
docker compose -f docker-compose.hub.yml up -d
```

- API: **http://localhost:8000**
- Docs: **http://localhost:8000/docs**
- Image used: `st9240202/lgwebos-remote-api:latest`

To stop:
```bash
docker compose -f docker-compose.hub.yml down
```

### 3. Build and Run with Docker Compose (local build)

```bash
docker-compose up -d --build
```

The API will be available at `http://localhost:8000`

Access Swagger UI at: `http://localhost:8000/docs`

### 4. Or Build and Run Manually

**Build the image:**
```bash
docker build -t lg-remote-api:latest .
```

**Run the container:**
```bash
docker run -d \
  --name lg-remote-api \
  -p 8000:8000 \
  -e TV_IP=your-tv-ip \
  -e TV_MAC=your-tv-mac \
  -v $(pwd)/store.json:/app/store.json \
  lg-remote-api:latest
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TV_IP` | 192.168.1.100 | TV IP address or hostname |
| `TV_MAC` | xx-xx-xx-xx-xx-xx | TV MAC address for WOL |
| `STORE_PATH` | store.json | Path to WebOS auth store |
| `DEFAULT_WAIT` | 0 | Default wait time (seconds) |
| `DEFAULT_WAIT_POWER` | 5 | Wait time for power ops (seconds) |
| `DEFAULT_VERIFY` | false | Verify TV after power on |
| `DEFAULT_APP` | netflix | Default app to launch |

## Helpful Commands

**View logs:**
```bash
docker-compose logs -f lg-remote-api
```

**Stop the container:**
```bash
docker-compose down
```

**Rebuild after code changes:**
```bash
docker-compose up -d --build
```

**Test the API:**
```bash
curl http://localhost:8000/health
```

## Notes

- The `store.json` file is mounted as a volume to persist WebOS authentication between container restarts
- On first connection to TV, authorization may be required (accept on TV screen)
- For best results, use your TV's IP address instead of hostname
- Make sure your Mac and TV are on the same network
- **OrbStack**: Use `docker compose -f docker-compose.hub.yml up -d` to run the image from Docker Hub (`st9240202/lgwebos-remote-api`) without building locally
