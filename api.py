from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import asyncio
import os


from lg_remote import send_magic_packet_unicast, try_connect_pywebostv, try_poweroff_pywebostv, try_launch_app_pywebostv, try_go_home_pywebostv, get_tv_status_pywebostv, get_current_app_pywebostv, list_available_apps_pywebostv, try_remote_button_pywebostv, try_poweron_webos_api, setup_webos_api

# ========== Default Configuration ==========
# Modify these values to set defaults, used when POST body doesn't specify parameters
# Or use environment variables to override (recommended for Docker)
DEFAULT_IP = os.getenv("TV_IP", "q1router.tplinkdns.com")
DEFAULT_STORE = os.getenv("STORE_PATH", "store.json")
DEFAULT_MAC = os.getenv("TV_MAC", "F0-86-20-48-2D-46")
DEFAULT_WAIT = int(os.getenv("DEFAULT_WAIT", "0"))                    # Wait time (seconds)
DEFAULT_WAIT_POWER = int(os.getenv("DEFAULT_WAIT_POWER", "5"))        # Wait time for power endpoints
DEFAULT_VERIFY = os.getenv("DEFAULT_VERIFY", "false").lower() == "true"  # Whether to verify connection
DEFAULT_APP = os.getenv("DEFAULT_APP", "netflix")                     # Default application
# ==========================================

app = FastAPI(
    title="LG Remote API",
    description="Wake-on-LAN and optional WebOS verification (Swagger UI available at /docs)",
    version="0.1",
)

class TVStatusRequest(BaseModel):
    ip: str = DEFAULT_IP
    store: Optional[str] = DEFAULT_STORE
    wait: int = DEFAULT_WAIT


@app.post("/status", summary="Get TV status (volume, mute, input, etc.)")
async def get_status(req: TVStatusRequest):
    """Get TV status (volume, mute, input source, power, etc.)"""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(get_tv_status_pywebostv, req.ip, Path(req.store) if req.store else None, req.wait),
    )
    return result


class CurrentAppRequest(BaseModel):
    ip: str = DEFAULT_IP
    store: Optional[str] = DEFAULT_STORE
    wait: int = DEFAULT_WAIT


@app.post("/currentapp", summary="Get current running app on TV")
async def get_current_app(req: CurrentAppRequest):
    """Get currently running application on TV"""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(get_current_app_pywebostv, req.ip, Path(req.store) if req.store else None, req.wait),
    )
    return result


class ListAppsRequest(BaseModel):
    ip: str = DEFAULT_IP
    store: Optional[str] = DEFAULT_STORE
    wait: int = DEFAULT_WAIT


@app.post("/apps", summary="List available apps on TV")
async def list_apps(req: ListAppsRequest):
    """List available applications on TV"""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(list_available_apps_pywebostv, req.ip, Path(req.store) if req.store else None, req.wait),
    )
    return result


class PowerRequest(BaseModel):
    mac: str = DEFAULT_MAC
    ip: Optional[str] = DEFAULT_IP
    wait: int = DEFAULT_WAIT_POWER
    store: Optional[str] = DEFAULT_STORE
    verify: bool = DEFAULT_VERIFY


class PowerOffRequest(BaseModel):
    ip: str = DEFAULT_IP
    store: Optional[str] = DEFAULT_STORE
    wait: int = DEFAULT_WAIT


class LaunchRequest(BaseModel):
    ip: str = DEFAULT_IP
    store: Optional[str] = DEFAULT_STORE
    app: str = DEFAULT_APP
    wait: int = DEFAULT_WAIT


class HomeRequest(BaseModel):
    ip: str = DEFAULT_IP
    store: Optional[str] = DEFAULT_STORE
    wait: int = DEFAULT_WAIT


class RemoteButtonRequest(BaseModel):
    ip: str = DEFAULT_IP
    store: Optional[str] = DEFAULT_STORE
    button: Optional[str] = None  # Optional for convenience, but set by specific endpoints
    wait: int = DEFAULT_WAIT


class RemoteRequest(BaseModel):
    ip: str = DEFAULT_IP
    store: Optional[str] = DEFAULT_STORE
    wait: int = DEFAULT_WAIT


