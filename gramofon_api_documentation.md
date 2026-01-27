# Gramofon Device HTTP API - Complete Documentation
## Reverse Engineered from APK (VERIFIED)

This documentation has been verified against the actual decompiled Java source code from the Gramofon Setup APK.

## Critical Discovery: JSON-RPC API

The Gramofon device uses **JSON-RPC 2.0** protocol, NOT simple REST endpoints as initially thought.

## Base Configuration

- **Device IP**: `192.168.10.1` (when in setup mode)
- **Protocol**: JSON-RPC 2.0
- **Base URL**: `http://192.168.10.1/api/{session_id}`
- **Method**: POST (all requests)
- **Content-Type**: `application/json`
- **Authentication**: Session-based with username/password

## Authentication & Session Management

### 1. Obtain Session ID (Login)

**Endpoint**: `http://192.168.10.1/api/00000000000000000000000000000000`

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "session",
    "login",
    {
      "username": "admin",
      "password": "admin"
    }
  ]
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    0,
    {
      "sid": "abc123def456..." // This is your session ID
    }
  ]
}
```

**Important**: 
- Use the placeholder session ID `00000000000000000000000000000000` for the initial login
- Extract the `sid` from the response
- Use this `sid` for all subsequent API calls: `http://192.168.10.1/api/{sid}`

### Response Format

All JSON-RPC responses follow this structure:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    0,  // Status code: 0 = success
    {   // Actual response data
      // ... response fields ...
    }
  ]
}
```

Or on error:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32002,  // Error code
    "message": "Error message"
  }
}
```

## API Methods

### WiFi Configuration

#### Get WiFi Configuration
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "wifid",
    "get_wiface",
    {
      "name": "private"
    }
  ]
}
```

**Response fields**:
- `mode`: WiFi mode (e.g., "psk2")
- `encryption`: Encryption type
- `device`: Device name
- `ssid`: Network SSID
- `macaddr`: MAC address
- `key`: WiFi password
- `network`: Network name
- `bssid`: Access point BSSID
- `disabled`: Boolean, whether disabled

#### Set WiFi Configuration
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "wifid",
    "set_wiface",
    {
      "name": "private",
      "ssid": "YourNetworkName",
      "key": "YourPassword",
      "mode": "psk2",
      "encryption": "ap"
    }
  ]
}
```

#### Easy Setup (Complete WiFi Configuration)
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "anet",
    "doeasysetup",
    {
      "netmode": "wcliclone",
      "ssid": "YourNetworkName",
      "bssid": "aa:bb:cc:dd:ee:ff",  // Optional, for firmware >= 2.0.14
      "key": "YourPassword",
      "encryption": "psk2",
      "gramofon_name": "Living Room",  // Optional device name
      "ap_disabled": false
    }
  ]
}
```

**Note**: `netmode` can be:
- `wcliclone`: WiFi client mode (connect to existing network)
- `ethbridged`: Ethernet bridge mode

#### Reload WiFi Configuration
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "wifid",
    "reload",
    {}
  ]
}
```

### Network Scanning

#### Start WiFi Scan
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "anet",
    "ssid_scan",
    {
      "iface": "radio"
    }
  ]
}
```

#### Get Scan Results
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "anet",
    "get_ssids",
    {}
  ]
}
```

**Response** includes array of networks with:
- `ssid`: Network name
- `bssid`: MAC address
- `quality`: Signal strength value
- `quality_max`: Maximum signal strength
- `encryption`: Security type

### Device Information

#### Get Device Name
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "anet",
    "get_gramofonname",
    {}
  ]
}
```

**Response**:
```json
{
  "result": [
    0,
    {
      "spotifyname": "Living Room",
      "mdnsname": "Living Room"
    }
  ]
}
```

#### Set Device Name
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "anet",
    "set_gramofonname",
    {
      "mdnsname": "Living Room",
      "spotifyname": "Living Room"
    }
  ]
}
```

