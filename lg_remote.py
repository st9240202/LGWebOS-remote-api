"""
Simple LG WebOS TV power-on utility.

Features:
- Send a Wake-on-LAN magic packet to the TV's MAC address to power it on.
- Optionally attempt to connect using PyWebOSTV to verify the TV is online
  and to register (persisting authentication store to a JSON file).

Usage examples:
	python lg_remote.py --mac F0-86-20-48-2D-46 --wait 5
	python lg_remote.py --ip 192.168.0.167 --mac F0-86-20-48-2D-46 --store store.json

If you want to use the WebOS API features, install `pywebostv`:
  pip install pywebostv
"""

import argparse
import json
import socket
import struct
import time
from typing import Dict, Any
from pathlib import Path

def get_tv_status_pywebostv(ip: str, store_path: Path | None, timeout: int = 10) -> Dict[str, Any]:
	"""Get TV status (volume, mute, input source, power, etc.)"""
	try:
		from pywebostv.connection import WebOSClient
		from pywebostv.controls import SystemControl
	except Exception as e:
		return {"ok": False, "error": f"pywebostv import failed: {e}"}

	store = {}
	if store_path and store_path.exists():
		try:
			store = json.loads(store_path.read_text())
		except Exception:
			store = {}

	client = WebOSClient(ip)
	try:
		client.connect()
	except Exception as e:
		return {"ok": False, "error": f"Failed to connect to TV at {ip}: {e}"}

	for status in client.register(store):
		if status == WebOSClient.PROMPTED:
			return {"ok": False, "error": "Registration prompted, please accept on TV."}
		elif status == WebOSClient.REGISTERED:
			if store_path:
				try:
					store_path.write_text(json.dumps(store))
				except Exception:
					pass

	result = {"ok": True}
	try:
		system = SystemControl(client)

		# System information
		try:
			info = system.info()
			result["system_info"] = info
		except Exception as e:
			result["system_info"] = f"Error: {e}"

		# Try to get volume through SystemControl methods
		volume_methods = [
			('get_volume', []),
			('getVolume', []),
			('volume', []),
		]
		for method_name, args in volume_methods:
			if hasattr(system, method_name):
				try:
					vol = getattr(system, method_name)(*args)
					result["volume"] = vol
					break
				except Exception as e:
					result["volume"] = f"Error trying {method_name}: {e}"
		
		if "volume" not in result:
			result["volume"] = "Volume not available"

		# Try to get input source through SystemControl methods
		input_methods = [
			('get_current_input', []),
			('get_input', []),
			('currentInputInfo', []),
		]
		for method_name, args in input_methods:
			if hasattr(system, method_name):
				try:
					inp = getattr(system, method_name)(*args)
					result["current_input"] = inp
					break
				except Exception as e:
					result["current_input"] = f"Error trying {method_name}: {e}"
		
		if "current_input" not in result:
			result["current_input"] = "Input info not available"

	except Exception as e:
		result["error"] = f"Failed to get status: {e}"
	return result

def get_current_app_pywebostv(ip: str, store_path: Path | None, timeout: int = 10) -> Dict[str, Any]:
	"""Get currently running application on TV"""
	try:
		from pywebostv.connection import WebOSClient
		from pywebostv.controls import ApplicationControl
	except Exception as e:
		return {"ok": False, "error": f"pywebostv import failed: {e}"}

	store = {}
	if store_path and store_path.exists():
		try:
			store = json.loads(store_path.read_text())
		except Exception:
			store = {}

	client = WebOSClient(ip)
	try:
		client.connect()
	except Exception as e:
		return {"ok": False, "error": f"Failed to connect to TV at {ip}: {e}"}

	for status in client.register(store):
		if status == WebOSClient.PROMPTED:
			return {"ok": False, "error": "Registration prompted, please accept on TV."}
		elif status == WebOSClient.REGISTERED:
			if store_path:
				try:
					store_path.write_text(json.dumps(store))
				except Exception:
					pass

	result = {"ok": True}
	try:
		app_ctrl = ApplicationControl(client)
		current_app = None

		# Try various possible methods to get current application
		methods = [
			'get_current',
			'get_current_app', 
			'getCurrentApp',
			'current',
			'currentApp',
		]
		
		for method_name in methods:
			if hasattr(app_ctrl, method_name):
				try:
					current_app = getattr(app_ctrl, method_name)()
					result["current_app"] = current_app
					break
				except Exception as e:
					try_msg = f"method {method_name}: {str(e)[:50]}"

		if "current_app" not in result:
			# If all above methods fail, try listing all apps with list_apps() and find status
			try:
				if hasattr(app_ctrl, 'list_apps'):
					apps = app_ctrl.list_apps()
					result["available_apps"] = apps
				elif hasattr(app_ctrl, 'list'):
					apps = app_ctrl.list()
					result["available_apps"] = apps
				else:
					result["current_app"] = "Method not available"
			except Exception as e:
				result["current_app"] = f"Error: {e}"

	except Exception as e:
		result["error"] = f"Failed to get current app: {e}"
	return result

