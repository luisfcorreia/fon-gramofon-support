# Gramofon Tools - Quick Reference Guide

## 📋 Complete Tool List

### Initial Setup Tools
1. **test_gramofon_connection.py** - Test connection to device
2. **gramofon_jsonrpc_client.py** - Configure new device
3. **gramofon_jsonrpc.sh** - Configure new device (bash)

### Discovery & Management Tools
4. **gramofon_discovery.py** - Find and manage devices on network
5. **gramofon_led_control.sh** - Quick LED control (bash)

### Factory Reset Tools (⚠️ Use with caution!)
6. **gramofon_factory_reset.py** - Factory reset with double confirmation
7. **gramofon_factory_reset.sh** - Factory reset (bash)

### Documentation
8. **README.md** - Main setup guide
9. **COMPLETE_API_DOCUMENTATION.md** - Full API reference
10. **DISCOVERY_README.md** - Discovery tools guide

---

## 🚀 Quick Command Reference

### First Time Setup (New/Reset Device)

```bash
# 1. Connect to "Gramofon Configuration" WiFi

# 2. Test connection
python test_gramofon_connection.py

# 3. Configure device
python gramofon_jsonrpc_client.py configure "YourWiFi" "YourPassword" --name "Living Room"
```

### Daily Usage (Configured Devices)

```bash
# Find all devices on network
python gramofon_discovery.py --list

# Turn off all LEDs (your main use case!)
python gramofon_discovery.py --led-off

# Turn on all LEDs
python gramofon_discovery.py --led-on

# Control specific device LED
python gramofon_jsonrpc_client.py --ip 192.168.1.100 led --off

# Interactive management
python gramofon_discovery.py
```

### LED Control (Quick)

```bash
# Bash script - fastest for single device
./gramofon_led_control.sh 192.168.1.100 off
./gramofon_led_control.sh 192.168.1.100 on
./gramofon_led_control.sh 192.168.1.100 status

# Python - if you know the IP
python gramofon_jsonrpc_client.py --ip 192.168.1.100 led --off
python gramofon_jsonrpc_client.py --ip 192.168.1.100 led --on

# Python - all devices at once
python gramofon_discovery.py --led-off
python gramofon_discovery.py --led-on
```

### Factory Reset (⚠️ Careful!)

```bash
# Python (recommended - most user-friendly)
python gramofon_factory_reset.py --ip 192.168.1.100

# Bash
./gramofon_factory_reset.sh 192.168.1.100

# From discovery tool (interactive)
python gramofon_discovery.py
# Select device → Option 7
```

**Important:** Factory reset requires:
1. Typing "yes" to first confirmation
2. Typing the exact device name to second confirmation

### Device Information

```bash
# Get status of specific device
python gramofon_jsonrpc_client.py --ip 192.168.1.100 status

# Get MAC address
python gramofon_jsonrpc_client.py --ip 192.168.1.100 mac

# Get device name
python gramofon_jsonrpc_client.py --ip 192.168.1.100 name

# All info at once
python gramofon_discovery.py --list
```

### Network Operations

```bash
# Scan network for devices
python gramofon_discovery.py --list
./gramofon_led_control.sh scan 192.168.1

# Reboot device
python gramofon_jsonrpc_client.py --ip 192.168.1.100 system --reboot

# Check for firmware updates
python gramofon_jsonrpc_client.py --ip 192.168.1.100 upgrade --check
```

---

## 🎯 Common Scenarios

### Scenario 1: Turn Off LED on All Devices Every Night

**Option A: Run manually**
```bash
python gramofon_discovery.py --led-off
```

**Option B: Automate with cron**
```bash
# Edit crontab
crontab -e

# Add this line (10 PM every night)
0 22 * * * cd /path/to/gramofon && python3 gramofon_discovery.py --led-off

# Optional: Turn back on at 8 AM
0 8 * * * cd /path/to/gramofon && python3 gramofon_discovery.py --led-on
```

### Scenario 2: Configure New Device

```bash
# Connect to "Gramofon Configuration" WiFi first!
python gramofon_jsonrpc_client.py configure "HomeWiFi" "password123" --name "Kitchen"
```

### Scenario 3: Find Device IP After Configuration

```bash
# Method 1: Use discovery
python gramofon_discovery.py --list

# Method 2: Check router DHCP leases
# (Log into your router and look for "gramofon" or device MAC)

# Method 3: Network scan
nmap -p 80 192.168.1.0/24 | grep -B 5 "gramofon"
```

### Scenario 4: Reset Device to Factory Settings

```bash
# Find the device IP first
python gramofon_discovery.py --list

# Reset it (requires double confirmation)
python gramofon_factory_reset.py --ip 192.168.1.100

# Wait for device to reboot (30-60 seconds)
# Then configure again from "Gramofon Configuration" WiFi
```

### Scenario 5: Quick LED Toggle for One Device

```bash
# If you know the IP, bash is fastest
./gramofon_led_control.sh 192.168.1.100 off

# Or create an alias
alias kitchen-led-off='./gramofon_led_control.sh 192.168.1.100 off'
alias kitchen-led-on='./gramofon_led_control.sh 192.168.1.100 on'

# Then just use:
kitchen-led-off
```