#### Get MAC Address
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "mfgd",
    "get_fonmac",
    {}
  ]
}
```

**Response**:
```json
{
  "result": [
    0,
    {
      "fonmac": "aa:bb:cc:dd:ee:ff"
    }
  ]
}
```

#### Get Device Status
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "anet",
    "status",
    {}
  ]
}
```

**Response includes**:
- `mode`: Current operating mode object with `code`
- `reqmode`: Requested mode object with `code`

### Firmware Management

#### Check for Upgrades
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "mfgd",
    "check_upgrades",
    {}
  ]
}
```

**Response**:
```json
{
  "result": [
    0,
    {
      "images": [
        {
          "firmware_id": "2.0.14",
          "user_message": "New firmware available"
        }
      ]
    }
  ]
}
```

#### Apply Firmware Upgrade
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "mfgd",
    "upgrade",
    {
      "firmware_id": "2.0.14"
    }
  ]
}
```

### Device Control

#### Reboot Device
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "mfgd",
    "reboot",
    {}
  ]
}
```

#### Reset to Factory Defaults
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "mfgd",
    "reset_defaults",
    {}
  ]
}
```

#### LED Control

**Get LED Status**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "ledd",
    "get",
    {}
  ]
}
```

**Response**:
- `name`: "disabled" or enabled
- `color`: "blue", "red", "magenta", "cyan", "yellow", "green"

**Switch LED**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": [
    "ledd",
    "switch",
    {
      "status": "enable"  // or "disable"
    }
  ]
}
```

## Complete Configuration Workflow

1. **Connect** to Gramofon's WiFi network (device creates its own AP when unconfigured)

2. **Login** to get session ID:
   ```bash
   curl -X POST http://192.168.10.1/api/00000000000000000000000000000000 \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"call","params":["session","login",{"username":"admin","password":"admin"}]}'
   ```

3. **Extract SID** from response (e.g., `abc123...`)

4. **Scan for networks** (optional):
   ```bash
   curl -X POST http://192.168.10.1/api/{sid} \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"call","params":["anet","ssid_scan",{"iface":"radio"}]}'
   
   # Wait 2 seconds, then get results
   curl -X POST http://192.168.10.1/api/{sid} \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"call","params":["anet","get_ssids",{}]}'
   ```

5. **Configure WiFi**:
   ```bash
   curl -X POST http://192.168.10.1/api/{sid} \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"call","params":["anet","doeasysetup",{"netmode":"wcliclone","ssid":"YourNetwork","key":"YourPassword","encryption":"psk2","gramofon_name":"Living Room","ap_disabled":false}]}'
   ```

6. **Set device name** (if not done in step 5):
   ```bash
   curl -X POST http://192.168.10.1/api/{sid} \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"call","params":["anet","set_gramofonname",{"mdnsname":"Living Room","spotifyname":"Living Room"}]}'
   ```

7. **Reload WiFi** to apply changes:
   ```bash
   curl -X POST http://192.168.10.1/api/{sid} \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"call","params":["wifid","reload",{}]}'
   ```

## Error Codes

- `0`: Success
- `-32002`: Session expired or invalid - need to login again
- `-32600`: Invalid JSON-RPC request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error

## Important Notes

1. **Session Management**: Sessions can expire. If you get error `-32002`, re-authenticate to get a new session ID.

2. **Timeouts**: The device may take several seconds to respond to configuration changes. Use appropriate timeouts (10-30 seconds).

3. **Network Scanning**: After starting a scan with `ssid_scan`, wait at least 2 seconds before calling `get_ssids` to retrieve results.

4. **Firmware Versions**: Some features (like BSSID specification) require firmware version 2.0.14 or later.

5. **Encryption Types**: Supported values are typically:
   - `psk2`: WPA2-PSK
   - `psk`: WPA-PSK
   - `wep`: WEP (deprecated)
   - `none`: Open network

6. **API Modules**:
   - `session`: Authentication
   - `anet`: Network configuration
   - `wifid`: WiFi daemon control
   - `mfgd`: Manufacturing/device control
   - `ledd`: LED control
   - `hotspotd`: Hotspot configuration

