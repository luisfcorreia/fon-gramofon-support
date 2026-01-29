# Gramofon Device Management Tools

Complete Python toolkit for configuring and managing Gramofon devices. These tools were created through reverse engineering of the Gramofon Setup APK to enable continued use of these legacy devices.

## 📦 What You Need

### Two Simple Python Scripts

1. **`gramofon_config.py`** - Complete configuration and management tool
2. **`gramofon_discovery.py`** - Network discovery tool

That's it! Everything else is optional documentation.

## 🚀 Quick Start

### Initial Setup (First Time)

1. **Factory reset your Gramofon** (hold reset button 10+ seconds)

2. **Connect to the device's WiFi network**: `"Gramofon Configuration"`

3. **Configure the device**:
   ```bash
   python gramofon_config.py setup "YourWiFiSSID" "YourPassword" --name "Living Room"
   ```

4. **Wait 30-60 seconds** for device to connect to your WiFi

### Daily Management

1. **Find your device on the network**:
   ```bash
   python gramofon_discovery.py
   ```

2. **Turn off LED** (main use case):
   ```bash
   # Turn off all devices
   python gramofon_discovery.py --led-off
   
   # Turn off specific device
   python gramofon_config.py --ip 192.168.1.100 led --off
   ```

That's all you need to know! Read below for more details.

---

## 📖 Detailed Documentation

### gramofon_config.py - Main Configuration Tool

Complete tool for all device operations.

#### Initial Setup Commands

```bash
# Basic setup
python gramofon_config.py setup "MyWiFi" "MyPassword"

# Setup with device name
python gramofon_config.py setup "MyWiFi" "MyPassword" --name "Living Room"
```

**Important**: Run setup commands while connected to the "Gramofon Configuration" WiFi network.

#### Device Management Commands

All management commands require the `--ip` parameter:

```bash
# Get device information
python gramofon_config.py --ip 192.168.1.100 info

# Get device status
python gramofon_config.py --ip 192.168.1.100 status

# Test connection
python gramofon_config.py --ip 192.168.1.100 test
```

#### LED Control

```bash
# Turn LED off
python gramofon_config.py --ip 192.168.1.100 led --off

# Turn LED on
python gramofon_config.py --ip 192.168.1.100 led --on

# Get LED status
python gramofon_config.py --ip 192.168.1.100 led --get
```

#### Device Name

```bash
# Get device name
python gramofon_config.py --ip 192.168.1.100 name

# Set device name
python gramofon_config.py --ip 192.168.1.100 name --set "Kitchen"
```

#### WiFi Operations

```bash
# Scan for networks
python gramofon_config.py --ip 192.168.1.100 wifi --scan

# Get WiFi configuration
python gramofon_config.py --ip 192.168.1.100 wifi --get

# Change WiFi network
python gramofon_config.py --ip 192.168.1.100 wifi --set "NewSSID" "NewPassword"

# Reload WiFi configuration
python gramofon_config.py --ip 192.168.1.100 wifi --reload
```

#### System Operations

```bash
# Reboot device
python gramofon_config.py --ip 192.168.1.100 system --reboot

# Factory reset (requires confirmation)
python gramofon_config.py --ip 192.168.1.100 system --reset
```

#### Firmware Management

```bash
# Check for firmware updates
python gramofon_config.py --ip 192.168.1.100 upgrade --check

# Apply firmware upgrade
python gramofon_config.py --ip 192.168.1.100 upgrade --apply "2.0.14"
```

---

### gramofon_discovery.py - Network Discovery Tool

Finds Gramofon devices on your local network and allows batch operations.

#### Discovery Commands

```bash
# Auto-discover and show interactive menu
python gramofon_discovery.py

# Auto-discover and list devices
python gramofon_discovery.py --list

# Scan specific network
python gramofon_discovery.py --network 192.168.1.0/24

# Check specific IP
python gramofon_discovery.py --ip 192.168.1.100
```

#### Batch Operations

```bash
# Turn off LED on all discovered devices
python gramofon_discovery.py --led-off

# Turn on LED on all discovered devices
python gramofon_discovery.py --led-on

# Control specific device
python gramofon_discovery.py --ip 192.168.1.100 --led-off
```

#### Interactive Mode

Run without arguments for interactive menu:

```bash
python gramofon_discovery.py
```

This will:
1. Auto-detect your network
2. Scan for all Gramofon devices
3. Show interactive menu for:
   - LED control (on/off/status)
   - Device information
   - Device status
   - Reboot device

---

## 🎯 Common Use Cases

### Turn Off All Device LEDs

The simplest way:

```bash
python gramofon_discovery.py --led-off
```

### Find Device IP Address

```bash
python gramofon_discovery.py --list
```

Output:
```
Discovered Gramofon Devices:
------------------------------------------------------------
  192.168.1.50    - Living Room         (aa:bb:cc:dd:ee:f1)
  192.168.1.51    - Bedroom             (aa:bb:cc:dd:ee:f2)
  192.168.1.52    - Kitchen             (aa:bb:cc:dd:ee:f3)
```

### Manage Multiple Devices

Create a shell script:

```bash
#!/bin/bash
# manage_all_gramofons.sh

DEVICES=(
    "192.168.1.50"
    "192.168.1.51"
    "192.168.1.52"
)

for ip in "${DEVICES[@]}"; do
    echo "Turning off LED on $ip..."
    python gramofon_config.py --ip $ip led --off
done
```

### Automated LED Control (Cron)

Turn off LEDs every night at 10 PM:

```bash
# Edit crontab
crontab -e

# Add this line:
0 22 * * * /usr/bin/python3 /path/to/gramofon_discovery.py --led-off
```