@app.post("/power", summary="Power on TV via Wake-on-LAN (Unicast)")
async def power(req: PowerRequest):
    """Send Wake-on-LAN magic packet via unicast to target IP (not broadcast).
    
    Sends the magic packet directly to the specified IP address instead of 
    broadcasting to 255.255.255.255. More reliable when broadcast is restricted.
    """
    if not req.ip:
        return {"ok": False, "error": "IP address is required for unicast WOL"}
    
    try:
        send_magic_packet_unicast(req.mac, req.ip)
    except Exception as e:
        return {"ok": False, "error": f"Failed to send magic packet: {e}"}

    result = {"ok": True, "message": f"Magic packet sent to {req.ip}"}

    if req.verify:
        loop = asyncio.get_running_loop()
        from functools import partial
        ok = await loop.run_in_executor(
            None,
            partial(try_connect_pywebostv, req.ip, Path(req.store) if req.store else None, req.wait),
        )
        result["verified"] = bool(ok)

    return result


@app.post("/power/webos", summary="Power on TV via WebOS API")
async def power_webos(req: PowerRequest):
    """Power on TV using WebOS API via pywebostv.
    
    Requires the TV to be reachable by IP and pywebostv to be installed.
    """
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_poweron_webos_api, req.ip, Path(req.store) if req.store else None, req.wait),
    )
    if isinstance(result, dict):
        return result
    return {"ok": bool(result)}


@app.get("/health", summary="Health check")
async def health():
    return {"status": "ok"}


class SetupRequest(BaseModel):
    ip: str = DEFAULT_IP
    store: Optional[str] = DEFAULT_STORE
    timeout: int = 30  # Setup may take longer when waiting for user approval on TV


@app.post("/setup", summary="First-time setup: webOS API key guide and registration")
async def setup_webos(req: SetupRequest):
    """Guide and registration for obtaining webOS API key on first use.
    
    This endpoint provides the full setup flow:
    1. Check dependencies and existing configuration
    2. Connect to the TV
    3. Guide you through the authorization flow
    4. Save credentials to the store file
    
    Steps:
    1. Ensure the TV is on and on the same network
    2. Call this endpoint with the TV's IP address
    3. If the TV shows an authorization prompt, choose Allow/OK on the TV
    4. Call this endpoint again to complete setup
    
    Returns detailed status and next-step instructions.
    """
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(setup_webos_api, req.ip, Path(req.store) if req.store else None, req.timeout),
    )
    return result


@app.post("/poweroff", summary="Power off TV via WebOS (turn screen off / standby)")
async def poweroff(req: PowerOffRequest):
    """Attempt to turn the TV to standby / switch screen off using pywebostv.

    Requires `pywebostv` to be installed and the TV to be reachable by IP.
    """
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_poweroff_pywebostv, req.ip, Path(req.store) if req.store else None, req.wait),
    )
    # try_poweroff_pywebostv returns dict with `ok` and `details`
    if isinstance(result, dict):
        return result
    return {"ok": bool(result)}


@app.post("/launch", summary="Launch an app on the TV (e.g. Netflix)")
async def launch_app(req: LaunchRequest):
    """Launch an application on the TV using pywebostv."""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_launch_app_pywebostv, req.ip, Path(req.store) if req.store else None, req.app, req.wait),
    )
    # result is a dict with `ok` and `details`
    if isinstance(result, dict):
        return result
    return {"ok": bool(result)}


@app.post("/home", summary="Return TV to home screen")
async def go_home(req: HomeRequest):
    """Return the TV to the home screen using pywebostv.

    Requires `pywebostv` to be installed and the TV to be reachable by IP.
    """
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_go_home_pywebostv, req.ip, Path(req.store) if req.store else None, req.wait),
    )
    # result is a dict with `ok` and `details`
    if isinstance(result, dict):
        return result
    return {"ok": bool(result)}


