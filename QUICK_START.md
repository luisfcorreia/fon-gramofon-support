# Gramofon Quick Reference

## Two Essential Scripts

```
gramofon_config.py      - Configuration and management
gramofon_discovery.py   - Find devices on network
```

## Initial Setup (One Time Only)

```bash
# 1. Reset device (hold button 10+ seconds)
# 2. Connect to "Gramofon Configuration" WiFi
# 3. Run setup:

python gramofon_config.py setup "YourWiFi" "YourPassword" --name "Living Room"
```

## Daily Use

### Find Your Devices

```bash
python gramofon_discovery.py --list
```

### Turn Off LED (Most Common)

```bash
# All devices
python gramofon_discovery.py --led-off

# One device
python gramofon_config.py --ip 192.168.1.100 led --off
```

### Turn On LED

```bash
# All devices
python gramofon_discovery.py --led-on

# One device
python gramofon_config.py --ip 192.168.1.100 led --on
```

## All Commands for One Device

Replace `192.168.1.100` with your device's IP:

```bash
# Information
python gramofon_config.py --ip 192.168.1.100 info
python gramofon_config.py --ip 192.168.1.100 status

# LED Control
python gramofon_config.py --ip 192.168.1.100 led --off
python gramofon_config.py --ip 192.168.1.100 led --on
python gramofon_config.py --ip 192.168.1.100 led --get

# Device Name
python gramofon_config.py --ip 192.168.1.100 name
python gramofon_config.py --ip 192.168.1.100 name --set "NewName"

# WiFi
python gramofon_config.py --ip 192.168.1.100 wifi --scan
python gramofon_config.py --ip 192.168.1.100 wifi --get

# System
python gramofon_config.py --ip 192.168.1.100 system --reboot
python gramofon_config.py --ip 192.168.1.100 test

# Factory Reset
python gramofon_config.py --ip 192.168.1.100 reset
```

## Factory Reset

Reset device to factory defaults (erases all configuration):

```bash
python gramofon_config.py --ip 192.168.1.100 reset
```

**What happens:**
- Erases WiFi configuration
- Erases device name
- Device reboots to factory settings
- Creates "Gramofon Configuration" WiFi network

**After reset:**
1. Wait 60 seconds for reboot
2. Connect to "Gramofon Configuration" WiFi
3. Run setup: `python gramofon_config.py setup SSID PASSWORD`

## Discovery Tool Commands

```bash
# Interactive menu
python gramofon_discovery.py

# List all devices
python gramofon_discovery.py --list

# LED control (all devices)
python gramofon_discovery.py --led-off
python gramofon_discovery.py --led-on

# Specific network
python gramofon_discovery.py --network 192.168.1.0/24

# Check specific IP
python gramofon_discovery.py --ip 192.168.1.100
```

## Installation

```bash
pip install requests
chmod +x gramofon_config.py gramofon_discovery.py
```

## Troubleshooting

### Can't find "Gramofon Configuration" network
- Hold reset button 10+ seconds
- Wait 30-60 seconds
- Check WiFi list again

### Setup fails
- Make sure you're connected to "Gramofon Configuration"
- Test: `ping 192.168.10.1`

### Discovery finds nothing
- Try specific network: `python gramofon_discovery.py --network 192.168.1.0/24`
- Check devices are on and connected

### Commands timeout
- Add `--timeout 60` to command
- Check device is on and connected

## Automation Examples

### Cron (turn off LED at 10 PM)
```bash
crontab -e
# Add:
0 22 * * * python3 /path/to/gramofon_discovery.py --led-off
```

### Shell Script (multiple devices)
```bash
#!/bin/bash
for ip in 192.168.1.50 192.168.1.51 192.168.1.52; do
    python gramofon_config.py --ip $ip led --off
done
```

## Help

```bash
python gramofon_config.py --help
python gramofon_discovery.py --help
```

---

**Most Common Task**: Turn off all device LEDs
```bash
python gramofon_discovery.py --led-off
```