---

## 📱 Tool Decision Matrix

| What You Want | Best Tool | Command |
|---------------|-----------|---------|
| Setup new device | jsonrpc_client.py | `python gramofon_jsonrpc_client.py configure ...` |
| Find all devices | discovery.py | `python gramofon_discovery.py --list` |
| Turn off all LEDs | discovery.py | `python gramofon_discovery.py --led-off` |
| Turn off one LED (fast) | led_control.sh | `./gramofon_led_control.sh <IP> off` |
| Turn off one LED (Python) | jsonrpc_client.py | `python gramofon_jsonrpc_client.py --ip <IP> led --off` |
| Manage multiple devices | discovery.py | `python gramofon_discovery.py` (interactive) |
| Factory reset | factory_reset.py | `python gramofon_factory_reset.py --ip <IP>` |
| Test connection | test_connection.py | `python test_gramofon_connection.py` |

---

## 🔧 Troubleshooting Quick Reference

### Can't Find Device After Configuration

```bash
# 1. Make sure device is powered on
# 2. Check if it's on your network (router DHCP list)
# 3. Scan network
python gramofon_discovery.py --network 192.168.1.0/24

# 4. Try pinging common IPs
ping 192.168.1.100
ping 192.168.1.50
```

### Device Not Responding to Commands

```bash
# 1. Test basic connection
python test_gramofon_connection.py

# 2. Try with longer timeout
python gramofon_jsonrpc_client.py --ip 192.168.1.100 --timeout 60 status

# 3. Reboot the device
python gramofon_jsonrpc_client.py --ip 192.168.1.100 system --reboot
```

### Configuration Failed

```bash
# 1. Connect to "Gramofon Configuration" WiFi
# 2. Test connection first
python test_gramofon_connection.py

# 3. Try configuration without scanning
python gramofon_jsonrpc_client.py configure "SSID" "Pass" --no-scan

# 4. If still fails, check WiFi password is correct
```

### Want to Start Over

```bash
# Factory reset the device
python gramofon_factory_reset.py --ip 192.168.1.100

# Wait 60 seconds, then reconfigure
python gramofon_jsonrpc_client.py configure "SSID" "Pass" --name "New Name"
```

---

## 💡 Pro Tips

1. **Save Device IPs**: Once you find your devices, save their IPs for faster access
   ```bash
   # Create a config file
   echo "192.168.1.100 # Living Room" >> ~/gramofon_devices.txt
   echo "192.168.1.101 # Bedroom" >> ~/gramofon_devices.txt
   ```

2. **Create Aliases**: Add to `~/.bashrc` or `~/.zshrc`
   ```bash
   alias g-led-off='python3 ~/gramofon/gramofon_discovery.py --led-off'
   alias g-led-on='python3 ~/gramofon/gramofon_discovery.py --led-on'
   alias g-find='python3 ~/gramofon/gramofon_discovery.py --list'
   ```

3. **Batch Operations**: Create a script for multiple devices
   ```bash
   #!/bin/bash
   for ip in 192.168.1.{100,101,102}; do
       ./gramofon_led_control.sh $ip off
   done
   ```

4. **Home Automation**: Integrate with Home Assistant, Node-RED, etc.
   See DISCOVERY_README.md for examples

5. **Network Scanning**: If you have many devices, save the discovered list
   ```bash
   python gramofon_discovery.py --list > my_gramofons.txt
   ```

---

## 📚 Documentation Reference

- **README.md** - Start here for setup
- **COMPLETE_API_DOCUMENTATION.md** - Full JSON-RPC API details
- **DISCOVERY_README.md** - Network management guide
- **This file** - Quick command reference

---

## 🆘 Getting Help

### Check Connection First
```bash
python test_gramofon_connection.py
```

### Verify API is Working
```bash
# Test each step manually
python gramofon_jsonrpc_client.py --ip 192.168.10.1 status
```

### Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Login failed" | Can't authenticate | Check IP, ensure device is on |
| "Connection timeout" | Can't reach device | Check network, IP address |
| "Session expired" | Session timed out | Tool will auto-retry login |
| "API Error -32002" | Session invalid | Tool will re-login automatically |

---

## ⚡ Power User Commands

```bash
# Find and turn off all LEDs in one line
python gramofon_discovery.py --led-off

# Turn off LED on specific device (fastest)
./gramofon_led_control.sh 192.168.1.100 off

# Get all device info as JSON
python gramofon_jsonrpc_client.py --ip 192.168.1.100 status | jq '.'

# Scan network and save results
python gramofon_discovery.py --list > devices_$(date +%Y%m%d).txt

# Control multiple devices in parallel
for ip in 192.168.1.{100..110}; do
    (./gramofon_led_control.sh $ip off &)
done
wait

# Auto-discover and interactive manage
python gramofon_discovery.py
```

---

**Last Updated:** 2026-01-28  
**Version:** 1.0  
**Tools:** Complete reverse-engineered JSON-RPC API implementation
