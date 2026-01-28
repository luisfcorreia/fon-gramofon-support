#!/usr/bin/env python3
"""
Test device name setting to diagnose the issue
"""

import requests
import json
import sys

def jsonrpc_call(ip, sid, module, method, params):
    """Make a JSON-RPC call"""
    url = f"http://{ip}/api/{sid}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "call",
        "params": [module, method, params]
    }
    
    print(f"\n📤 Request to {module}.{method}:")
    print(json.dumps(params, indent=2))
    
    response = requests.post(url, json=payload, timeout=10)
    data = response.json()
    
    print(f"\n📥 Response:")
    print(json.dumps(data, indent=2))
    
    return data

def login(ip):
    """Login and get session"""
    result = jsonrpc_call(ip, "00000000000000000000000000000000", 
                         "session", "login", 
                         {"username": "admin", "password": "admin"})
    
    if "result" in result and len(result["result"]) > 1:
        return result["result"][1].get("sid")
    return None

def test_name_setting(ip, test_name):
    """Test different ways to set device name"""
    print("="*70)
    print("TESTING DEVICE NAME SETTING")
    print("="*70)
    
    # Login
    print("\n1. Logging in...")
    sid = login(ip)
    if not sid:
        print("❌ Login failed")
        return
    print(f"✓ Session ID: {sid}")
    
    # Get current name
    print("\n2. Getting current device name...")
    result = jsonrpc_call(ip, sid, "anet", "get_gramofonname", {})
    if result and "result" in result:
        current_name = result["result"][1].get("spotifyname", "Unknown")
        print(f"✓ Current name: {current_name}")
    
    # Try setting with set_gramofonname
    print(f"\n3. Testing set_gramofonname with '{test_name}'...")
    result = jsonrpc_call(ip, sid, "anet", "set_gramofonname", {
        "mdnsname": test_name,
        "spotifyname": test_name
    })
    
    if result and "result" in result and result["result"][0] == 0:
        print("✓ set_gramofonname call succeeded")
    else:
        print("❌ set_gramofonname call failed")
    
    # Verify the change
    print("\n4. Verifying name change...")
    result = jsonrpc_call(ip, sid, "anet", "get_gramofonname", {})
    if result and "result" in result:
        new_name = result["result"][1].get("spotifyname", "Unknown")
        print(f"Name after set_gramofonname: {new_name}")
        if new_name == test_name:
            print("✓ Name was changed successfully!")
        else:
            print(f"❌ Name did not change (expected '{test_name}', got '{new_name}')")
    
    # Try with just spotifyname
    print(f"\n5. Testing with only spotifyname parameter...")
    result = jsonrpc_call(ip, sid, "anet", "set_gramofonname", {
        "spotifyname": test_name + "_v2"
    })
    
    # Try with just mdnsname
    print(f"\n6. Testing with only mdnsname parameter...")
    result = jsonrpc_call(ip, sid, "anet", "set_gramofonname", {
        "mdnsname": test_name + "_v3"
    })
    
    # Check final state
    print("\n7. Final verification...")
    result = jsonrpc_call(ip, sid, "anet", "get_gramofonname", {})
    if result and "result" in result:
        final_name = result["result"][1].get("spotifyname", "Unknown")
        final_mdns = result["result"][1].get("mdnsname", "Unknown")
        print(f"Final spotifyname: {final_name}")
        print(f"Final mdnsname: {final_mdns}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python test_name_setting.py <device_ip> <test_name>")
        print("Example: python test_name_setting.py 192.168.1.100 'Test Device'")
        sys.exit(1)
    
    test_name_setting(sys.argv[1], sys.argv[2])