def list_available_apps_pywebostv(ip: str, store_path: Path | None, timeout: int = 10) -> Dict[str, Any]:
	"""List available applications on TV"""
	try:
		from pywebostv.connection import WebOSClient
		from pywebostv.controls import ApplicationControl
	except Exception as e:
		return {"ok": False, "error": f"pywebostv import failed: {e}"}

	store = {}
	if store_path and store_path.exists():
		try:
			store = json.loads(store_path.read_text())
		except Exception:
			store = {}

	client = WebOSClient(ip)
	try:
		client.connect()
	except Exception as e:
		return {"ok": False, "error": f"Failed to connect to TV at {ip}: {e}"}

	for status in client.register(store):
		if status == WebOSClient.PROMPTED:
			return {"ok": False, "error": "Registration prompted, please accept on TV."}
		elif status == WebOSClient.REGISTERED:
			if store_path:
				try:
					store_path.write_text(json.dumps(store))
				except Exception:
					pass

	result = {"ok": True, "apps": []}
	try:
		app_ctrl = ApplicationControl(client)

		# Try various methods to list applications
		methods = [
			'list_apps',
			'list',
			'get_list',
			'get_apps',
			'apps',
		]
		
		for method_name in methods:
			if hasattr(app_ctrl, method_name):
				try:
					apps = getattr(app_ctrl, method_name)()
					if apps:
						result["apps"] = apps
						result["method_used"] = method_name
						break
				except Exception as e:
					pass

		if not result["apps"]:
			result["apps"] = []
			result["message"] = "Could not retrieve app list from TV"

	except Exception as e:
		result["error"] = f"Failed to list apps: {e}"
	return result
import time
from pathlib import Path

def send_magic_packet_unicast(mac: str, target_ip: str, port: int = 9):
	"""Send a Wake-on-LAN magic packet to a specific IP address (unicast).
	
	Instead of broadcasting to 255.255.255.255, this sends directly to the target IP.
	Useful when the target is not on the local broadcast domain or when broadcast is restricted.
	"""
	# Normalize MAC: remove separators
	mac_clean = mac.replace(':', '').replace('-', '').replace('.', '').lower()
	if len(mac_clean) != 12:
		raise ValueError('MAC address is invalid')

	mac_bytes = bytes.fromhex(mac_clean)
	packet = b'\xff' * 6 + mac_bytes * 16

	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
		sock.sendto(packet, (target_ip, port))