### Check Device Status

```bash
python gramofon_config.py --ip 192.168.1.100 status | python -m json.tool
```

---

## 🔧 Advanced Usage

### Custom Timeout

For slow networks or distant devices:

```bash
python gramofon_config.py --ip 192.168.1.100 --timeout 60 status
```

### Home Automation Integration

#### Home Assistant

```yaml
# configuration.yaml
shell_command:
  gramofon_led_off: "python3 /path/to/gramofon_config.py --ip 192.168.1.100 led --off"
  gramofon_led_on: "python3 /path/to/gramofon_config.py --ip 192.168.1.100 led --on"

# automations.yaml
- alias: "Gramofon LED Off at Night"
  trigger:
    platform: time
    at: "22:00:00"
  action:
    service: shell_command.gramofon_led_off
```

#### Python Script Integration

```python
import subprocess
import json

def get_gramofon_status(ip):
    """Get Gramofon device status"""
    result = subprocess.run(
        ['python', 'gramofon_config.py', '--ip', ip, 'status'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def turn_off_led(ip):
    """Turn off Gramofon LED"""
    subprocess.run(
        ['python', 'gramofon_config.py', '--ip', ip, 'led', '--off']
    )

# Usage
status = get_gramofon_status('192.168.1.100')
print(f"Device status: {status}")
turn_off_led('192.168.1.100')
```

---

## 🐛 Troubleshooting

### Cannot Find "Gramofon Configuration" Network

**Problem**: Device not in setup mode

**Solution**:
1. Hold reset button for 10+ seconds
2. Wait 30-60 seconds for device to boot
3. Check WiFi networks again

### Setup Command Fails

**Problem**: Not connected to device network

**Solution**:
```bash
# Check you're connected to "Gramofon Configuration"
# On macOS:
networksetup -getairportnetwork en0

# On Linux:
iwgetid -r

# Test connectivity
ping 192.168.10.1
```

### Discovery Finds No Devices

**Problem**: Devices on different network or network too large

**Solution**:
```bash
# Try specific network range
python gramofon_discovery.py --network 192.168.1.0/24

# Or check specific IP if you know it
python gramofon_discovery.py --ip 192.168.1.100
```

### "Network Error" or Timeout

**Problem**: Device unreachable or network slow

**Solution**:
```bash
# Increase timeout
python gramofon_config.py --ip 192.168.1.100 --timeout 60 status

# Check device is on
ping 192.168.1.100

# Check firewall isn't blocking port 80
```

### LED Command Fails

**Problem**: Device may be rebooting or session expired

**Solution**:
```bash
# Test connection first
python gramofon_config.py --ip 192.168.1.100 test

# If test passes, try LED command again
python gramofon_config.py --ip 192.168.1.100 led --off
```

---

## 📋 Requirements

### Required
- **Python 3.6+**
- **requests library**: `pip install requests`

### Optional
- **jq** (for prettier JSON output in some cases)

### Installation

```bash
# Install Python dependencies
pip install requests

# Make scripts executable (Unix/Linux/macOS)
chmod +x gramofon_config.py gramofon_discovery.py

# Optional: Add to PATH
sudo ln -s $(pwd)/gramofon_config.py /usr/local/bin/gramofon-config
sudo ln -s $(pwd)/gramofon_discovery.py /usr/local/bin/gramofon-discovery

# Now you can use from anywhere:
gramofon-config --help
gramofon-discovery --list
```

---

## 🔐 Security Notes

The Gramofon uses simple admin/admin authentication:

- Keep devices on your home network only
- Don't expose devices to the internet
- Consider VLAN isolation for IoT devices
- Use MAC filtering on your router if desired

---

## 📚 Additional Documentation

### Complete API Reference
- **COMPLETE_API_DOCUMENTATION.md** - Full JSON-RPC API documentation

### Discovery Details
- **DISCOVERY_README.md** - Detailed discovery tool documentation

---

## 🎉 Quick Reference Card

```bash
# SETUP (once)
python gramofon_config.py setup "WiFi" "Password" --name "Name"

# FIND DEVICES
python gramofon_discovery.py --list

# LED OFF (most common)
python gramofon_discovery.py --led-off                    # All devices
python gramofon_config.py --ip IP led --off               # One device

# LED ON
python gramofon_discovery.py --led-on                     # All devices
python gramofon_config.py --ip IP led --on                # One device

# INFO
python gramofon_config.py --ip IP info                    # Device info
python gramofon_config.py --ip IP status                  # Device status

# SYSTEM
python gramofon_config.py --ip IP system --reboot         # Reboot
python gramofon_config.py --ip IP test                    # Test connection
```

---

## 🙏 Credits

- Reverse engineered from Gramofon Setup APK v114602
- Decompiled Java source code analysis
- JSON-RPC 2.0 protocol discovered through code inspection
- Created to preserve functionality of legacy hardware
- Original hardware by Fon/Gramofon (defunct company)

---

## 📝 License

This work is provided for educational purposes and to enable continued use of legacy hardware whose manufacturer has ceased operations. The reverse engineering was performed solely to maintain compatibility with purchased hardware.

---

## 💡 Tips

1. **Save device IPs**: Once you discover your devices, note their IPs for faster access
2. **Use aliases**: Create shell aliases for frequent commands
3. **Batch operations**: Use discovery tool for multiple devices
4. **Test first**: Use `test` command before assuming device is broken
5. **Be patient**: Some operations take 5-10 seconds to respond

---

**Need help?** Use `--help` on any command:

```bash
python gramofon_config.py --help
python gramofon_config.py setup --help
python gramofon_config.py led --help
python gramofon_discovery.py --help
```
