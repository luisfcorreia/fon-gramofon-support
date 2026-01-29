# Gramofon Device Configuration Tools

This repository contains tools for configuring Gramofon devices without the official Android app, which no longer works on Android 14+.

## Background

The Gramofon is a WiFi-enabled audio streaming device manufactured by Fon. The company has ceased operations, and the official Android app is no longer compatible with modern Android versions. These tools were created through reverse engineering of the original APK (including decompiled Java source code) to enable continued use of these devices.

## ⚠️ Important: Which Files to Use

After decompiling the APK, we discovered the device uses **JSON-RPC 2.0**, not REST. Use these files:

### ✅ Correct Implementation (JSON-RPC)
- **COMPLETE_API_DOCUMENTATION.md** - Verified API documentation with JSON-RPC protocol
- **gramofon_jsonrpc_client.py** - Python client using JSON-RPC 2.0
- **gramofon_jsonrpc.sh** - Bash script using JSON-RPC 2.0

### ❌ Superseded Files (REST-based, won't work)
- ~~gramofon_api_documentation.md~~ (initial attempt)
- ~~gramofon_client.py~~ (initial attempt)
- ~~gramofon_config.sh~~ (initial attempt)

## What's Included

1. **COMPLETE_API_DOCUMENTATION.md** - Complete verified JSON-RPC API reference
2. **gramofon_jsonrpc_client.py** - Full-featured Python client using JSON-RPC 2.0
3. **gramofon_jsonrpc.sh** - Bash script using JSON-RPC 2.0
4. **README.md** - This file

## Quick Start

### Prerequisites

- The Gramofon device reset to factory settings (in setup mode)
- A computer with WiFi capability
- Python 3.6+ (for Python client) or bash (for shell script)

### Step 1: Connect to the Device

**IMPORTANT:** When factory reset, the Gramofon creates a WiFi network called **"Gramofon Configuration"**

1. Reset your Gramofon to factory settings (if needed):
   - Hold the reset button for 10+ seconds
   - Wait for the device to reboot
   - The LED will indicate setup mode (usually flashing)

2. On your computer, connect to the WiFi network: **"Gramofon Configuration"**
   - This is an open network (no password required)
   - Your computer will connect to the device at IP: 192.168.10.1

### Step 2: Configure the Device

### Method 1: Using the Bash Script (Simplest)

1. Make the script executable:
```bash
chmod +x gramofon_jsonrpc.sh
```

2. Get device information:
```bash
./gramofon_jsonrpc.sh info
```

3. Configure the device:
```bash
./gramofon_jsonrpc.sh configure "YourWiFiNetwork" "YourPassword" "Living Room Speaker"
```

### Method 2: Using the Python Client (Recommended)

1. Install required packages:
```bash
pip install requests
```

2. Connect to "Gramofon Configuration" WiFi network

3. Use the client:

**Complete configuration (easiest):**
```bash
python gramofon_jsonrpc_client.py configure "YourWiFiNetwork" "YourPassword" --name "Living Room"
```

**Get device status:**
```bash
python gramofon_jsonrpc_client.py status
```

**Scan for networks:**
```bash
python gramofon_jsonrpc_client.py wifi --scan
```

### Step 3: Verify Connection

After configuration:
1. The device will apply the WiFi settings and may reboot (wait 30-60 seconds)
2. Your Gramofon should now connect to your home WiFi network
3. The "Gramofon Configuration" network will disappear
4. You can now use your Gramofon for music streaming

## Usage Examples

### Check Device Status
```bash
# Using bash script
./gramofon_jsonrpc.sh status

# Using Python
python gramofon_jsonrpc_client.py status
```

### Scan for WiFi Networks
```bash
# Using bash script
./gramofon_jsonrpc.sh scan

# Using Python
python gramofon_jsonrpc_client.py wifi --scan
```

### Configure WiFi
```bash
# Using bash script
./gramofon_jsonrpc.sh wifi-set "MyNetwork" "MyPassword"

# Using Python
python gramofon_jsonrpc_client.py wifi --set "MyNetwork" "MyPassword"
```

### Set Device Name
```bash
# Using bash script
./gramofon_jsonrpc.sh name "Kitchen Speaker"

# Using Python
python gramofon_jsonrpc_client.py name --set "Kitchen Speaker"
```