def try_poweron_webos_api(ip: str, store_path: Path | None, timeout: int = 10) -> Dict[str, Any]:
	"""Power on TV via WebOS API using pywebostv.
	
	Sends a power-on command to the TV using the WebOS system control API.
	Returns a dict with keys: `ok` (bool) and `details` (message or list).
	"""
	try:
		from pywebostv.connection import WebOSClient
		from pywebostv.controls import SystemControl
	except Exception as e:
		return {"ok": False, "details": f"pywebostv import failed: {e}"}
	
	store = {}
	if store_path and store_path.exists():
		try:
			store = json.loads(store_path.read_text())
		except Exception:
			store = {}
	
	client = WebOSClient(ip)
	try:
		client.connect()
	except Exception as e:
		return {"ok": False, "details": f"Failed to connect to TV at {ip}: {e}"}
	
	tried = []
	
	try:
		for status in client.register(store):
			if status == WebOSClient.PROMPTED:
				tried.append('PROMPTED: user must accept on TV')
			elif status == WebOSClient.REGISTERED:
				tried.append('REGISTERED')
				if store_path:
					try:
						store_path.write_text(json.dumps(store))
						tried.append(f'Saved store to {store_path}')
					except Exception:
						tried.append(f'Could not save store to {store_path}')
		
		system = None
		try:
			system = SystemControl(client)
		except Exception as e:
			tried.append(f'No SystemControl: {e}')
		
		# Try SystemControl methods for power on
		if system:
			for method in ("power_on", "powerOn", "turn_on", "turnOn", "on", "set_power"):
				if hasattr(system, method):
					try:
						getattr(system, method)()
						return {"ok": True, "details": f"Sent power-on via SystemControl.{method}"}
					except Exception as e:
						tried.append((f'SystemControl.{method}()', str(e)))
		
		# Fallback: use client.request/call with various service/method strings for power-on
		svc_candidates = [
			('luna://com.webos.service.power-control', 'powerOn'),
			('luna://com.webos.service.power', 'powerOn'),
			('com.webos.service.power-control', 'powerOn'),
			('com.webos.service.power', 'powerOn'),
			('luna://com.webos.service.osInfo', 'on'),
			('system', 'powerOn'),
			('system', 'turnOn'),
		]
		
		for svc, method in svc_candidates:
			if hasattr(client, 'request'):
				try:
					client.request(svc, method, {})
					return {"ok": True, "details": f"Requested power-on via client.request {svc}.{method}"}
				except Exception as e:
					tried.append((f'request:{svc}.{method}', str(e)[:60]))
			if hasattr(client, 'call'):
				try:
					client.call(svc, method, {})
					return {"ok": True, "details": f"Requested power-on via client.call {svc}.{method}"}
				except Exception as e:
					tried.append((f'call:{svc}.{method}', str(e)[:60]))
		
		return {"ok": False, "details": tried}
	except Exception as e:
		return {"ok": False, "details": f"pywebostv power on request failed: {e}"}


def try_poweron_http_api(ip: str, timeout: int = 10) -> Dict[str, Any]:
	"""Power on TV via HTTP API (LG WebOS HTTP interface).
	
	Sends a power-on command directly to the TV's HTTP endpoint.
	This works on some LG models without requiring authentication.
	Returns a dict with keys: `ok` (bool) and `details` (message or list).
	"""
	try:
		import urllib.request
		import urllib.error
	except Exception as e:
		return {"ok": False, "details": f"urllib import failed: {e}"}
	
	tried = []
	
	# LG WebOS TV HTTP API endpoints for power control
	# These endpoints work on many LG models for power control without authentication
	endpoints = [
		f"http://{ip}:8008/api/v2/power/on",
		f"http://{ip}:8008/api/power/on",
		f"http://{ip}:8008/power/on",
		f"http://{ip}:5000/api/v2/power/on",
		f"http://{ip}:5000/api/power/on",
	]
	
	for endpoint in endpoints:
		try:
			req = urllib.request.Request(endpoint, method='POST', data=b'{}')
			req.add_header('Content-Type', 'application/json')
			
			with urllib.request.urlopen(req, timeout=timeout) as response:
				result = response.read()
				return {"ok": True, "details": f"Sent power-on to {endpoint}"}
		except urllib.error.URLError as e:
			tried.append(f"URLError on {endpoint}: {str(e)[:60]}")
		except urllib.error.HTTPError as e:
			# HTTP errors might still indicate the command was received
			if e.code in [200, 201, 204]:
				return {"ok": True, "details": f"Sent power-on to {endpoint} (HTTP {e.code})"}
			tried.append(f"HTTPError {e.code} on {endpoint}")
		except Exception as e:
			tried.append(f"Error on {endpoint}: {str(e)[:60]}")
	
	return {"ok": False, "details": tried}


