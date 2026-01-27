#!/usr/bin/env python3
"""
Gramofon Device API Client
A Python client for configuring Gramofon devices via their HTTP API.

This client was created through reverse engineering of the Gramofon Setup APK
to enable configuration of these devices on modern Android versions (14+) where
the original app no longer works.
"""

import requests
import json
import argparse
from typing import Dict, Optional, List


class GramofonClient:
    """Client for interacting with Gramofon device API."""
    
    def __init__(self, device_ip: str = "192.168.10.1", session_id: str = "00000000000000000000000000000000", timeout: int = 10):
        """
        Initialize the Gramofon client.
        
        Args:
            device_ip: IP address of the Gramofon device (default: 192.168.10.1)
            session_id: Session ID for API calls (default: 32 zeros)
            timeout: Request timeout in seconds
        """
        self.device_ip = device_ip
        self.session_id = session_id
        self.timeout = timeout
        self.base_url = f"http://{device_ip}/api/{session_id}"
        
    def _get(self, endpoint: str) -> Dict:
        """Make a GET request to the device."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making GET request to {endpoint}: {e}")
            return {"error": str(e)}
    
    def _post(self, endpoint: str, data: Dict) -> Dict:
        """Make a POST request to the device."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making POST request to {endpoint}: {e}")
            return {"error": str(e)}
    
    def get_status(self) -> Dict:
        """Get the current device status."""
        return self._get("status")
    
    def get_firmware_version(self) -> Dict:
        """Get the current firmware version."""
        return self._get("get_fw_version")
    
    def get_mac_address(self) -> Dict:
        """Get the device MAC address."""
        return self._get("get_fonmac")
    
    def get_device_name(self) -> Dict:
        """Get the device's friendly name."""
        return self._get("get_gramofonname")
    
    def set_device_name(self, name: str) -> Dict:
        """
        Set the device's friendly name.
        
        Args:
            name: The new device name
        """
        return self._post("set_gramofonname", {"gramofon_name": name})
    
    def get_wifi_config(self) -> Dict:
        """Get the current WiFi configuration."""
        return self._get("get_wiface")
    
    def scan_networks(self) -> Dict:
        """Scan for available WiFi networks."""
        return self._get("get_ssids")
    
    def set_wifi_config(self, ssid: str, password: str, **kwargs) -> Dict:
        """
        Configure WiFi settings.
        
        Args:
            ssid: WiFi network name
            password: WiFi network password
            **kwargs: Additional configuration parameters
        """
        data = {
            "ssid": ssid,
            "password": password,
            **kwargs
        }
        return self._post("set_wiface", data)
    
    def check_upgrades(self) -> Dict:
        """Check for available firmware upgrades."""
        return self._get("check_upgrades")
    
    def check_adapters(self) -> Dict:
        """Check available network adapters."""
        return self._get("check_adapters")
    
    def check_packages(self) -> Dict:
        """Check installed packages."""
        return self._get("check_packages")
    
    def check_validation(self) -> Dict:
        """Validate the current configuration."""
        return self._get("check_validation")
    
    def configure_device(self, ssid: str, password: str, device_name: Optional[str] = None) -> Dict:
        """
        Complete device configuration workflow.
        
        Args:
            ssid: WiFi network name
            password: WiFi password
            device_name: Optional friendly name for the device
        
        Returns:
            Dict with configuration results
        """
        results = {}
        
        # Get initial status
        print("Getting device status...")
        results['initial_status'] = self.get_status()
        
        # Scan for networks
        print("Scanning for WiFi networks...")
        results['available_networks'] = self.scan_networks()
        
        # Configure WiFi
        print(f"Configuring WiFi (SSID: {ssid})...")
        results['wifi_config'] = self.set_wifi_config(ssid, password)
        
        # Set device name if provided
        if device_name:
            print(f"Setting device name to: {device_name}")
            results['device_name'] = self.set_device_name(device_name)
        
        # Validate configuration
        print("Validating configuration...")
        results['validation'] = self.check_validation()
        
        # Get final status
        print("Getting final status...")
        results['final_status'] = self.get_status()
        
        return results


def main():
    """Command-line interface for the Gramofon client."""
    parser = argparse.ArgumentParser(description='Gramofon Device Configuration Tool')
    parser.add_argument('--ip', default='192.168.10.1', help='Device IP address')
    parser.add_argument('--session', default='00000000000000000000000000000000', help='Session ID')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Status command
    subparsers.add_parser('status', help='Get device status')
    
    # Firmware version command
    subparsers.add_parser('version', help='Get firmware version')
    
    # MAC address command
    subparsers.add_parser('mac', help='Get MAC address')
    
    # Device name commands
    name_parser = subparsers.add_parser('name', help='Get or set device name')
    name_parser.add_argument('--set', metavar='NAME', help='Set device name')
    
    # WiFi commands
    wifi_parser = subparsers.add_parser('wifi', help='WiFi configuration')
    wifi_parser.add_argument('--scan', action='store_true', help='Scan for networks')
    wifi_parser.add_argument('--get', action='store_true', help='Get current WiFi config')
    wifi_parser.add_argument('--set', nargs=2, metavar=('SSID', 'PASSWORD'), help='Configure WiFi')
    
    # Upgrade command
    subparsers.add_parser('upgrades', help='Check for firmware upgrades')
    
    # Complete configuration
    config_parser = subparsers.add_parser('configure', help='Complete device setup')
    config_parser.add_argument('ssid', help='WiFi SSID')
    config_parser.add_argument('password', help='WiFi password')
    config_parser.add_argument('--name', help='Device name')
    
    args = parser.parse_args()
    
    # Create client
    client = GramofonClient(device_ip=args.ip, session_id=args.session)
    
    # Execute command
    result = None
    
    if args.command == 'status':
        result = client.get_status()
    
    elif args.command == 'version':
        result = client.get_firmware_version()
    
    elif args.command == 'mac':
        result = client.get_mac_address()
    
    elif args.command == 'name':
        if args.set:
            result = client.set_device_name(args.set)
        else:
            result = client.get_device_name()
    
    elif args.command == 'wifi':
        if args.scan:
            result = client.scan_networks()
        elif args.get:
            result = client.get_wifi_config()
        elif args.set:
            result = client.set_wifi_config(args.set[0], args.set[1])
        else:
            print("Please specify --scan, --get, or --set")
            return
    
    elif args.command == 'upgrades':
        result = client.check_upgrades()
    
    elif args.command == 'configure':
        result = client.configure_device(args.ssid, args.password, args.name)
    
    else:
        parser.print_help()
        return
    
    # Print result
    if result:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