### Complete Setup (All-in-One)
```bash
# Using bash script
./gramofon_jsonrpc.sh configure "MyNetwork" "MyPassword" "Kitchen"

# Using Python
python gramofon_jsonrpc_client.py configure "MyNetwork" "MyPassword" --name "Kitchen"
```

### LED Control
```bash
# Using bash script
./gramofon_jsonrpc.sh led-on
./gramofon_jsonrpc.sh led-off

# Using Python
python gramofon_jsonrpc_client.py led --on
python gramofon_jsonrpc_client.py led --off
```

### Check for Firmware Updates
```bash
# Using bash script
./gramofon_jsonrpc.sh upgrades

# Using Python
python gramofon_jsonrpc_client.py upgrade --check
```

## Python Client as a Library

You can also use the Python client as a library in your own scripts:

```python
from gramofon_jsonrpc_client import GramofonClient, GramofonAPIError

# Create client
client = GramofonClient(device_ip="192.168.10.1")

try:
    # Login (authenticate)
    session_id = client.login()
    print(f"Logged in with session: {session_id}")
    
    # Get status
    status = client.get_status()
    print(f"Device status: {status}")
    
    # Scan for networks
    networks = client.scan_networks()
    print(f"Found {len(networks)} networks")
    for net in networks:
        print(f"  - {net['ssid']}: {net['encryption']}")
    
    # Configure WiFi
    result = client.configure_wifi_simple("MyNetwork", "MyPassword", device_name="Living Room")
    
    # Reload WiFi to apply changes
    client.reload_wifi()
    
    # Set device name
    client.set_device_name("Living Room Speaker")
    
    # Complete configuration (does everything)
    results = client.configure_device(
        ssid="MyNetwork",
        password="MyPassword",
        device_name="Living Room"
    )
    
except GramofonAPIError as e:
    print(f"API Error: {e}")
```

## Advanced Usage

### Custom Device IP
If your device uses a different IP address:

```bash
# Bash script
export GRAMOFON_IP="192.168.1.100"
./gramofon_config.sh status

# Python client
python gramofon_client.py --ip 192.168.1.100 status
```

### Custom Session ID
If you discover the device uses a different session ID format:

```bash
# Bash script
export GRAMOFON_SESSION="your-session-id-here"
./gramofon_config.sh status

# Python client
python gramofon_client.py --session "your-session-id-here" status
```

## Troubleshooting

### Device Not Responding
- Ensure you're connected to the **"Gramofon Configuration"** WiFi network
- Try resetting the device to factory settings (hold reset button for 10+ seconds)
- Check that the device IP is 192.168.10.1 by running: `ping 192.168.10.1`
- Verify the device is in setup mode (LED should be flashing)
- Make sure no firewall is blocking connections to 192.168.10.1

### Cannot Find "Gramofon Configuration" Network
- Device may not be in setup mode - try factory reset
- Hold reset button for 10+ seconds until LED changes
- Wait 30-60 seconds for the device to fully boot
- Check if your WiFi adapter is enabled and scanning for networks
- Try moving closer to the device

### Connection Timeout
- Increase timeout: `python gramofon_jsonrpc_client.py --timeout 60 status`
- Check if you can ping the device: `ping 192.168.10.1`
- Verify you're connected to "Gramofon Configuration" network
- Try disabling other network interfaces temporarily
- Check firewall settings on your computer

### Authentication Errors / Session Errors
- The device uses JSON-RPC 2.0 with session-based authentication
- Login credentials are: username="admin", password="admin"
- Sessions can expire - the client will automatically re-login if needed
- If you see error code -32002, this means session expired

### WiFi Configuration Not Working
- Verify the SSID is correct (case-sensitive)
- Check password is correct
- Try manually connecting to the target network first to verify credentials
- Ensure your home network is 2.4GHz (Gramofon may not support 5GHz)
- Check that encryption is WPA2-PSK (most common)
- After configuration, wait 30-60 seconds for device to apply changes and reboot

### Device Appears Configured but Not Connecting
- Check if your home WiFi network is 2.4GHz (device may not support 5GHz)
- Verify router is not blocking the device (check MAC filtering)
- Try moving device closer to router
- Check router logs for connection attempts
- Factory reset and try configuration again