# Remote Control Endpoints
@app.post("/remote/button", summary="Send a remote button press to TV")
async def send_remote_button(req: RemoteButtonRequest):
    """Send any remote control button press to the TV.
    
    Supported buttons: up, down, left, right, enter, back, home, menu, mute, 
    volumeup, volumedown, channelup, channeldown
    """
    if not req.button:
        return {"ok": False, "details": "button field is required"}
    
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_remote_button_pywebostv, req.ip, Path(req.store) if req.store else None, req.button, req.wait),
    )
    if isinstance(result, dict):
        return result
    return {"ok": bool(result)}


@app.post("/remote/up", summary="Remote control: Up button")
async def remote_up(req: RemoteRequest):
    """Send UP button press to TV"""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_remote_button_pywebostv, req.ip, Path(req.store) if req.store else None, "up", req.wait),
    )
    return result if isinstance(result, dict) else {"ok": bool(result)}


@app.post("/remote/down", summary="Remote control: Down button")
async def remote_down(req: RemoteRequest):
    """Send DOWN button press to TV"""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_remote_button_pywebostv, req.ip, Path(req.store) if req.store else None, "down", req.wait),
    )
    return result if isinstance(result, dict) else {"ok": bool(result)}


@app.post("/remote/left", summary="Remote control: Left button")
async def remote_left(req: RemoteRequest):
    """Send LEFT button press to TV"""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_remote_button_pywebostv, req.ip, Path(req.store) if req.store else None, "left", req.wait),
    )
    return result if isinstance(result, dict) else {"ok": bool(result)}


@app.post("/remote/right", summary="Remote control: Right button")
async def remote_right(req: RemoteRequest):
    """Send RIGHT button press to TV"""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_remote_button_pywebostv, req.ip, Path(req.store) if req.store else None, "right", req.wait),
    )
    return result if isinstance(result, dict) else {"ok": bool(result)}


@app.post("/remote/enter", summary="Remote control: Enter/OK button")
async def remote_enter(req: RemoteRequest):
    """Send ENTER/OK button press to TV"""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_remote_button_pywebostv, req.ip, Path(req.store) if req.store else None, "enter", req.wait),
    )
    return result if isinstance(result, dict) else {"ok": bool(result)}


@app.post("/remote/back", summary="Remote control: Back/Return button")
async def remote_back(req: RemoteRequest):
    """Send BACK/RETURN button press to TV"""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_remote_button_pywebostv, req.ip, Path(req.store) if req.store else None, "back", req.wait),
    )
    return result if isinstance(result, dict) else {"ok": bool(result)}


@app.post("/remote/menu", summary="Remote control: Menu button")
async def remote_menu(req: RemoteRequest):
    """Send MENU button press to TV"""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_remote_button_pywebostv, req.ip, Path(req.store) if req.store else None, "menu", req.wait),
    )
    return result if isinstance(result, dict) else {"ok": bool(result)}


@app.post("/remote/mute", summary="Remote control: Mute button")
async def remote_mute(req: RemoteRequest):
    """Send MUTE button press to TV"""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_remote_button_pywebostv, req.ip, Path(req.store) if req.store else None, "mute", req.wait),
    )
    return result if isinstance(result, dict) else {"ok": bool(result)}


@app.post("/remote/volumeup", summary="Remote control: Volume Up button")
async def remote_volumeup(req: RemoteRequest):
    """Send VOLUME UP button press to TV"""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_remote_button_pywebostv, req.ip, Path(req.store) if req.store else None, "volumeup", req.wait),
    )
    return result if isinstance(result, dict) else {"ok": bool(result)}


@app.post("/remote/volumedown", summary="Remote control: Volume Down button")
async def remote_volumedown(req: RemoteRequest):
    """Send VOLUME DOWN button press to TV"""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_remote_button_pywebostv, req.ip, Path(req.store) if req.store else None, "volumedown", req.wait),
    )
    return result if isinstance(result, dict) else {"ok": bool(result)}


@app.post("/remote/home", summary="Remote control: Home button")
async def remote_home(req: RemoteRequest):
    """Send HOME button press to TV"""
    from functools import partial
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(try_remote_button_pywebostv, req.ip, Path(req.store) if req.store else None, "home", req.wait),
    )
    return result if isinstance(result, dict) else {"ok": bool(result)}


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI app so `python api.py` starts the server (useful for Run & Debug)
    uvicorn.run(app, host="0.0.0.0", port=8000)
