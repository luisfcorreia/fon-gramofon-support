# Gramofon Device Configuration Tools

This repository contains tools for configuring Gramofon devices without the official Android app, which no longer works on Android 14+.

## Background

The Gramofon is a WiFi-enabled audio streaming device manufactured by Fon. The company has ceased operations, and the official Android app is no longer compatible with modern Android versions. These tools were created through reverse engineering of the original APK to enable continued use of these devices.

## What's Included

1. **API Documentation** (`gramofon_api_documentation.md`) - Complete HTTP API reference
2. **Python Client** (`gramofon_client.py`) - Full-featured Python client library
3. **Bash Script** (`gramofon_config.sh`) - Simple shell script for quick configuration
4. **Analysis Scripts** - Tools used for reverse engineering the APK

## Quick Start

### Prerequisites

- The Gramofon device in setup mode (creates its own WiFi network)
- A computer connected to the Gramofon's WiFi network
- Python 3.6+ (for Python client) or bash (for shell script)

### Method 1: Using the Bash Script (Simplest)

1. Connect your computer to the Gramofon's WiFi network (usually named "Gramofon-XXXX")

2. Make the script executable:
```bash
chmod +x gramofon_config.sh
```

3. Get device information:
```bash
./gramofon_config.sh info
```

4. Configure the device:
```bash
./gramofon_config.sh configure "YourWiFiNetwork" "YourPassword" "Living Room Speaker"
```

### Method 2: Using the Python Client

1. Install required packages:
```bash
pip install requests
```

2. Connect to the Gramofon's WiFi network

3. Use the client:

**Get device status:**
```bash
python gramofon_client.py status
```

**Scan for networks:**
```bash
python gramofon_client.py wifi --scan
```

**Complete configuration:**
```bash
python gramofon_client.py configure "YourWiFiNetwork" "YourPassword" --name "Living Room"
```

## Usage Examples

### Check Device Status
```bash
# Using bash script
./gramofon_config.sh status

# Using Python
python gramofon_client.py status
```

### Scan for WiFi Networks
```bash
# Using bash script
./gramofon_config.sh scan

# Using Python
python gramofon_client.py wifi --scan
```

### Configure WiFi
```bash
# Using bash script
./gramofon_config.sh wifi-set "MyNetwork" "MyPassword"

# Using Python
python gramofon_client.py wifi --set "MyNetwork" "MyPassword"
```

### Set Device Name
```bash
# Using bash script
./gramofon_config.sh name "Kitchen Speaker"

# Using Python
python gramofon_client.py name --set "Kitchen Speaker"
```

### Complete Setup (All-in-One)
```bash
# Using bash script
./gramofon_config.sh configure "MyNetwork" "MyPassword" "Kitchen"

# Using Python
python gramofon_client.py configure "MyNetwork" "MyPassword" --name "Kitchen"
```

### Check Firmware Version
```bash
# Using bash script
./gramofon_config.sh version

# Using Python
python gramofon_client.py version
```

## Python Client as a Library

You can also use the Python client as a library in your own scripts:

```python
from gramofon_client import GramofonClient

# Create client
client = GramofonClient(device_ip="192.168.10.1")

# Get status
status = client.get_status()
print(f"Device status: {status}")

# Scan for networks
networks = client.scan_networks()
print(f"Found {len(networks)} networks")

# Configure WiFi
result = client.set_wifi_config("MyNetwork", "MyPassword")

# Set device name
client.set_device_name("Living Room Speaker")

# Complete configuration
results = client.configure_device(
    ssid="MyNetwork",
    password="MyPassword",
    device_name="Living Room"
)
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
- Ensure you're connected to the Gramofon's WiFi network
- Try resetting the device (hold reset button for 10+ seconds)
- Check that the device IP is 192.168.10.1 (ping it first)
- Verify the device is in setup mode (LED should be flashing)

### Connection Timeout
- Increase timeout in Python client: `GramofonClient(timeout=30)`
- Try the bash script which may handle network issues better
- Check firewall settings on your computer

### Authentication Errors
- The session ID may need to be obtained from the device first
- Try accessing `http://192.168.10.1` in a web browser to see the web interface
- Monitor network traffic with Wireshark to see actual API calls

### WiFi Configuration Not Working
- Verify the SSID is correct (case-sensitive)
- Check password is correct
- Try manually connecting to the network first to verify credentials
- Some security types may require additional parameters

## API Endpoints Reference

All endpoints use base URL: `http://192.168.10.1/api/{session_id}/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `status` | GET | Get device status |
| `get_fw_version` | GET | Get firmware version |
| `get_fonmac` | GET | Get MAC address |
| `get_gramofonname` | GET | Get device name |
| `set_gramofonname` | POST | Set device name |
| `get_wiface` | GET | Get WiFi config |
| `set_wiface` | POST | Set WiFi config |
| `get_ssids` | GET | Scan networks |
| `check_upgrades` | GET | Check firmware updates |
| `check_adapters` | GET | Check network adapters |
| `check_validation` | GET | Validate configuration |

See `gramofon_api_documentation.md` for complete API details.

## Files Included

- `gramofon_api_documentation.md` - Complete API reference
- `gramofon_client.py` - Python client and CLI tool
- `gramofon_config.sh` - Bash script for simple operations
- `extract_api_info.py` - Script used to analyze the APK
- `analyze_dex.py` - DEX file analysis tool

## Contributing

If you discover additional API endpoints or improve the tools, please share your findings!

Areas that need investigation:
- Actual session ID generation/authentication
- Additional configuration parameters
- Fonera mode settings
- Firmware update process
- Music streaming API (if separate)

## Legal

This work is provided for educational purposes and to enable continued use of legacy hardware whose manufacturer has ceased operations. The reverse engineering was performed solely to maintain compatibility with purchased hardware.

## Credits

- Reverse engineered from Gramofon Setup APK version 114602
- Original hardware by Fon/Gramofon (defunct)
- Tools created to preserve functionality of existing devices

## Support

Since the manufacturer is defunct, community support is the only option. If you find these tools useful or have improvements, please share with other Gramofon users!
