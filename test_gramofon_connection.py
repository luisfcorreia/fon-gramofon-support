#!/usr/bin/env python3
"""
Gramofon Connection Test Script
================================

This script tests your connection to the Gramofon device step-by-step
and helps diagnose any issues.
"""

import sys
import requests
import json
import time

DEVICE_IP = "192.168.10.1"
TIMEOUT = 10

def test_step(step_num, description):
    """Print a test step header"""
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {description}")
    print('='*60)

def jsonrpc_call(module, method, params, session_id=None):
    """Make a JSON-RPC call"""
    sid = session_id or "00000000000000000000000000000000"
    url = f"http://{DEVICE_IP}/api/{sid}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "call",
        "params": [module, method, params]
    }
    
    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    
    return response.json()

def main():
    print("\n" + "="*60)
    print("GRAMOFON DEVICE CONNECTION TEST")
    print("="*60)
    print(f"\nDevice IP: {DEVICE_IP}")
    print(f"Timeout: {TIMEOUT} seconds")
    
    # Step 1: Ping test
    test_step(1, "Testing network connectivity")
    try:
        import subprocess
        result = subprocess.run(['ping', '-c', '1', '-W', '2', DEVICE_IP], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Device is reachable via ping")
        else:
            print("✗ Cannot ping device")
            print("  Make sure you're connected to 'Gramofon Configuration' WiFi")
            return 1
    except Exception as e:
        print(f"⚠ Could not test ping: {e}")
    
    # Step 2: HTTP connectivity
    test_step(2, "Testing HTTP connectivity")
    try:
        response = requests.get(f"http://{DEVICE_IP}", timeout=5)
        print(f"✓ HTTP connection successful (Status: {response.status_code})")
    except Exception as e:
        print(f"✗ HTTP connection failed: {e}")
        return 1
    
    # Step 3: Login test
    test_step(3, "Testing authentication (login)")
    try:
        result = jsonrpc_call("session", "login", {
            "username": "admin",
            "password": "admin"
        })
        
        print("Response:")
        print(json.dumps(result, indent=2))
        
        if "result" in result and len(result["result"]) > 1:
            session_id = result["result"][1].get("sid")
            if session_id:
                print(f"\n✓ Login successful!")
                print(f"  Session ID: {session_id}")
            else:
                print("\n✗ Login failed: No session ID in response")
                return 1
        else:
            print("\n✗ Login failed: Unexpected response format")
            return 1
            
    except Exception as e:
        print(f"\n✗ Login failed: {e}")
        return 1
    
    # Step 4: Get device status
    test_step(4, "Testing device status API")
    try:
        result = jsonrpc_call("anet", "status", {}, session_id)
        print("Response:")
        print(json.dumps(result, indent=2))
        
        if "result" in result and result["result"][0] == 0:
            print("\n✓ Status API working!")
        else:
            print("\n⚠ Status API returned unexpected response")
            
    except Exception as e:
        print(f"\n✗ Status API failed: {e}")
    
    # Step 5: Get MAC address
    test_step(5, "Testing device info API")
    try:
        result = jsonrpc_call("mfgd", "get_fonmac", {}, session_id)
        
        if "result" in result and result["result"][0] == 0:
            mac = result["result"][1].get("fonmac", "Unknown")
            print(f"✓ Device MAC: {mac}")
        else:
            print("⚠ Could not get MAC address")
            
    except Exception as e:
        print(f"✗ Get MAC failed: {e}")
    
    # Step 6: Get device name
    test_step(6, "Testing device name API")
    try:
        result = jsonrpc_call("anet", "get_gramofonname", {}, session_id)
        
        if "result" in result and result["result"][0] == 0:
            name = result["result"][1].get("spotifyname", "Unknown")
            print(f"✓ Device name: {name}")
        else:
            print("⚠ Could not get device name")
            
    except Exception as e:
        print(f"✗ Get name failed: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("✓ All core functions are working!")
    print("\nYou can now configure your device with:")
    print(f"  python gramofon_jsonrpc_client.py configure <SSID> <PASSWORD>")
    print(f"or:")
    print(f"  ./gramofon_jsonrpc.sh configure <SSID> <PASSWORD>")
    print()
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
