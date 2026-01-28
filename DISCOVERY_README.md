# Gramofon Network Discovery & Management

After your Gramofon is configured and connected to your home WiFi, you can continue to manage it using the same JSON-RPC API. These tools help you discover and control your Gramofon devices on your local network.

## Overview

Once configured, Gramofon devices:
- ✅ Keep the same JSON-RPC 2.0 API interface
- ✅ Are accessible via their home network IP address
- ✅ Can be controlled remotely (LED, reboot, status, etc.)
- ✅ Still use admin/admin credentials

## Tools Included

### 1. `gramofon_discovery.py` - Full Discovery & Management Tool

**Features:**
- Auto-detects your local network
- Scans for all Gramofon devices
- Interactive menu for device management
- Batch LED control
- Device information retrieval

**Quick Start:**
```bash
# Auto-discover and manage devices
python gramofon_discovery.py

# Scan specific network
python gramofon_discovery.py --network 192.168.1.0/24

# Turn off LED on all devices
python gramofon_discovery.py --led-off

# Just list devices
python gramofon_discovery.py --list

# Control specific device
python gramofon_discovery.py --ip 192.168.1.100 --led-off
```

**Interactive Mode:**

When run without arguments, the tool will:
1. Auto-detect your network
2. Scan for Gramofon devices
3. Show an interactive menu where you can:
   - Select a device
   - Control LED (on/off/status)
   - Get device status
   - Reboot device
   - View device information

### 2. `gramofon_led_control.sh` - Quick LED Control (Bash)

**Features:**
- Simple bash script for quick LED control
- Network scanning capability
- No Python required

**Usage:**
```bash
# Turn LED off on specific device
./gramofon_led_control.sh 192.168.1.100 off

# Turn LED on
./gramofon_led_control.sh 192.168.1.100 on

# Get LED status
./gramofon_led_control.sh 192.168.1.100 status

# Scan network for devices
./gramofon_led_control.sh scan 192.168.1
```

### 3. `gramofon_jsonrpc_client.py` - Direct Control (If you know the IP)

If you already know your device's IP address:

```bash
# Turn LED off
python gramofon_jsonrpc_client.py --ip 192.168.1.100 led --off

# Turn LED on
python gramofon_jsonrpc_client.py --ip 192.168.1.100 led --on

# Get status
python gramofon_jsonrpc_client.py --ip 192.168.1.100 status

# Reboot
python gramofon_jsonrpc_client.py --ip 192.168.1.100 system --reboot
```

## Common Use Cases

### Turn Off LED on All Devices

**Python (recommended):**
```bash
python gramofon_discovery.py --led-off
```

**Bash:**
```bash
# Scan and save device list
./gramofon_led_control.sh scan 192.168.1

# Turn off each device (manual)
./gramofon_led_control.sh 192.168.1.50 off
./gramofon_led_control.sh 192.168.1.51 off
```

### Find Your Gramofon's IP Address

**Method 1: Discovery scan**
```bash
python gramofon_discovery.py --list
```

**Method 2: Check your router**
- Log into your router's admin interface
- Look for devices named "gramofon" or "Gramofon"
- Note the IP address

**Method 3: Network scan tools**
```bash
# Using nmap (if installed)
nmap -p 80 192.168.1.0/24 | grep -B 5 "gramofon"

# Using arp
arp -a | grep -i gramofon
```

### Monitor Multiple Devices

Create a script to check all your devices:

```bash
#!/bin/bash
# my_gramofons.sh

DEVICES=(
    "192.168.1.50|Living Room"
    "192.168.1.51|Bedroom"
    "192.168.1.52|Kitchen"
)

for device in "${DEVICES[@]}"; do
    IP=$(echo $device | cut -d'|' -f1)
    NAME=$(echo $device | cut -d'|' -f2)
    
    echo "Checking $NAME ($IP)..."
    python gramofon_jsonrpc_client.py --ip $IP status
    echo ""
done
```

### Automated LED Control with Cron

Turn off LEDs every night at 10 PM:

```bash
# Add to crontab (crontab -e)
0 22 * * * /usr/bin/python3 /path/to/gramofon_discovery.py --led-off

# Turn back on at 8 AM
0 8 * * * /usr/bin/python3 /path/to/gramofon_discovery.py --led-on
```

## How Discovery Works