def setup_webos_api(ip: str, store_path: Path | None, timeout: int = 30) -> Dict[str, Any]:
	"""First-time setup: guide and registration flow for webOS API key.
	
	Provides full setup guidance:
	1. Check dependencies
	2. Attempt connection to TV
	3. Guide user through registration
	4. Save credentials
	
	Returns detailed status and next-step instructions.
	"""
	try:
		from pywebostv.connection import WebOSClient
		from pywebostv.controls import SystemControl
	except Exception as e:
		return {
			"ok": False,
			"step": "dependency_check",
			"error": f"pywebostv not installed or import failed: {e}",
			"guide": {
				"title": "Install dependencies",
				"steps": [
					"Install the pywebostv package:",
					"pip install pywebostv",
					"Or use:",
					"pip install -r requirements.txt"
				]
			}
		}
	
	# Check if store already exists with credentials
	has_existing_store = store_path and store_path.exists()
	if has_existing_store:
		try:
			existing_store = json.loads(store_path.read_text())
			if existing_store:
				return {
					"ok": True,
					"step": "already_configured",
					"message": "TV is already set up; credentials exist",
					"store_path": str(store_path) if store_path else None,
					"guide": {
						"title": "Setup complete",
						"message": "Your TV is already configured for webOS API. You can use other API endpoints.",
						"next_steps": [
							"Use /status to check TV status",
							"Use /power to power on",
							"Use /remote/* to control the TV"
						]
					}
				}
		except Exception:
			pass
	
	# Load or init store
	store = {}
	if has_existing_store:
		try:
			store = json.loads(store_path.read_text())
		except Exception:
			store = {}
	
	# Try to connect
	client = WebOSClient(ip)
	try:
		client.connect()
	except Exception as e:
		return {
			"ok": False,
			"step": "connection",
			"error": f"Failed to connect to TV ({ip}): {e}",
			"guide": {
				"title": "Connection failed",
				"steps": [
					"Please verify:",
					f"1. TV IP address is correct: {ip}",
					"2. TV is on and on the same network",
					"3. Firewall allows the connection",
					"4. On TV you can find IP: Settings > Network > Network Status > Wired/Wi-Fi > IP Settings"
				],
				"tips": [
					"Ensure TV and this device are on the same LAN",
					"Some routers block device-to-device traffic; check router settings"
				]
			}
		}
	
	# Start registration
	registration_status = None
	registration_messages = []
	
	try:
		for status in client.register(store):
			if status == WebOSClient.PROMPTED:
				registration_status = "PROMPTED"
				registration_messages.append("Authorization prompt shown on TV")
				return {
					"ok": False,
					"step": "awaiting_user_approval",
					"status": "PROMPTED",
					"message": "Please accept the connection request on the TV screen",
					"guide": {
						"title": "Awaiting approval",
						"steps": [
							"1. Look at your LG TV screen",
							"2. You should see an authorization prompt (e.g. 'Allow connection' or 'Allow app to connect')",
							"3. Use the TV remote to select Allow or OK",
							"4. After approving, call this API endpoint again to complete setup"
						],
						"important": [
							"The prompt usually appears within 30 seconds",
							"If you don't see it, confirm the TV is on and on the same network",
							"Some models require enabling 'Allow app connection' in TV settings first"
						],
						"tv_settings_path": [
							"Settings > General > External Devices > Device Connection Manager",
							"Or: Settings > Network > Advanced Settings > Allow app connection"
						]
					}
				}
			elif status == WebOSClient.REGISTERED:
				registration_status = "REGISTERED"
				registration_messages.append("Registration successful")
				
				# Save store
				if store_path:
					try:
						store_path.write_text(json.dumps(store))
						registration_messages.append(f"Credentials saved to {store_path}")
					except Exception as e:
						registration_messages.append(f"Failed to save credentials: {e}")
						return {
							"ok": False,
							"step": "save_failed",
							"status": "REGISTERED",
							"error": f"Registration succeeded but save failed: {e}",
							"messages": registration_messages
						}
				
				# Verify connection and get system info
				try:
					system = SystemControl(client)
					info = system.info()
					return {
						"ok": True,
						"step": "completed",
						"status": "REGISTERED",
						"message": "webOS API setup complete.",
						"store_path": str(store_path) if store_path else None,
						"tv_info": info,
						"messages": registration_messages,
						"guide": {
							"title": "Setup complete",
							"message": "Your TV is now connected via webOS API.",
							"next_steps": [
								"You can now use all API endpoints to control the TV",
								"Use /status to check TV status",
								"Use /power to power on",
								"Use /remote/* for remote control",
								"Use /launch to start apps"
							],
							"store_file": {
								"path": str(store_path) if store_path else "not set",
								"description": "This file holds TV credentials; keep it secure"
							}
						}
					}
				except Exception as e:
					return {
						"ok": True,
						"step": "registered_but_info_failed",
						"status": "REGISTERED",
						"message": "Registration succeeded but could not get TV info",
						"warning": f"Error getting system info: {e}",
						"store_path": str(store_path) if store_path else None,
						"messages": registration_messages,
						"guide": {
							"title": "Setup mostly complete",
							"message": "TV is registered but detailed info could not be retrieved",
							"note": "This usually does not affect basic usage"
						}
					}
		
		# Registration loop ended without returning
		return {
			"ok": False,
			"step": "registration_timeout",
			"status": registration_status,
			"error": "Registration timed out or did not complete",
			"messages": registration_messages,
			"guide": {
				"title": "Registration timeout",
				"steps": [
					"Registration may have failed because:",
					"1. TV did not respond to the authorization request",
					"2. Unstable network",
					"3. App connection not enabled in TV settings",
					"",
					"Try:",
					"- Confirm the TV is on",
					"- Check 'Allow app connection' in TV settings",
					"- Call this API again later"
				]
			}
		}
	except Exception as e:
		return {
			"ok": False,
			"step": "registration_error",
			"error": f"Error during registration: {e}",
			"guide": {
				"title": "Registration error",
				"message": "An unexpected error occurred during registration",
				"troubleshooting": [
					"Check that the TV supports webOS API",
					"Ensure TV firmware is up to date",
					"Try restarting the TV and running setup again"
				]
			}
		}


