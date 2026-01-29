#!/usr/bin/env python3
"""
Gramofon Configuration & Management Tool
=========================================

Complete tool for configuring and managing Gramofon devices.

Usage:
    # Initial setup (connect to "Gramofon Configuration" network first)
    gramofon_config.py setup <SSID> <PASSWORD> [--name NAME]
    
    # Manage configured device on your network
    gramofon_config.py --ip <IP> led --off
    gramofon_config.py --ip <IP> status
    gramofon_config.py --ip <IP> reboot
"""

import requests
import json
import time
import argparse
import sys
from typing import Dict, Optional, List, Any


class GramofonAPIError(Exception):
    """Raised when the Gramofon API returns an error"""
    pass


class GramofonClient:
    """Client for interacting with Gramofon device using JSON-RPC 2.0 API."""
    
    def __init__(self, device_ip: str = "192.168.10.1", timeout: int = 30):
        """
        Initialize the Gramofon client.
        
        Args:
            device_ip: IP address of the Gramofon device
            timeout: Request timeout in seconds
        """
        self.device_ip = device_ip
        self.timeout = timeout
        self.session_id = None
        
    def _get_url(self) -> str:
        """Get the current API URL based on session state."""
        sid = self.session_id or "00000000000000000000000000000000"
        return f"http://{self.device_ip}/api/{sid}"
    
    def _call(self, module: str, method: str, params: Optional[Dict] = None) -> Any:
        """
        Make a JSON-RPC call to the device.
        
        Args:
            module: API module (e.g., 'session', 'anet', 'wifid')
            method: Method name (e.g., 'login', 'get_ssids')
            params: Method parameters as dict
            
        Returns:
            The result data from the response
            
        Raises:
            GramofonAPIError: If the API returns an error
            requests.RequestException: On network errors
        """
        url = self._get_url()
        
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
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for JSON-RPC error
            if "error" in data:
                error = data["error"]
                raise GramofonAPIError(
                    f"API Error {error.get('code')}: {error.get('message')}"
                )
            
            # Extract result
            result = data.get("result", [])
            
            # Check result status code
            if len(result) > 0:
                status_code = result[0]
                if status_code != 0:
                    raise GramofonAPIError(f"Operation failed with status code: {status_code}")
                
                # Return the actual result data (second element)
                return result[1] if len(result) > 1 else None
            
            return None
            
        except requests.exceptions.RequestException as e:
            raise GramofonAPIError(f"Network error: {e}")
    
    def login(self, username: str = "admin", password: str = "admin") -> str:
        """Authenticate and obtain a session ID."""
        result = self._call("session", "login", {
            "username": username,
            "password": password
        })
        
        if result and "sid" in result:
            self.session_id = result["sid"]
            return self.session_id
        else:
            raise GramofonAPIError("Login failed: No session ID returned")
    
    def get_status(self) -> Dict:
        """Get the current device status."""
        return self._call("anet", "status", {})
    
    def get_mac_address(self) -> str:
        """Get the device MAC address."""
        result = self._call("mfgd", "get_fonmac", {})
        return result.get("fonmac", "") if result else ""
    
    def get_device_name(self) -> str:
        """Get the device's friendly name."""
        result = self._call("anet", "get_gramofonname", {})
        return result.get("spotifyname", "") if result else ""
    
    def set_device_name(self, name: str) -> Dict:
        """Set the device's friendly name."""
        return self._call("anet", "set_gramofonname", {
            "mdnsname": name,
            "spotifyname": name
        })
    
    def get_wifi_config(self) -> Dict:
        """Get the current WiFi configuration."""
        return self._call("wifid", "get_wiface", {
            "name": "private"
        })
    
    def scan_networks(self, wait_time: int = 2) -> List[Dict]:
        """Scan for available WiFi networks."""
        # Start scan
        self._call("anet", "ssid_scan", {
            "iface": "radio"
        })
        
        # Wait for scan to complete
        time.sleep(wait_time)
        
        # Get results
        result = self._call("anet", "get_ssids", {})
        return result.get("results", []) if result else []
    
    def configure_wifi(self, ssid: str, password: str, 
                      encryption: str = "psk2",
                      device_name: Optional[str] = None,
                      disable_ap: bool = False) -> Dict:
        """Configure WiFi using the easy setup method."""
        params = {
            "netmode": "wcliclone",
            "ssid": ssid,
            "key": password,
            "encryption": encryption,
            "ap_disabled": disable_ap
        }
        
        if device_name:
            params["gramofon_name"] = device_name
        
        return self._call("anet", "doeasysetup", params)
    
    def reload_wifi(self) -> bool:
        """Reload WiFi configuration to apply changes."""
        try:
            self._call("wifid", "reload", {})
            return True
        except:
            return False
    
    def reboot(self) -> bool:
        """Reboot the device."""
        try:
            self._call("mfgd", "reboot", {})
            return True
        except:
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset device to factory defaults."""
        try:
            self._call("mfgd", "reset_defaults", {})
            return True
        except:
            return False
    
    def get_led_status(self) -> Dict:
        """Get current LED status and color."""
        return self._call("ledd", "get", {})
    
    def set_led(self, enabled: bool) -> bool:
        """Enable or disable the LED."""
        try:
            self._call("ledd", "switch", {
                "status": "enable" if enabled else "disable"
            })
            return True
        except:
            return False


def cmd_setup(args):
    """Initial device setup command"""
    client = GramofonClient(device_ip=args.ip, timeout=args.timeout)
    
    print("="*60)
    print("GRAMOFON INITIAL SETUP")
    print("="*60)
    print(f"\nMake sure you're connected to 'Gramofon Configuration' WiFi")
    print(f"Device IP: {args.ip}\n")
    
    # Step 1: Login
    try:
        print("Step 1: Logging in...")
        client.login()
        print(f"   ✓ Logged in (Session: {client.session_id})")
    except Exception as e:
        print(f"   ✗ Login failed: {e}")
        return 1
    
    # Step 2: Configure WiFi
    try:
        print(f"\nStep 2: Configuring WiFi...")
        print(f"   SSID: {args.ssid}")
        print(f"   Password: {'*' * len(args.password)}")
        if args.name:
            print(f"   Device Name: {args.name}")
        
        client.configure_wifi(
            ssid=args.ssid,
            password=args.password,
            device_name=args.name
        )
        print(f"   ✓ WiFi configuration sent")
        
        # Reload WiFi
        print(f"\nStep 3: Applying configuration...")
        if client.reload_wifi():
            print(f"   ✓ Configuration applied")
        else:
            print(f"   ⚠ Configuration may have been applied")
            
    except Exception as e:
        print(f"   ✗ Configuration failed: {e}")
        return 1
    
    # Success
    print("\n" + "="*60)
    print("✓ SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Wait 30-60 seconds for device to apply settings")
    print("2. 'Gramofon Configuration' network will disappear")
    print("3. Device will connect to your home WiFi")
    print("4. Use discovery tool to find device IP on your network:")
    print(f"   python gramofon_discovery.py\n")
    
    return 0


def cmd_status(args):
    """Get device status"""
    client = GramofonClient(device_ip=args.ip, timeout=args.timeout)
    
    try:
        client.login()
        status = client.get_status()
        print(json.dumps(status, indent=2))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_info(args):
    """Get device information"""
    client = GramofonClient(device_ip=args.ip, timeout=args.timeout)
    
    try:
        client.login()
        
        print("="*60)
        print("DEVICE INFORMATION")
        print("="*60)
        
        name = client.get_device_name()
        print(f"Name:       {name}")
        
        mac = client.get_mac_address()
        print(f"MAC:        {mac}")
        
        print(f"IP:         {args.ip}")
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_name(args):
    """Get or set device name"""
    client = GramofonClient(device_ip=args.ip, timeout=args.timeout)
    
    try:
        client.login()
        
        if args.set:
            # Set name
            client.set_device_name(args.set)
            print(f"✓ Device name set to: {args.set}")
        else:
            # Get name
            name = client.get_device_name()
            print(f"Device name: {name}")
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_wifi(args):
    """WiFi operations"""
    client = GramofonClient(device_ip=args.ip, timeout=args.timeout)
    
    try:
        client.login()
        
        if args.scan:
            # Scan networks
            print("Scanning for WiFi networks...")
            networks = client.scan_networks(wait_time=3)
            print(f"\nFound {len(networks)} networks:\n")
            
            for net in networks:
                ssid = net.get('ssid', 'Hidden')
                quality = net.get('quality', 0)
                quality_max = net.get('quality_max', 100)
                encryption = net.get('encryption', 'unknown')
                
                try:
                    strength = int((int(quality) / int(quality_max)) * 100)
                except:
                    strength = 0
                
                print(f"  {ssid:30} {strength:3}%  {encryption}")
            
        elif args.get:
            # Get WiFi config
            config = client.get_wifi_config()
            print(json.dumps(config, indent=2))
            
        elif args.set:
            # Set WiFi config
            ssid, password = args.set
            client.configure_wifi(ssid, password)
            print(f"✓ WiFi configured to: {ssid}")
            print("Reloading configuration...")
            client.reload_wifi()
            print("✓ Done")
            
        elif args.reload:
            # Reload WiFi
            if client.reload_wifi():
                print("✓ WiFi configuration reloaded")
            else:
                print("⚠ Reload may have failed")
        else:
            print("Error: No wifi action specified", file=sys.stderr)
            print("Use: --scan, --get, --set SSID PASSWORD, or --reload")
            return 1
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_led(args):
    """LED control"""
    client = GramofonClient(device_ip=args.ip, timeout=args.timeout)
    
    try:
        client.login()
        
        if args.get:
            # Get LED status
            status = client.get_led_status()
            print(json.dumps(status, indent=2))
            
        elif args.on:
            # Turn LED on
            if client.set_led(True):
                print("✓ LED turned ON")
            else:
                print("✗ Failed to turn LED on")
                return 1
                
        elif args.off:
            # Turn LED off
            if client.set_led(False):
                print("✓ LED turned OFF")
            else:
                print("✗ Failed to turn LED off")
                return 1
        else:
            print("Error: No LED action specified", file=sys.stderr)
            print("Use: --get, --on, or --off")
            return 1
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_system(args):
    """System operations"""
    client = GramofonClient(device_ip=args.ip, timeout=args.timeout)
    
    try:
        client.login()
        
        if args.reboot:
            # Reboot
            confirm = input("Reboot device? (yes/no): ")
            if confirm.lower() == 'yes':
                if client.reboot():
                    print("✓ Reboot command sent")
                else:
                    print("✗ Reboot failed")
                    return 1
            else:
                print("Cancelled")
                
        elif args.reset:
            # Factory reset
            print("WARNING: This will reset device to factory defaults!")
            print("After reset, you'll need to setup the device again.")
            confirm = input("Type 'RESET' to confirm: ")
            if confirm == 'RESET':
                if client.reset_to_defaults():
                    print("✓ Factory reset initiated")
                    print("\nDevice will reboot to factory settings.")
                    print("Wait 60 seconds, then connect to 'Gramofon Configuration' WiFi")
                    print("to setup the device again.")
                else:
                    print("✗ Reset failed")
                    return 1
            else:
                print("Cancelled")
        else:
            print("Error: No system action specified", file=sys.stderr)
            print("Use: --reboot or --reset")
            return 1
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_reset(args):
    """Factory reset command (direct access)"""
    client = GramofonClient(device_ip=args.ip, timeout=args.timeout)
    
    print("="*60)
    print("FACTORY RESET")
    print("="*60)
    print(f"\nDevice: {args.ip}")
    print("\nWARNING: This will:")
    print("  - Reset device to factory defaults")
    print("  - Erase WiFi configuration")
    print("  - Erase device name")
    print("  - Reboot the device")
    print("\nAfter reset:")
    print("  - Device will create 'Gramofon Configuration' WiFi")
    print("  - You'll need to run setup again")
    print()
    
    confirm = input("Type 'RESET' to confirm factory reset: ")
    
    if confirm != 'RESET':
        print("Cancelled")
        return 0
    
    try:
        print("\nConnecting to device...")
        client.login()
        print("✓ Connected")
        
        print("\nInitiating factory reset...")
        if client.reset_to_defaults():
            print("✓ Factory reset command sent")
            print("\n" + "="*60)
            print("Device is resetting...")
            print("="*60)
            print("\nNext steps:")
            print("1. Wait 60 seconds for device to reboot")
            print("2. Look for 'Gramofon Configuration' WiFi network")
            print("3. Connect to it")
            print("4. Run setup: python gramofon_config.py setup SSID PASSWORD")
            return 0
        else:
            print("✗ Factory reset failed")
            return 1
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_test(args):
    """Test connection to device"""
    client = GramofonClient(device_ip=args.ip, timeout=args.timeout)
    
    print("="*60)
    print("GRAMOFON CONNECTION TEST")
    print("="*60)
    print(f"\nDevice IP: {args.ip}")
    print(f"Timeout: {args.timeout} seconds\n")
    
    # Test 1: HTTP connectivity
    print("Test 1: HTTP Connection")
    try:
        response = requests.get(f"http://{args.ip}", timeout=5)
        print(f"  ✓ HTTP connection successful (Status: {response.status_code})")
    except Exception as e:
        print(f"  ✗ HTTP connection failed: {e}")
        return 1
    
    # Test 2: Login
    print("\nTest 2: Authentication")
    try:
        client.login()
        print(f"  ✓ Login successful (Session: {client.session_id})")
    except Exception as e:
        print(f"  ✗ Login failed: {e}")
        return 1
    
    # Test 3: Get status
    print("\nTest 3: API Communication")
    try:
        status = client.get_status()
        print(f"  ✓ API working (received status)")
    except Exception as e:
        print(f"  ✗ API communication failed: {e}")
        return 1
    
    # Test 4: Get device info
    print("\nTest 4: Device Information")
    try:
        name = client.get_device_name()
        mac = client.get_mac_address()
        print(f"  ✓ Name: {name}")
        print(f"  ✓ MAC:  {mac}")
    except Exception as e:
        print(f"  ⚠ Could not get device info: {e}")
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED")
    print("="*60)
    print("\nDevice is ready for management!")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Gramofon Configuration & Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initial setup (on "Gramofon Configuration" network)
  %(prog)s setup MyWiFi MyPassword --name "Living Room"
  
  # Manage device on your network
  %(prog)s --ip 192.168.1.100 led --off
  %(prog)s --ip 192.168.1.100 info
  %(prog)s --ip 192.168.1.100 system --reboot
  
  # Factory reset device
  %(prog)s --ip 192.168.1.100 reset
  
  # WiFi operations
  %(prog)s --ip 192.168.1.100 wifi --scan
  %(prog)s --ip 192.168.1.100 wifi --get
  
  # Test connection
  %(prog)s --ip 192.168.1.100 test
        """
    )
    
    parser.add_argument('--ip', default='192.168.10.1',
                       help='Device IP address (default: 192.168.10.1 for setup)')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Request timeout in seconds (default: 30)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Setup command (initial configuration)
    setup_parser = subparsers.add_parser('setup', 
                                         help='Initial device setup')
    setup_parser.add_argument('ssid', help='WiFi SSID')
    setup_parser.add_argument('password', help='WiFi password')
    setup_parser.add_argument('--name', help='Device name')
    
    # Status command
    subparsers.add_parser('status', help='Get device status')
    
    # Info command
    subparsers.add_parser('info', help='Get device information')
    
    # Name command
    name_parser = subparsers.add_parser('name', help='Get or set device name')
    name_parser.add_argument('--set', metavar='NAME', help='Set device name')
    
    # WiFi commands
    wifi_parser = subparsers.add_parser('wifi', help='WiFi operations')
    wifi_parser.add_argument('--scan', action='store_true', help='Scan for networks')
    wifi_parser.add_argument('--get', action='store_true', help='Get WiFi config')
    wifi_parser.add_argument('--set', nargs=2, metavar=('SSID', 'PASSWORD'),
                            help='Set WiFi configuration')
    wifi_parser.add_argument('--reload', action='store_true', help='Reload WiFi')
    
    # LED commands
    led_parser = subparsers.add_parser('led', help='LED control')
    led_parser.add_argument('--get', action='store_true', help='Get LED status')
    led_parser.add_argument('--on', action='store_true', help='Turn LED on')
    led_parser.add_argument('--off', action='store_true', help='Turn LED off')
    
    # System commands
    system_parser = subparsers.add_parser('system', help='System control')
    system_parser.add_argument('--reboot', action='store_true', help='Reboot device')
    system_parser.add_argument('--reset', action='store_true', 
                              help='Factory reset (requires confirmation)')
    
    # Factory reset command (direct access)
    subparsers.add_parser('reset', help='Factory reset device (guided)')
    
    # Test command
    subparsers.add_parser('test', help='Test connection to device')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handlers
    commands = {
        'setup': cmd_setup,
        'status': cmd_status,
        'info': cmd_info,
        'name': cmd_name,
        'wifi': cmd_wifi,
        'led': cmd_led,
        'system': cmd_system,
        'reset': cmd_reset,
        'test': cmd_test,
    }
    
    try:
        return commands[args.command](args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