1. **Network Scanning**: The tool scans IP addresses on your network
2. **API Check**: For each IP, it attempts to:
   - Connect to `http://IP/api/00000000000000000000000000000000`
   - Login with admin/admin credentials
   - Request device information
3. **Identification**: If successful and device responds with Gramofon-specific data, it's identified
4. **Information Gathering**: Device name, MAC address, and other info is retrieved

## Troubleshooting

### Discovery finds no devices

**Check network:**
```bash
# Make sure you're on the same network as your Gramofon
ip addr show  # Linux
ifconfig      # macOS

# Try pinging known Gramofon IP
ping 192.168.1.100
```

**Manual IP specification:**
If you know the IP but discovery doesn't find it:
```bash
python gramofon_discovery.py --ip 192.168.1.100
```

**Firewall issues:**
- Ensure your firewall isn't blocking outgoing connections to port 80
- Check router firewall settings

### Device found but commands fail

**Session timeout:**
The device may have expired the session. The tools auto-login, but if you see repeated failures:
```bash
# Try reconnecting
python gramofon_jsonrpc_client.py --ip <IP> status
```

**Device rebooting:**
If you just configured or rebooted the device, wait 30-60 seconds.

### Scan is very slow

**Reduce scan range:**
```bash
# Instead of /24 (254 addresses), scan smaller range
python gramofon_discovery.py --network 192.168.1.50/28  # Only 14 addresses
```

**Increase timeout:**
```bash
# Default is 2 seconds per IP, increase for slow networks
python gramofon_discovery.py --timeout 5
```

## API Endpoints Available on Network

All the same JSON-RPC endpoints work when the device is on your network:

| Module.Method | Purpose |
|---------------|---------|
| `ledd.switch` | Turn LED on/off |
| `ledd.get` | Get LED status |
| `anet.status` | Get device status |
| `anet.get_gramofonname` | Get device name |
| `anet.set_gramofonname` | Set device name |
| `mfgd.get_fonmac` | Get MAC address |
| `mfgd.reboot` | Reboot device |
| `mfgd.check_upgrades` | Check firmware updates |

See `COMPLETE_API_DOCUMENTATION.md` for full API reference.

## Network Security Note

The Gramofon devices use simple admin/admin authentication. Since they're on your home network:

**Recommendations:**
- Keep devices on isolated VLAN if possible
- Use network firewall to prevent external access
- Don't port forward Gramofon devices to the internet
- Consider setting up MAC address filtering on your router

## Integration Examples

### Home Assistant

```yaml
# configuration.yaml
switch:
  - platform: command_line
    switches:
      gramofon_led:
        command_on: "python3 /path/to/gramofon_jsonrpc_client.py --ip 192.168.1.100 led --on"
        command_off: "python3 /path/to/gramofon_jsonrpc_client.py --ip 192.168.1.100 led --off"
```

### Node-RED

Use HTTP request node with JSON-RPC payload to control devices.

### Python Script

```python
from gramofon_discovery import scan_network

# Find all devices
devices = scan_network("192.168.1.0/24")

# Turn off all LEDs
for device in devices:
    device.set_led(False)
    print(f"Turned off LED on {device.name}")
```

## Performance Tips

1. **Save device IPs**: Once you find your devices, save their IPs instead of scanning every time
2. **Use specific IPs**: Direct IP access is much faster than network scanning
3. **Batch operations**: Use the discovery tool's batch features (`--led-off`, `--led-on`)
4. **Parallel execution**: The discovery tool uses threading for fast scanning

## Summary

| Task | Best Tool | Command |
|------|-----------|---------|
| Find devices | Discovery script | `python gramofon_discovery.py --list` |
| Turn off all LEDs | Discovery script | `python gramofon_discovery.py --led-off` |
| Quick LED toggle | LED control script | `./gramofon_led_control.sh <IP> off` |
| Full device control | JSON-RPC client | `python gramofon_jsonrpc_client.py --ip <IP>` |
| Interactive management | Discovery script | `python gramofon_discovery.py` |

---

**Pro Tip:** Create a shell alias for quick LED control:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias gramofon-led-off='python3 ~/gramofon/gramofon_discovery.py --led-off'
alias gramofon-led-on='python3 ~/gramofon/gramofon_discovery.py --led-on'

# Usage:
# gramofon-led-off
```