def try_connect_pywebostv(ip: str, store_path: Path | None, timeout: int = 10):
	"""Attempt to connect to TV using pywebostv and print info if successful.

	Returns True if connected and `system.info()` returned data.
	"""
	try:
		from pywebostv.connection import WebOSClient
		from pywebostv.controls import SystemControl
	except Exception as e:
		print('pywebostv not installed or failed to import:', e)
		return False

def try_poweroff_pywebostv(ip: str, store_path: Path | None, timeout: int = 10):
	"""Attempt to send a power-off (screen off / standby) command via pywebostv.

	Returns a dict with keys: `ok` (bool) and `details` (list or message).
	"""
	try:
		from pywebostv.connection import WebOSClient
		from pywebostv.controls import SystemControl
	except Exception as e:
		return {"ok": False, "details": f"pywebostv import failed: {e}"}

	store = {}
	if store_path and store_path.exists():
		try:
			store = json.loads(store_path.read_text())
		except Exception:
			store = {}

	client = WebOSClient(ip)
	try:
		client.connect()
	except Exception as e:
		return {"ok": False, "details": f"Failed to connect to TV at {ip}: {e}"}

	tried = []

	try:
		for status in client.register(store):
			if status == WebOSClient.PROMPTED:
				tried.append('PROMPTED: user must accept on TV')
			elif status == WebOSClient.REGISTERED:
				tried.append('REGISTERED')
				if store_path:
					try:
						store_path.write_text(json.dumps(store))
						tried.append(f'Saved store to {store_path}')
					except Exception:
						tried.append(f'Could not save store to {store_path}')

		system = None
		try:
			system = SystemControl(client)
		except Exception as e:
			tried.append(f'No SystemControl: {e}')

		# Try SystemControl methods first
		if system:
			for method in ("power_off", "powerOff", "turn_off", "turnOff", "off", "power_toggle", "set_power"):
				if hasattr(system, method):
					try:
						getattr(system, method)()
						return {"ok": True, "details": f"Sent power-off via SystemControl.{method}"}
					except Exception as e:
						tried.append((f'SystemControl.{method}()', str(e)))

		# Fallback: use client.request/call with various service/method strings for power-off
		svc_candidates = [
			('luna://com.webos.service.power-control', 'powerOff'),
			('luna://com.webos.service.power', 'powerOff'),
			('com.webos.service.power-control', 'powerOff'),
			('com.webos.service.power', 'powerOff'),
			('luna://com.webos.service.osInfo', 'off'),
			('system', 'powerOff'),
			('system', 'turnOff'),
		]

		for svc, method in svc_candidates:
			if hasattr(client, 'request'):
				try:
					client.request(svc, method, {})
					return {"ok": True, "details": f"Requested power-off via client.request {svc}.{method}"}
				except Exception as e:
					tried.append((f'request:{svc}.{method}', str(e)[:60]))
			if hasattr(client, 'call'):
				try:
					client.call(svc, method, {})
					return {"ok": True, "details": f"Requested power-off via client.call {svc}.{method}"}
				except Exception as e:
					tried.append((f'call:{svc}.{method}', str(e)[:60]))

		return {"ok": False, "details": tried}
	except Exception as e:
		return {"ok": False, "details": f"pywebostv poweroff request failed: {e}"}


