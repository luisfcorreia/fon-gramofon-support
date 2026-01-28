#!/usr/bin/env python3
"""
Gramofon Network Discovery Tool
================================

Discovers Gramofon devices on your local network and allows you to manage them.
The device keeps the same JSON-RPC API after configuration, just accessible via
your home network instead of the setup network.
"""

import socket
import subprocess
import ipaddress
import concurrent.futures
import requests
import json
import argparse
from typing import List, Dict, Optional, Tuple
import sys


class GramofonDevice:
    """Represents a discovered Gramofon device"""
    
    def __init__(self, ip: str, session_id: Optional[str] = None):
        self.ip = ip
        self.session_id = session_id
        self.name = None
        self.mac = None
        self.status = None
        
    def __str__(self):
        return f"Gramofon at {self.ip} ({self.name or 'Unknown'})"
    
    def _call(self, module: str, method: str, params: Optional[Dict] = None, timeout: int = 5):
        """Make a JSON-RPC call to the device"""
        sid = self.session_id or "00000000000000000000000000000000"
        url = f"http://{self.ip}/api/{sid}"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [module, method, params or {}]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            data = response.json()
            
            if "error" in data:
                return None
            
            result = data.get("result", [])
            if len(result) > 0 and result[0] == 0:
                return result[1] if len(result) > 1 else {}
            
            return None
        except:
            return None
    
    def login(self, username: str = "admin", password: str = "admin") -> bool:
        """Authenticate with the device"""
        result = self._call("session", "login", {
            "username": username,
            "password": password
        })
        
        if result and "sid" in result:
            self.session_id = result["sid"]
            return True
        return False
    
    def get_info(self) -> bool:
        """Fetch device information"""
        # Get name
        result = self._call("anet", "get_gramofonname", {})
        if result:
            self.name = result.get("spotifyname", "Unknown")
        
        # Get MAC
        result = self._call("mfgd", "get_fonmac", {})
        if result:
            self.mac = result.get("fonmac", "Unknown")
        
        return self.name is not None
    
    def get_led_status(self) -> Dict:
        """Get LED status"""
        return self._call("ledd", "get", {})
    
    def set_led(self, enabled: bool) -> bool:
        """Turn LED on or off"""
        result = self._call("ledd", "switch", {
            "status": "enable" if enabled else "disable"
        })
        return result is not None
    
    def get_status(self) -> Dict:
        """Get device status"""
        return self._call("anet", "status", {})
    
    def reboot(self) -> bool:
        """Reboot the device"""
        result = self._call("mfgd", "reboot", {})
        return result is not None


def check_ip_is_gramofon(ip: str, timeout: int = 2) -> Optional[GramofonDevice]:
    """Check if an IP address is a Gramofon device"""
    try:
        # Try to connect to the Gramofon API
        device = GramofonDevice(ip)
        
        # Attempt login
        if device.login():
            # Try to get device info
            if device.get_info():
                return device
    except:
        pass
    
    return None


