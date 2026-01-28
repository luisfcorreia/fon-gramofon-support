#!/usr/bin/env python3
"""
Gramofon Device API Client (JSON-RPC 2.0)
==========================================

A Python client for configuring Gramofon devices via their JSON-RPC 2.0 HTTP API.
Based on reverse engineering of the Gramofon Setup APK and verified against decompiled Java source code.

The Gramofon uses JSON-RPC 2.0, not REST! All requests are POST with JSON-RPC payloads.
"""

import requests
import json
import time
import argparse
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
            device_ip: IP address of the Gramofon device (default: 192.168.10.1)
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
        """
        Authenticate and obtain a session ID.
        
        Args:
            username: Admin username (default: "admin")
            password: Admin password (default: "admin")
            
        Returns:
            Session ID string
        """
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
        """
        Set the device's friendly name.
        
        Args:
            name: The new device name
        """
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
        """
        Scan for available WiFi networks.
        
        Args:
            wait_time: Seconds to wait for scan to complete (default: 2)
            
        Returns:
            List of network dictionaries with ssid, bssid, quality, encryption
        """
        # Start scan
        self._call("anet", "ssid_scan", {
            "iface": "radio"
        })
        
        # Wait for scan to complete
        time.sleep(wait_time)
        
        # Get results
        result = self._call("anet", "get_ssids", {})
        return result.get("results", []) if result else []
    
    def configure_wifi_simple(self, ssid: str, password: str, 
                             encryption: str = "psk2",
                             device_name: Optional[str] = None,
                             disable_ap: bool = False) -> Dict:
        """
        Configure WiFi using the easy setup method.
        
        Args:
            ssid: WiFi network name
            password: WiFi network password
            encryption: Encryption type (default: "psk2" for WPA2)
            device_name: Optional friendly name for the device
            disable_ap: Whether to disable the device's access point
            
        Returns:
            Response data
        """
        params = {
            "netmode": "wcliclone",  # WiFi client clone mode
            "ssid": ssid,
            "key": password,
            "encryption": encryption,
            "ap_disabled": disable_ap
        }
        
        if device_name:
            params["gramofon_name"] = device_name
        
        return self._call("anet", "doeasysetup", params)
    
    def configure_wifi_advanced(self, ssid: str, password: str,
                                bssid: Optional[str] = None,
                                encryption: str = "psk2",
                                device_name: Optional[str] = None,
                                disable_ap: bool = False) -> Dict:
        """
        Configure WiFi with advanced options (requires firmware >= 2.0.14 for BSSID).
        
        Args:
            ssid: WiFi network name
            password: WiFi network password  
            bssid: Access point BSSID/MAC address (optional)
            encryption: Encryption type (default: "psk2" for WPA2)
            device_name: Optional friendly name for the device
            disable_ap: Whether to disable the device's access point
            
        Returns:
            Response data
        """
        params = {
            "netmode": "wcliclone",
            "ssid": ssid,
            "key": password,
            "encryption": encryption,
            "ap_disabled": disable_ap
        }
        
        if bssid:
            params["bssid"] = bssid
        
        if device_name:
            params["gramofon_name"] = device_name
        
        return self._call("anet", "doeasysetup", params)
    
    def reload_wifi(self) -> bool:
        """
        Reload WiFi configuration to apply changes.
        
        Returns:
            True if successful
        """
        try:
            self._call("wifid", "reload", {})
            return True
        except:
            return False
    
    def check_upgrades(self) -> Dict:
        """
        Check for available firmware upgrades.
        
        Returns:
            Dictionary with 'images' array containing firmware info
        """
        return self._call("mfgd", "check_upgrades", {})
    
    def upgrade_firmware(self, firmware_id: str) -> Dict:
        """
        Apply a firmware upgrade.
        
        Args:
            firmware_id: Firmware version ID to upgrade to
        """
        return self._call("mfgd", "upgrade", {
            "firmware_id": firmware_id
        })
    
    def reboot(self) -> bool:
        """
        Reboot the device.
        
        Returns:
            True if reboot command accepted
        """
        try:
            self._call("mfgd", "reboot", {})
            return True
        except:
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset device to factory defaults.
        
        Returns:
            True if reset successful
        """
        try:
            self._call("mfgd", "reset_defaults", {})
            return True
        except:
            return False
    
    def get_led_status(self) -> Dict:
        """Get current LED status and color."""
        return self._call("ledd", "get", {})
    
    def set_led(self, enabled: bool) -> Dict:
        """
        Enable or disable the LED.
        
        Args:
            enabled: True to enable, False to disable
        """
        return self._call("ledd", "switch", {
            "status": "enable" if enabled else "disable"
        })
    
    def configure_device(self, ssid: str, password: str, 
                        device_name: Optional[str] = None,
                        scan_first: bool = False) -> Dict:
        """
        Complete device configuration workflow.
        
        Args:
            ssid: WiFi network name
            password: WiFi password
            device_name: Optional friendly name for the device
            scan_first: Whether to scan for networks first (default: False)
        
        Returns:
            Dict with configuration results
        """
        results = {
            'success': False,
            'steps_completed': []
        }
        
        try:
            # Step 1: Login
            print("1. Logging in...")
            self.login()
            print(f"   ✓ Logged in (Session ID: {self.session_id})")
            results['steps_completed'].append('login')
            results['session_id'] = self.session_id
            
        except Exception as e:
            print(f"   ✗ Login failed: {e}")
            results['error'] = f"Login failed: {e}"
            return results
        
        # Step 2: Optional network scan
        if scan_first:
            try:
                print("\n2. Scanning for WiFi networks...")
                networks = self.scan_networks(wait_time=3)
                print(f"   ✓ Found {len(networks)} networks")
                results['steps_completed'].append('scan')
                
                # Check if target network is visible
                target = next((n for n in networks if n.get('ssid') == ssid), None)
                if target:
                    print(f"   ✓ Target network '{ssid}' found")
                    print(f"      Encryption: {target.get('encryption', 'unknown')}")
                else:
                    print(f"   ⚠ Warning: Target network '{ssid}' not found in scan")
                    print(f"      (This may be OK if network is hidden)")
            except Exception as e:
                print(f"   ⚠ Network scan failed: {e}")
                print(f"      Continuing with configuration anyway...")
        
        # Step 3: Configure WiFi (the critical step)
        try:
            step_num = 3 if scan_first else 2
            print(f"\n{step_num}. Configuring WiFi...")
            print(f"   SSID: {ssid}")
            print(f"   Password: {'*' * len(password)}")
            if device_name:
                print(f"   Device Name: {device_name}")
            
            result = self.configure_wifi_simple(
                ssid=ssid,
                password=password,
                device_name=device_name
            )
            print(f"   ✓ WiFi configuration sent successfully")
            results['steps_completed'].append('wifi_config')
            results['wifi_result'] = result
            
        except Exception as e:
            print(f"   ✗ WiFi configuration failed: {e}")
            results['error'] = f"WiFi configuration failed: {e}"
            return results
        
        # Step 4: Reload WiFi
        try:
            step_num += 1
            print(f"\n{step_num}. Reloading WiFi configuration...")
            if self.reload_wifi():
                print(f"   ✓ WiFi configuration reloaded")
                results['steps_completed'].append('wifi_reload')
            else:
                print(f"   ⚠ WiFi reload returned no confirmation")
                print(f"      Configuration may still have been applied")
        except Exception as e:
            print(f"   ⚠ WiFi reload error: {e}")
            print(f"      Configuration may still have been applied")
        
        # Success!
        results['success'] = True
        print("\n" + "="*60)
        print("✓ Configuration Complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Wait 30-60 seconds for the device to apply settings")
        print("2. The 'Gramofon Configuration' network will disappear")
        print("3. Your Gramofon should connect to your home WiFi")
        print("4. You may need to find the device's new IP on your network")
        
        return results


def main():
    """Command-line interface for the Gramofon client."""
    parser = argparse.ArgumentParser(
        description='Gramofon Device Configuration Tool (JSON-RPC)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                          # Get device status
  %(prog)s scan                            # Scan for WiFi networks
  %(prog)s wifi --set MyNetwork MyPass     # Configure WiFi
  %(prog)s configure MyNetwork MyPass --name "Living Room"  # Complete setup
        """
    )
    parser.add_argument('--ip', default='192.168.10.1', 
                       help='Device IP address (default: 192.168.10.1)')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Request timeout in seconds (default: 30)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Status command
    subparsers.add_parser('status', help='Get device status')
    
    # MAC address command
    subparsers.add_parser('mac', help='Get MAC address')
    
    # Device name commands
    name_parser = subparsers.add_parser('name', help='Get or set device name')
    name_parser.add_argument('--set', metavar='NAME', help='Set device name')
    
    # WiFi commands
    wifi_parser = subparsers.add_parser('wifi', help='WiFi configuration')
    wifi_parser.add_argument('--scan', action='store_true', help='Scan for networks')
    wifi_parser.add_argument('--get', action='store_true', help='Get current WiFi config')
    wifi_parser.add_argument('--set', nargs=2, metavar=('SSID', 'PASSWORD'), 
                            help='Configure WiFi')
    wifi_parser.add_argument('--reload', action='store_true', help='Reload WiFi configuration')
    
    # LED commands
    led_parser = subparsers.add_parser('led', help='LED control')
    led_parser.add_argument('--get', action='store_true', help='Get LED status')
    led_parser.add_argument('--on', action='store_true', help='Turn LED on')
    led_parser.add_argument('--off', action='store_true', help='Turn LED off')
    
    # Upgrade commands
    upgrade_parser = subparsers.add_parser('upgrade', help='Firmware management')
    upgrade_parser.add_argument('--check', action='store_true', help='Check for upgrades')
    upgrade_parser.add_argument('--apply', metavar='FIRMWARE_ID', help='Apply firmware upgrade')
    
    # System commands
    system_parser = subparsers.add_parser('system', help='System control')
    system_parser.add_argument('--reboot', action='store_true', help='Reboot device')
    system_parser.add_argument('--reset', action='store_true', help='Factory reset')
    
    # Complete configuration
    config_parser = subparsers.add_parser('configure', help='Complete device setup')
    config_parser.add_argument('ssid', help='WiFi SSID')
    config_parser.add_argument('password', help='WiFi password')
    config_parser.add_argument('--name', help='Device name')
    config_parser.add_argument('--no-scan', action='store_true', help='Skip network scan')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create client
    client = GramofonClient(device_ip=args.ip, timeout=args.timeout)
    
    # Execute command
    try:
        result = None
        
        # Login is required for most commands
        if args.command != 'configure':
            print("Logging in...")
            client.login()
            print(f"Logged in successfully (SID: {client.session_id})\n")
        
        if args.command == 'status':
            result = client.get_status()
        
        elif args.command == 'mac':
            mac = client.get_mac_address()
            print(f"MAC Address: {mac}")
            return
        
        elif args.command == 'name':
            if args.set:
                result = client.set_device_name(args.set)
                print(f"Device name set to: {args.set}")
            else:
                name = client.get_device_name()
                print(f"Device name: {name}")
                return
        
        elif args.command == 'wifi':
            if args.scan:
                networks = client.scan_networks()
                print(f"Found {len(networks)} networks:\n")
                for net in networks:
                    ssid = net.get('ssid', 'Hidden')
                    quality = net.get('quality', 0)
                    quality_max = net.get('quality_max', 100)
                    encryption = net.get('encryption', 'unknown')
                    strength = int((int(quality) / int(quality_max)) * 100) if quality_max else 0
                    print(f"  {ssid:30} {strength:3}%  {encryption}")
                return
            elif args.get:
                result = client.get_wifi_config()
            elif args.set:
                result = client.configure_wifi_simple(args.set[0], args.set[1])
                print(f"WiFi configured. Reloading...")
                client.reload_wifi()
            elif args.reload:
                if client.reload_wifi():
                    print("WiFi configuration reloaded")
                return
            else:
                wifi_parser.print_help()
                return
        
        elif args.command == 'led':
            if args.get:
                result = client.get_led_status()
            elif args.on:
                result = client.set_led(True)
                print("LED turned on")
            elif args.off:
                result = client.set_led(False)
                print("LED turned off")
            else:
                led_parser.print_help()
                return
        
        elif args.command == 'upgrade':
            if args.check:
                result = client.check_upgrades()
                if result and 'images' in result:
                    images = result['images']
                    if images:
                        print(f"Available upgrades:")
                        for img in images:
                            print(f"  - {img.get('firmware_id')}: {img.get('user_message')}")
                    else:
                        print("No upgrades available")
                return
            elif args.apply:
                result = client.upgrade_firmware(args.apply)
                print(f"Firmware upgrade initiated: {args.apply}")
            else:
                upgrade_parser.print_help()
                return
        
        elif args.command == 'system':
            if args.reboot:
                if client.reboot():
                    print("Reboot command sent")
                return
            elif args.reset:
                if client.reset_to_defaults():
                    print("Factory reset initiated")
                return
            else:
                system_parser.print_help()
                return
        
        elif args.command == 'configure':
            result = client.configure_device(
                ssid=args.ssid,
                password=args.password,
                device_name=args.name,
                scan_first=not args.no_scan
            )
        
        # Print result if any
        if result:
            print("\nResponse:")
            print(json.dumps(result, indent=2))
            
    except GramofonAPIError as e:
        print(f"\n❌ API Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main() or 0)