## Python Example

```python
import requests
import json

class GramofonAPI:
    def __init__(self, ip="192.168.10.1"):
        self.ip = ip
        self.sid = None
        
    def call(self, module, method, params=None):
        """Make a JSON-RPC call"""
        url = f"http://{self.ip}/api/{self.sid or '00000000000000000000000000000000'}"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [module, method, params or {}]
        }
        
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        
        if "error" in data:
            raise Exception(f"API Error: {data['error']}")
            
        return data["result"][1] if len(data["result"]) > 1 else None
    
    def login(self):
        """Authenticate and get session ID"""
        result = self.call("session", "login", {
            "username": "admin",
            "password": "admin"
        })
        self.sid = result["sid"]
        return self.sid
    
    def configure_wifi(self, ssid, password, device_name=None):
        """Complete WiFi configuration"""
        params = {
            "netmode": "wcliclone",
            "ssid": ssid,
            "key": password,
            "encryption": "psk2",
            "ap_disabled": False
        }
        
        if device_name:
            params["gramofon_name"] = device_name
            
        return self.call("anet", "doeasysetup", params)
    
    def scan_networks(self):
        """Scan and return available WiFi networks"""
        # Start scan
        self.call("anet", "ssid_scan", {"iface": "radio"})
        
        # Wait for scan to complete
        import time
        time.sleep(2)
        
        # Get results
        result = self.call("anet", "get_ssids", {})
        return result.get("results", [])
    
    def set_name(self, name):
        """Set device name"""
        return self.call("anet", "set_gramofonname", {
            "mdnsname": name,
            "spotifyname": name
        })
    
    def reboot(self):
        """Reboot the device"""
        return self.call("mfgd", "reboot", {})

# Usage
api = GramofonAPI()
api.login()
api.configure_wifi("MyNetwork", "MyPassword", "Living Room")
```

## Bash Script Example

```bash
#!/bin/bash

API_BASE="http://192.168.10.1/api"
SID=""

# Login and get session ID
login() {
    local response=$(curl -s -X POST "$API_BASE/00000000000000000000000000000000" \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","id":1,"method":"call","params":["session","login",{"username":"admin","password":"admin"}]}')
    
    SID=$(echo "$response" | jq -r '.result[1].sid')
    echo "Session ID: $SID"
}

# Make API call
api_call() {
    local module="$1"
    local method="$2"
    local params="$3"
    
    curl -s -X POST "$API_BASE/$SID" \
        -H "Content-Type: application/json" \
        -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"call\",\"params\":[\"$module\",\"$method\",$params]}"
}

# Configure WiFi
configure_wifi() {
    local ssid="$1"
    local password="$2"
    local name="$3"
    
    local params="{\"netmode\":\"wcliclone\",\"ssid\":\"$ssid\",\"key\":\"$password\",\"encryption\":\"psk2\",\"gramofon_name\":\"$name\",\"ap_disabled\":false}"
    
    api_call "anet" "doeasysetup" "$params"
}

# Main
login
configure_wifi "MyNetwork" "MyPassword" "Living Room"
```

## Troubleshooting

1. **"Session expired" error**: Re-run the login to get a new session ID.

2. **404 errors**: Device may be rebooting or not accessible. Wait and retry.

3. **Timeout**: Increase timeout values. Configuration operations can take 10-30 seconds.

4. **WiFi not connecting**: Verify:
   - SSID is correct (case-sensitive)
   - Password is correct
   - Encryption type matches your network (usually "psk2" for WPA2)
   - Network is within range

5. **Device not responding after configuration**: Normal - device may reboot to apply changes. Wait 30-60 seconds.

## References

- Decompiled from: `Gramofon_Setup_114602.apk`
- Package: `com.fon.gramofonsetup`
- Main service class: `com.fon.gramofonsetup.services.C0714k`
- Protocol: JSON-RPC 2.0 specification