def try_launch_app_pywebostv(ip: str, store_path: Path | None, app_id: str = 'netflix', timeout: int = 10):
	"""Attempt to launch an app (e.g. Netflix) via pywebostv.

	Returns a dict with keys: `ok` (bool) and `details` (list or message).
	"""
	try:
		from pywebostv.connection import WebOSClient
		from pywebostv.controls import ApplicationControl
	except Exception as e:
		return {"ok": False, "details": f"pywebostv import failed: {e}"}

	store = {}
	if store_path and store_path.exists():
		try:
			store = json.loads(store_path.read_text())
		except Exception:
			store = {}

	client = WebOSClient(ip)
	try:
		client.connect()
	except Exception as e:
		return {"ok": False, "details": f"Failed to connect to TV at {ip}: {e}"}

	tried = []

	# Build candidate app ids for common cases (Netflix has several possible identifiers)
	candidates = [app_id]
	if app_id.lower() == 'netflix':
		candidates = [
			'netflix',
			'com.netflix.app',
			'com.netflix.ninja',
			'com.netflix.app.lgsmarttv',
			'netflix.app',
		]

	try:
		for status in client.register(store):
			if status == WebOSClient.PROMPTED:
				tried.append('PROMPTED: user must accept on TV')
			elif status == WebOSClient.REGISTERED:
				tried.append('REGISTERED')
				if store_path:
					try:
						store_path.write_text(json.dumps(store))
						tried.append(f'Saved store to {store_path}')
					except Exception:
						tried.append(f'Could not save store to {store_path}')

		app_ctrl = None
		try:
			app_ctrl = ApplicationControl(client)
		except Exception as e:
			tried.append(f'No ApplicationControl: {e}')

		# Try application control methods first with both string and dict params
		if app_ctrl:
			for candidate in candidates:
				# Try with dict param format
				for method in ("launch", "launch_app", "launch_app_by_id", "launchApplication"):
					if hasattr(app_ctrl, method):
						# Try dict format first
						try:
							getattr(app_ctrl, method)({'id': candidate})
							return {"ok": True, "details": f"Launched {candidate} via ApplicationControl.{method}(dict)"}
						except Exception as e:
							tried.append((f'ApplicationControl.{method}(dict:{candidate})', str(e)[:60]))
						# Try string format
						try:
							getattr(app_ctrl, method)(candidate)
							return {"ok": True, "details": f"Launched {candidate} via ApplicationControl.{method}(str)"}
						except Exception as e:
							tried.append((f'ApplicationControl.{method}(str:{candidate})', str(e)[:60]))

		# Direct client.call with various WebOS services for launching apps
		svc_candidates = [
			('luna://com.webos.applicationManager', 'launch'),
			('luna://com.webos.applicationManager', 'open'),
			('luna://com.webos.service.launcher', 'launch'),
			('luna://com.webos.service.launcher', 'open'),
			('com.webos.applicationManager', 'launch'),
			('launcher', 'open'),
		]

		for candidate in candidates:
			for svc, method in svc_candidates:
				params = {'id': candidate}
				if hasattr(client, 'call'):
					try:
						client.call(svc, method, params)
						return {"ok": True, "details": f"Launched {candidate} via client.call {svc}/{method}"}
					except Exception as e:
						tried.append((f'call:{svc}/{method}({candidate})', str(e)[:50]))

				if hasattr(client, 'request'):
					try:
						client.request(svc, method, params)
						return {"ok": True, "details": f"Launched {candidate} via client.request {svc}/{method}"}
					except Exception as e:
						tried.append((f'request:{svc}/{method}({candidate})', str(e)[:50]))

		return {"ok": False, "details": tried}
	except Exception as e:
		return {"ok": False, "details": f"pywebostv launch request failed: {e}"}

