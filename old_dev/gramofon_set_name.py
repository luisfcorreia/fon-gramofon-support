#!/usr/bin/env python3
"""
Gramofon Device Name Tool
==========================

Set or get the friendly name of your Gramofon device.
Works with both newly configured devices and devices already on your network.
"""

import sys
import requests
import json
import argparse
from typing import Optional


def jsonrpc_call(ip: str, sid: str, module: str, method: str, params: dict, timeout: int = 10):
    """Make a JSON-RPC call"""
    url = f"http://{ip}/api/{sid}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "call",
        "params": [module, method, params]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        data = response.json()
        
        if "error" in data:
            return None, data["error"]
        
        result = data.get("result", [])
        if len(result) > 0 and result[0] == 0:
            return (result[1] if len(result) > 1 else {}), None
        
        return None, {"message": "API returned error"}
    except Exception as e:
        return None, {"message": str(e)}


def login(ip: str, timeout: int = 10) -> Optional[str]:
    """Login and get session ID"""
    result, error = jsonrpc_call(
        ip, "00000000000000000000000000000000",
        "session", "login",
        {"username": "admin", "password": "admin"},
        timeout
    )
    
    if result and "sid" in result:
        return result["sid"]
    return None


def get_name(ip: str, sid: str, timeout: int = 10) -> Optional[str]:
    """Get current device name"""
    result, error = jsonrpc_call(ip, sid, "anet", "get_gramofonname", {}, timeout)
    
    if result:
        return result.get("spotifyname", "Unknown")
    return None


def set_name(ip: str, sid: str, name: str, timeout: int = 10) -> bool:
    """Set device name"""
    params = {
        "mdnsname": name,
        "spotifyname": name
    }
    
    result, error = jsonrpc_call(ip, sid, "anet", "set_gramofonname", params, timeout)
    return result is not None


def main():
    parser = argparse.ArgumentParser(
        description='Get or set Gramofon device name',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get current name
  %(prog)s --ip 192.168.1.100
  
  # Set new name
  %(prog)s --ip 192.168.1.100 --set "Living Room"
  
  # Set name during initial setup (connected to "Gramofon Configuration")
  %(prog)s --ip 192.168.10.1 --set "Kitchen"
        """
    )
    
    parser.add_argument('--ip', '-i', required=True,
                       help='IP address of the Gramofon device')
    parser.add_argument('--set', '-s', metavar='NAME',
                       help='Set device name to this value')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Connection timeout in seconds (default: 10)')
    
    args = parser.parse_args()
    
    # Login
    print(f"Connecting to {args.ip}...")
    sid = login(args.ip, args.timeout)
    
    if not sid:
        print("✗ Failed to connect to device")
        print("\nTroubleshooting:")
        print("  - Check device is powered on")
        print("  - Verify IP address is correct")
        print("  - Ensure device is on the network")
        return 1
    
    print(f"✓ Connected (Session: {sid[:16]}...)")
    print()
    
    # Set or get name
    if args.set:
        # Set name
        print(f"Setting device name to: {args.set}")
        
        if set_name(args.ip, sid, args.set, args.timeout):
            print("✓ Device name set successfully!")
            print()
            
            # Verify
            print("Verifying...")
            new_name = get_name(args.ip, sid, args.timeout)
            if new_name == args.set:
                print(f"✓ Confirmed: Device name is now '{new_name}'")
            else:
                print(f"⚠ Warning: Device reports name as '{new_name}'")
                print("  Name may take a moment to update, or device may need reboot")
        else:
            print("✗ Failed to set device name")
            print("\nPossible reasons:")
            print("  - Device may be rebooting")
            print("  - Name may contain invalid characters")
            print("  - Try again in a few seconds")
            return 1
    else:
        # Get name
        print("Getting current device name...")
        name = get_name(args.ip, sid, args.timeout)
        
        if name:
            print(f"\nDevice name: {name}")
        else:
            print("✗ Failed to get device name")
            return 1
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
