#!/usr/bin/env python3
"""
Gramofon Factory Reset Tool
============================

Safely resets Gramofon devices to factory defaults with double confirmation.
This will erase all configuration and the device will create "Gramofon Configuration"
WiFi network again.

WARNING: This cannot be undone!
"""

import sys
import requests
import json
import argparse
import time
from typing import Optional


class GramofonReset:
    """Handle factory reset operations"""
    
    def __init__(self, ip: str, timeout: int = 30):
        self.ip = ip
        self.timeout = timeout
        self.session_id = None
        self.device_name = None
        self.device_mac = None
    
    def _call(self, module: str, method: str, params: Optional[dict] = None):
        """Make a JSON-RPC call"""
        sid = self.session_id or "00000000000000000000000000000000"
        url = f"http://{self.ip}/api/{sid}"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [module, method, params or {}]
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            data = response.json()
            
            if "error" in data:
                return None
            
            result = data.get("result", [])
            if len(result) > 0 and result[0] == 0:
                return result[1] if len(result) > 1 else {}
            
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def login(self) -> bool:
        """Authenticate with the device"""
        print(f"Connecting to {self.ip}...")
        result = self._call("session", "login", {
            "username": "admin",
            "password": "admin"
        })
        
        if result and "sid" in result:
            self.session_id = result["sid"]
            print("✓ Connected successfully")
            return True
        
        print("✗ Failed to connect")
        return False
    
    def get_device_info(self) -> bool:
        """Get device information"""
        # Get name
        result = self._call("anet", "get_gramofonname", {})
        if result:
            self.device_name = result.get("spotifyname", "Unknown")
        
        # Get MAC
        result = self._call("mfgd", "get_fonmac", {})
        if result:
            self.device_mac = result.get("fonmac", "Unknown")
        
        return self.device_name is not None
    
    def factory_reset(self) -> bool:
        """Perform factory reset"""
        result = self._call("mfgd", "reset_defaults", {})
        return result is not None


def print_warning():
    """Print warning banner"""
    print("\n" + "="*70)
    print("⚠️  WARNING: FACTORY RESET ⚠️".center(70))
    print("="*70)
    print("""
This will:
  • Erase ALL configuration from the device
  • Remove WiFi settings (device will disconnect from your network)
  • Reset device name to default
  • Create "Gramofon Configuration" WiFi network again
  • Require you to reconfigure the device from scratch

This action CANNOT BE UNDONE!
""")
    print("="*70 + "\n")


def confirm_reset(device_name: str, device_ip: str, device_mac: str) -> bool:
    """Get double confirmation from user"""
    print("Device Information:")
    print(f"  Name: {device_name}")
    print(f"  IP:   {device_ip}")
    print(f"  MAC:  {device_mac}")
    print()
    
    # First confirmation
    print("="*70)
    response1 = input("Are you SURE you want to factory reset this device? (yes/no): ").strip().lower()
    
    if response1 != "yes":
        print("\nFactory reset cancelled.")
        return False
    
    # Second confirmation with device name
    print("\n" + "="*70)
    print("⚠️  FINAL CONFIRMATION ⚠️".center(70))
    print("="*70)
    print(f"\nYou are about to factory reset: {device_name}")
    print("All settings will be permanently erased.")
    print()
    
    response2 = input(f"Type the device name '{device_name}' to confirm: ").strip()
    
    if response2 == device_name:
        print()
        return True
    else:
        print("\nDevice name doesn't match. Factory reset cancelled.")
        return False


def perform_reset(ip: str, timeout: int = 30):
    """Perform the factory reset with confirmations"""
    
    # Create reset handler
    resetter = GramofonReset(ip, timeout)
    
    # Connect to device
    if not resetter.login():
        print("\nCould not connect to device.")
        print("Make sure:")
        print("  - Device is powered on")
        print("  - Device is on the network")
        print("  - IP address is correct")
        return 1
    
    print()
    
    # Get device info
    print("Getting device information...")
    if not resetter.get_device_info():
        print("Warning: Could not retrieve device information")
        resetter.device_name = "Unknown Device"
        resetter.device_mac = "Unknown"
    
    print()
    
    # Show warning
    print_warning()
    
    # Get confirmations
    if not confirm_reset(resetter.device_name, resetter.ip, resetter.device_mac):
        return 0
    
    # Perform reset
    print("\n" + "="*70)
    print("Performing factory reset...")
    print("="*70)
    print()
    
    if resetter.factory_reset():
        print("✓ Factory reset command sent successfully!")
        print()
        print("Device is now resetting...")
        print()
        print("Next steps:")
        print("  1. Wait 30-60 seconds for device to reboot")
        print("  2. Look for 'Gramofon Configuration' WiFi network")
        print("  3. Connect to it and reconfigure the device")
        print()
        print("You can now disconnect from the current network.")
        print()
        return 0
    else:
        print("✗ Factory reset failed!")
        print("The device may not support this operation or connection was lost.")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Factory reset Gramofon device with double confirmation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
⚠️  WARNING: Factory reset will erase ALL configuration!

Examples:
  # Reset specific device
  %(prog)s --ip 192.168.1.100
  
  # Reset with longer timeout
  %(prog)s --ip 192.168.1.100 --timeout 60
  
  # Use discovered device
  python gramofon_discovery.py --list  # Find your device IP first
  %(prog)s --ip <IP_from_discovery>
        """
    )
    
    parser.add_argument('--ip', '-i', required=True,
                       help='IP address of the Gramofon device to reset')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Connection timeout in seconds (default: 30)')
    parser.add_argument('--yes', action='store_true',
                       help='Skip first confirmation (NOT RECOMMENDED - you will still need to confirm device name)')
    
    args = parser.parse_args()
    
    # If --yes flag, show warning but skip first confirmation
    if args.yes:
        print_warning()
        print("⚠️  Running with --yes flag, skipping first confirmation...")
        print("You will still need to confirm the device name.")
        print()
        
        # Still get device info for second confirmation
        resetter = GramofonReset(args.ip, args.timeout)
        if not resetter.login():
            print("Could not connect to device.")
            return 1
        
        resetter.get_device_info()
        
        # Only second confirmation
        print("="*70)
        print("⚠️  FINAL CONFIRMATION ⚠️".center(70))
        print("="*70)
        print(f"\nYou are about to factory reset: {resetter.device_name}")
        print(f"IP: {resetter.ip}")
        print(f"MAC: {resetter.device_mac}")
        print("\nAll settings will be permanently erased.")
        print()
        
        response = input(f"Type the device name '{resetter.device_name}' to confirm: ").strip()
        
        if response != resetter.device_name:
            print("\nDevice name doesn't match. Factory reset cancelled.")
            return 0
        
        print("\nPerforming factory reset...")
        if resetter.factory_reset():
            print("✓ Factory reset command sent successfully!")
            print("\nDevice is now resetting. Wait 30-60 seconds.")
            print("Look for 'Gramofon Configuration' WiFi network.")
            return 0
        else:
            print("✗ Factory reset failed!")
            return 1
    
    # Normal mode with double confirmation
    try:
        return perform_reset(args.ip, args.timeout)
    except KeyboardInterrupt:
        print("\n\nFactory reset cancelled by user.")
        return 0
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