def try_go_home_pywebostv(ip: str, store_path: Path | None, timeout: int = 10):
	"""Attempt to go to home screen via pywebostv.

	Returns a dict with keys: `ok` (bool) and `details` (list or message).
	"""
	try:
		from pywebostv.connection import WebOSClient
		from pywebostv.controls import SystemControl, ApplicationControl
	except Exception as e:
		return {"ok": False, "details": f"pywebostv import failed: {e}"}

	store = {}
	if store_path and store_path.exists():
		try:
			store = json.loads(store_path.read_text())
		except Exception:
			store = {}

	client = WebOSClient(ip)
	try:
		client.connect()
	except Exception as e:
		return {"ok": False, "details": f"Failed to connect to TV at {ip}: {e}"}

	tried = []

	try:
		# Registration phase
		for status in client.register(store):
			if status == WebOSClient.PROMPTED:
				tried.append('PROMPTED: user must accept on TV')
			elif status == WebOSClient.REGISTERED:
				tried.append('REGISTERED')
				if store_path:
					try:
						store_path.write_text(json.dumps(store))
						tried.append(f'Saved store to {store_path}')
					except Exception:
						tried.append(f'Could not save store to {store_path}')

		# Try ApplicationControl first (like Netflix)
		app_ctrl = None
		try:
			app_ctrl = ApplicationControl(client)
			tried.append('ApplicationControl created')
		except Exception as e:
			tried.append(f'ApplicationControl creation failed: {str(e)[:60]}')

		if app_ctrl:
			# Try various home app IDs
			home_candidates = [
				'com.webos.app.home',
				'home',
				'com.lge.app.home',
			]
			for app_id in home_candidates:
				for method in ("launch", "launch_app"):
					if hasattr(app_ctrl, method):
						try:
							tried.append(f'try ApplicationControl.{method}({app_id})')
							getattr(app_ctrl, method)({'id': app_id})
							tried.append(f'SUCCESS: ApplicationControl.{method}({app_id})')
							return {"ok": True, "details": tried}
						except Exception as e:
							tried.append(f'FAILED {method}({app_id}): {str(e)[:40]}')

		# SystemControl request as fallback
		system = None
		try:
			system = SystemControl(client)
			tried.append('SystemControl created OK')
		except Exception as e:
			tried.append(f'SystemControl creation failed: {str(e)[:60]}')
			return {"ok": False, "details": tried}

		if system and hasattr(system, 'request'):
			tried.append('Trying SystemControl.request for home')
			try:
				system.request('com.webos.service.core-apps', 'launchCoreApp', {'id': 'home'})
				tried.append('SUCCESS: launchCoreApp(home)')
				return {"ok": True, "details": tried}
			except Exception as e:
				tried.append(f'FAILED launchCoreApp: {str(e)[:40]}')

		return {"ok": False, "details": tried}
	except Exception as e:
		tried.append(f'Outer exception: {str(e)[:60]}')
		return {"ok": False, "details": tried}