def get_local_network() -> str:
    """Get the local network CIDR"""
    try:
        # Get default gateway
        if sys.platform == "darwin":  # macOS
            result = subprocess.run(['route', '-n', 'get', 'default'], 
                                  capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if 'interface:' in line:
                    iface = line.split(':')[1].strip()
                    # Get IP for this interface
                    result = subprocess.run(['ifconfig', iface], 
                                          capture_output=True, text=True, timeout=5)
                    for line in result.stdout.split('\n'):
                        if 'inet ' in line and '127.0.0.1' not in line:
                            parts = line.split()
                            ip = parts[1]
                            netmask = parts[3]
                            # Convert netmask to CIDR
                            return f"{ip}/24"  # Assuming /24 for simplicity
        else:  # Linux
            result = subprocess.run(['ip', 'route', 'show', 'default'], 
                                  capture_output=True, text=True, timeout=5)
            iface = result.stdout.split('dev')[1].split()[0]
            
            result = subprocess.run(['ip', 'addr', 'show', iface], 
                                  capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if 'inet ' in line and '127.0.0.1' not in line:
                    ip_cidr = line.split()[1]
                    return ip_cidr
    except:
        pass
    
    # Fallback: ask user for their network
    return None


def scan_network(network: str, max_workers: int = 50) -> List[GramofonDevice]:
    """Scan a network for Gramofon devices"""
    try:
        net = ipaddress.ip_network(network, strict=False)
    except ValueError as e:
        print(f"Error: Invalid network: {e}")
        return []
    
    print(f"Scanning network {network}...")
    print(f"This will check up to {net.num_addresses} addresses...")
    print("(This may take 1-2 minutes)\n")
    
    devices = []
    checked = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all IPs to be checked
        future_to_ip = {
            executor.submit(check_ip_is_gramofon, str(ip)): str(ip) 
            for ip in net.hosts()
        }
        
        for future in concurrent.futures.as_completed(future_to_ip):
            checked += 1
            if checked % 50 == 0:
                print(f"  Checked {checked}/{net.num_addresses} addresses...", end='\r')
            
            device = future.result()
            if device:
                devices.append(device)
                print(f"\n  ✓ Found Gramofon at {device.ip} ({device.name})")
    
    print(f"\nScan complete. Found {len(devices)} device(s).\n")
    return devices


def interactive_menu(devices: List[GramofonDevice]):
    """Interactive menu for managing discovered devices"""
    if not devices:
        print("No devices found.")
        return
    
    while True:
        print("\n" + "="*60)
        print("GRAMOFON DEVICES")
        print("="*60)
        
        for i, device in enumerate(devices, 1):
            print(f"{i}. {device.ip:15} - {device.name or 'Unknown':20} ({device.mac})")
        
        print("\nActions:")
        print("  [number] - Select device")
        print("  r - Rescan network")
        print("  q - Quit")
        
        choice = input("\nChoice: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 'r':
            print("\nRescanning...")
            network = get_local_network()
            if network:
                devices.clear()
                devices.extend(scan_network(network))
            continue
        
        try:
            device_num = int(choice)
            if 1 <= device_num <= len(devices):
                device_menu(devices[device_num - 1])
        except ValueError:
            print("Invalid choice")


def device_menu(device: GramofonDevice):
    """Menu for a specific device"""
    while True:
        print("\n" + "="*60)
        print(f"DEVICE: {device.name} ({device.ip})")
        print("="*60)
        
        print("\n1. Get LED status")
        print("2. Turn LED ON")
        print("3. Turn LED OFF")
        print("4. Get device status")
        print("5. Get device info")
        print("6. Reboot device")
        print("b. Back to device list")
        
        choice = input("\nChoice: ").strip().lower()
        
        if choice == 'b':
            break
        elif choice == '1':
            print("\nGetting LED status...")
            status = device.get_led_status()
            if status:
                print(f"LED Status: {json.dumps(status, indent=2)}")
            else:
                print("Failed to get LED status")
        elif choice == '2':
            print("\nTurning LED ON...")
            if device.set_led(True):
                print("✓ LED turned ON")
            else:
                print("✗ Failed to turn LED on")
        elif choice == '3':
            print("\nTurning LED OFF...")
            if device.set_led(False):
                print("✓ LED turned OFF")
            else:
                print("✗ Failed to turn LED off")
        elif choice == '4':
            print("\nGetting device status...")
            status = device.get_status()
            if status:
                print(f"Status: {json.dumps(status, indent=2)}")
            else:
                print("Failed to get status")
        elif choice == '5':
            print("\nGetting device info...")
            if device.get_info():
                print(f"Name: {device.name}")
                print(f"MAC: {device.mac}")
                print(f"IP: {device.ip}")
            else:
                print("Failed to get device info")
        elif choice == '6':
            confirm = input("\nAre you sure you want to reboot? (yes/no): ")
            if confirm.lower() == 'yes':
                print("Rebooting device...")
                if device.reboot():
                    print("✓ Reboot command sent")
                else:
                    print("✗ Failed to reboot")
        
        input("\nPress Enter to continue...")


def main():
    parser = argparse.ArgumentParser(
        description='Discover and manage Gramofon devices on your network',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect network and scan
  %(prog)s
  
  # Scan specific network
  %(prog)s --network 192.168.1.0/24
  
  # Scan and turn off LED on all devices
  %(prog)s --led-off
  
  # Scan specific IP
  %(prog)s --ip 192.168.1.100 --led-off
        """
    )
    
    parser.add_argument('--network', '-n', 
                       help='Network to scan (e.g., 192.168.1.0/24)')
    parser.add_argument('--ip', '-i',
                       help='Specific IP to check/manage')
    parser.add_argument('--led-on', action='store_true',
                       help='Turn LED on for all found devices')
    parser.add_argument('--led-off', action='store_true',
                       help='Turn LED off for all found devices')
    parser.add_argument('--list', action='store_true',
                       help='Just list devices and exit')
    parser.add_argument('--timeout', type=int, default=2,
                       help='Connection timeout per device (default: 2s)')
    
    args = parser.parse_args()
    
    devices = []
    
    # Specific IP mode
    if args.ip:
        print(f"Checking {args.ip}...")
        device = check_ip_is_gramofon(args.ip, args.timeout)
        if device:
            print(f"✓ Found Gramofon at {device.ip} ({device.name})")
            devices.append(device)
        else:
            print(f"✗ No Gramofon found at {args.ip}")
            return 1
    
    # Network scan mode
    else:
        network = args.network
        
        if not network:
            network = get_local_network()
            if not network:
                print("Could not auto-detect network.")
                network = input("Enter network to scan (e.g., 192.168.1.0/24): ").strip()
                if not network:
                    print("No network specified. Exiting.")
                    return 1
        
        devices = scan_network(network)
    
    if not devices:
        print("\nNo Gramofon devices found on the network.")
        print("\nTroubleshooting:")
        print("  - Make sure devices are powered on")
        print("  - Verify they're connected to your WiFi")
        print("  - Check they're on the same network as this computer")
        print("  - Try specifying network manually with --network")
        return 1
    
    # Execute actions if specified
    if args.led_on:
        print("\nTurning LED ON for all devices...")
        for device in devices:
            if device.set_led(True):
                print(f"  ✓ {device.ip} ({device.name})")
            else:
                print(f"  ✗ {device.ip} ({device.name}) - Failed")
        return 0
    
    if args.led_off:
        print("\nTurning LED OFF for all devices...")
        for device in devices:
            if device.set_led(False):
                print(f"  ✓ {device.ip} ({device.name})")
            else:
                print(f"  ✗ {device.ip} ({device.name}) - Failed")
        return 0
    
    if args.list:
        print("\nDiscovered Gramofon Devices:")
        print("-" * 60)
        for device in devices:
            print(f"  {device.ip:15} - {device.name:20} ({device.mac})")
        return 0
    
    # Interactive mode
    try:
        interactive_menu(devices)
    except KeyboardInterrupt:
        print("\n\nExiting...")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