## API Protocol

The Gramofon uses **JSON-RPC 2.0** protocol, NOT REST!

All requests are POST to: `http://192.168.10.1/api/{session_id}`

### JSON-RPC Request Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": ["module", "method", {...parameters...}]
}
```

### Main API Modules

| Module | Description |
|--------|-------------|
| `session` | Authentication (login) |
| `anet` | Network configuration (main module) |
| `wifid` | WiFi daemon control |
| `mfgd` | Device control (reboot, reset, upgrade) |
| `ledd` | LED control |

### Common Methods

| Module.Method | Description |
|---------------|-------------|
| `session.login` | Authenticate and get session ID |
| `anet.status` | Get device status |
| `anet.get_ssids` | Get scanned WiFi networks |
| `anet.ssid_scan` | Start WiFi scan |
| `anet.doeasysetup` | Complete WiFi configuration |
| `anet.get_gramofonname` | Get device name |
| `anet.set_gramofonname` | Set device name |
| `wifid.get_wiface` | Get WiFi interface config |
| `wifid.reload` | Reload WiFi configuration |
| `mfgd.get_fonmac` | Get MAC address |
| `mfgd.check_upgrades` | Check firmware updates |
| `mfgd.reboot` | Reboot device |
| `mfgd.reset_defaults` | Factory reset |
| `ledd.get` | Get LED status |
| `ledd.switch` | Turn LED on/off |

See **COMPLETE_API_DOCUMENTATION.md** for full JSON-RPC API details with examples.

## Files Included

### Use These Files ✅
- **COMPLETE_API_DOCUMENTATION.md** - Complete verified JSON-RPC API reference
- **gramofon_jsonrpc_client.py** - Python client using JSON-RPC 2.0
- **gramofon_jsonrpc.sh** - Bash script using JSON-RPC 2.0
- **README.md** - This guide

### Historical/Superseded Files (Don't Use) ❌
- ~~gramofon_api_documentation.md~~ - Initial REST-based documentation (incorrect)
- ~~gramofon_client.py~~ - Initial REST client (won't work)
- ~~gramofon_config.sh~~ - Initial REST script (won't work)

The initial files were created from string analysis before we had access to the decompiled Java source code. After decompiling the APK, we discovered the device uses JSON-RPC 2.0, not REST. Always use the `_jsonrpc` versions!

## How It Works

1. **Factory Reset**: Device creates "Gramofon Configuration" WiFi network
2. **Connection**: Connect your computer to this network (device IP: 192.168.10.1)
3. **Authentication**: Login with username="admin", password="admin" to get session ID
4. **Configuration**: Send JSON-RPC commands to configure WiFi, device name, etc.
5. **Apply**: Device applies settings and reboots to connect to your home network

## Technical Details

- **Protocol**: JSON-RPC 2.0 over HTTP
- **Authentication**: Session-based (obtain `sid` via login)
- **Default Credentials**: admin/admin
- **Setup Network**: "Gramofon Configuration" (open, no password)
- **Device IP in Setup Mode**: 192.168.10.1
- **Reverse Engineered From**: Gramofon Setup APK v114602 (including decompiled Java source)

## Tested Firmware Versions

These tools have been verified against the decompiled APK source code and should work with firmware versions:
- 2.0.14 and later (recommended)
- May work with earlier versions but some features (like BSSID specification) require 2.0.14+

## Legal

This work is provided for educational purposes and to enable continued use of legacy hardware whose manufacturer has ceased operations. The reverse engineering was performed solely to maintain compatibility with purchased hardware.

## Credits

- Reverse engineered from Gramofon Setup APK version 114602
- Decompiled Java source code analyzed to verify API implementation
- Discovered JSON-RPC 2.0 protocol through code analysis
- Original hardware by Fon/Gramofon (defunct company)
- Tools created to preserve functionality of existing devices
- Special thanks to the Android reverse engineering community

## Support & Community

Since the manufacturer (Fon/Gramofon) is defunct, community support is the only option. If you find these tools useful or have improvements:
- Share your experiences with other Gramofon users
- Report issues or improvements
- Help others in the community troubleshoot their devices

These tools represent hundreds of hours of reverse engineering work to keep legacy hardware functional!