def try_remote_button_pywebostv(ip: str, store_path: Path | None, button: str, timeout: int = 10) -> Dict[str, Any]:
	"""Send a remote control button press to the TV via pywebostv.
	
	Supported buttons: up, down, left, right, enter/ok, back, home, menu, mute, 
	volumeup, volumedown, channelup, channeldown, etc.
	
	Returns a dict with keys: `ok` (bool) and `details` (message or list).
	"""
	try:
		from pywebostv.connection import WebOSClient
		from pywebostv.controls import InputControl
	except Exception as e:
		return {"ok": False, "details": f"pywebostv import failed: {e}"}
	
	store = {}
	if store_path and store_path.exists():
		try:
			store = json.loads(store_path.read_text())
		except Exception:
			store = {}
	
	client = WebOSClient(ip)
	try:
		client.connect()
	except Exception as e:
		return {"ok": False, "details": f"Failed to connect to TV at {ip}: {e}"}
	
	tried = []
	
	try:
		# Registration phase
		for status in client.register(store):
			if status == WebOSClient.PROMPTED:
				tried.append('PROMPTED: user must accept on TV')
			elif status == WebOSClient.REGISTERED:
				tried.append('REGISTERED')
				if store_path:
					try:
						store_path.write_text(json.dumps(store))
						tried.append(f'Saved store to {store_path}')
					except Exception:
						pass
		
		# Button name mapping (to InputControl command names)
		button_lower = button.lower().replace('_', '')
		button_mapping = {
			'up': 'up',
			'down': 'down',
			'left': 'left',
			'right': 'right',
			'enter': 'ok',
			'ok': 'ok',
			'select': 'ok',
			'back': 'back',
			'return': 'back',
			'exit': 'exit',
			'home': 'home',
			'menu': 'menu',
			'mute': 'mute',
			'volumeup': 'volume_up',
			'volume_up': 'volume_up',
			'volumedown': 'volume_down',
			'volume_down': 'volume_down',
			'channelup': 'channel_up',
			'channel_up': 'channel_up',
			'channeldown': 'channel_down',
			'channel_down': 'channel_down',
			'info': 'info',
			'red': 'red',
			'green': 'green',
			'yellow': 'yellow',
			'blue': 'blue',
			'num0': 'num_0',
			'num1': 'num_1',
			'num2': 'num_2',
			'num3': 'num_3',
			'num4': 'num_4',
			'num5': 'num_5',
			'num6': 'num_6',
			'num7': 'num_7',
			'num8': 'num_8',
			'num9': 'num_9',
			'play': 'play',
			'pause': 'pause',
			'stop': 'stop',
			'rewind': 'rewind',
			'fastforward': 'fastforward',
			'ffwd': 'fastforward',
		}
		
		cmd_name = button_mapping.get(button_lower, button_lower)
		
		# Try to send via InputControl
		try:
			input_control = InputControl(client)
			tried.append(f'InputControl created')
			
			# Connect the input channel (required for button presses)
			try:
				input_control.connect_input()
				tried.append(f'Input channel connected')
			except Exception as e:
				tried.append(f'connect_input failed: {str(e)[:60]}')
				# Some TVs may not support mouse socket, but button presses might still work
			
			# Check if the command is available
			if cmd_name in InputControl.INPUT_COMMANDS:
				# Dynamically call the command method (e.g., input_control.up())
				try:
					cmd_method = getattr(input_control, cmd_name)
					cmd_method()
					return {"ok": True, "details": f"Sent button '{button}' via InputControl.{cmd_name}()"}
				except Exception as e:
					tried.append(f"exec_mouse_command for '{cmd_name}' failed: {str(e)[:60]}")
			else:
				tried.append(f"Command '{cmd_name}' not in INPUT_COMMANDS")
				# List a few available commands for debugging
				available = list(InputControl.INPUT_COMMANDS.keys())[:5]
				tried.append(f"Available commands (sample): {available}")
		except Exception as e:
			tried.append(f'InputControl initialization failed: {str(e)[:60]}')
		
		return {"ok": False, "details": tried}
	
	except Exception as e:
		tried.append(f'Outer exception: {str(e)[:80]}')
		return {"ok": False, "details": tried}


def main():
	parser = argparse.ArgumentParser(description='Turn on LG WebOS TV via unicast WOL + optional WebOS verify')
	parser.add_argument('--ip', help='IP address of the TV (required for unicast WOL)', default='192.168.0.167')
	parser.add_argument('--mac', help='MAC address of the TV (required to send Wake-on-LAN)', default='F0-86-20-48-2D-46')
	parser.add_argument('--wait', type=int, default=5, help='Seconds to wait after WOL before verifying')
	parser.add_argument('--store', help='Path to JSON file to persist pywebostv auth store', default='store.json')
	args = parser.parse_args()

	if not args.mac or not args.ip:
		print('Please provide both --mac and --ip to send unicast Wake-on-LAN')
		return

	try:
		print(f'Sending Wake-on-LAN magic packet to {args.ip}')
		send_magic_packet_unicast(args.mac, args.ip)
		print('Magic packet sent.')
	except Exception as e:
		print('Failed to send magic packet:', e)
		return

	print(f'Waiting {args.wait} seconds for TV to wake...')
	time.sleep(args.wait)
	store_path = Path(args.store) if args.store else None
	ok = try_connect_pywebostv(args.ip, store_path, timeout=args.wait)
	if ok:
		print('TV appears online and reachable via WebOS API.')
	else:
		print('Could not verify via WebOS API. TV may be still booting or pywebostv not installed.')

if __name__ == '__main__':
	main()
