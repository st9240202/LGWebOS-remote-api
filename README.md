# LG WebOS Remote API

Control LG WebOS TVs over HTTP: power on/off (Wake-on-LAN / WebOS), launch apps, get status, and send remote button presses.

## Features

- **Power on**: Wake-on-LAN or WebOS API
- **Power off**: Standby via WebOS
- **Status**: Volume, mute, current app, system info
- **Launch apps**: e.g. Netflix, YouTube
- **Remote buttons**: Up/Down/Left/Right, Enter, Back, Menu, Mute, Volume, Home
- **Swagger UI**: Interactive API docs at `/docs`

## Requirements

- Python 3.x
- TV and host on the same network (or reachable via TV IP)
- WebOS features require a one-time pairing on the TV (see Setup below)

## Installation

```bash
pip install -r requirements.txt
```

## Setup

1. Copy the env example and edit:

   ```bash
   cp .env.example .env
   ```

2. Set your TV IP, MAC (for Wake-on-LAN), and optional `STORE_PATH` in `.env`:

   | Variable | Description |
   |----------|-------------|
   | `TV_IP` | TV IP or hostname |
   | `TV_MAC` | TV MAC address (for Wake-on-LAN) |
   | `STORE_PATH` | WebOS auth store path (default `store.json`) |
   | `DEFAULT_WAIT` | Default wait time (seconds) |
   | `DEFAULT_WAIT_POWER` | Wait after power on/off (seconds) |
   | `DEFAULT_APP` | Default app to launch (e.g. `netflix`) |

3. **First-time WebOS**: Call `POST /setup` or open `/docs`, then accept the prompt on the TV. Credentials are saved to `store.json` for power, apps, and remote APIs.

## Run

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

- API: <http://localhost:8000>
- Docs: <http://localhost:8000/docs>

## Docker

The repo includes a `Dockerfile` and `docker-compose.yml`. See [DOCKER_GUIDE.md](DOCKER_GUIDE.md).

## API Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | `/power` | Power on via Wake-on-LAN |
| POST | `/power/webos` | Power on via WebOS API |
| POST | `/poweroff` | Power off (standby) via WebOS |
| POST | `/status` | Get TV status |
| POST | `/currentapp` | Get current app |
| POST | `/apps` | List available apps |
| POST | `/launch` | Launch an app |
| POST | `/home` | Go to home screen |
| POST | `/remote/button` | Send a button by name |
| POST | `/remote/up`, `/remote/down`, ... | Direction, Enter, Back, Mute, Volume, Home |
| POST | `/setup` | First-time WebOS pairing guide |
| GET | `/health` | Health check |

Request parameters and defaults: see Swagger at <http://localhost:8000/docs>.

## License

For learning and personal use. Use of LG WebOS features is subject to LG’s terms.
