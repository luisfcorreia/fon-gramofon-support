# Gramofon Device HTTP API Documentation

## Overview

This documentation was reverse-engineered from the Gramofon Setup APK (version 114602) to enable configuration of the Gramofon hardware device without the Android app, which is no longer compatible with Android 14+.

The Gramofon device manufacturer (Fon/Gramofon) has stopped supporting the device and has gone out of business, making this reverse engineering effort necessary to continue using these devices.

## Base Information

- **Device IP Address**: `192.168.10.1` (default when in setup mode)
- **Base URL**: `http://192.168.10.1/api/`
- **Package Name**: `com.fon.gramofonsetup`
- **API Pattern**: `/api/<32-character-hex-string>`

## API Endpoints

Based on decompilation, the following API endpoints have been identified:

### 1. Get WiFi Interface Configuration
**Endpoint**: `/api/<session_id>/get_wiface`  
**Method**: GET  
**Description**: Retrieves the current WiFi interface configuration

**Response Model**: `GetWifaceResponse`

**Expected Response Fields**:
- SSID value
- Password value
- WiFi status
- Network extras
- Server parameters

---

### 2. Set WiFi Interface Configuration
**Endpoint**: `/api/<session_id>/set_wiface`  
**Method**: POST  
**Description**: Configures the WiFi settings for the device

**Parameters**:
- `ssid`: The WiFi network SSID to connect to
- `password`: The WiFi network password
- Additional network configuration parameters

**Request Fields**:
- `ssidValue`: String
- `passwordValue`: String
- WiFi security/encryption settings

---

### 3. Get Gramofon Name
**Endpoint**: `/api/<session_id>/get_gramofonname`  
**Method**: GET  
**Description**: Retrieves the current device name

**Response**:
- `gramofon_name`: String - The friendly name of the device

---

### 4. Set Gramofon Name
**Endpoint**: `/api/<session_id>/set_gramofonname`  
**Method**: POST  
**Description**: Sets the device's friendly name

**Parameters**:
- `gramofon_name`: String - The new name for the device

---

### 5. Check Upgrades
**Endpoint**: `/api/<session_id>/check_upgrades`  
**Method**: GET  
**Description**: Checks for firmware upgrades

**Response Model**: `CheckUpgradesResponse`

**Response Fields**:
- `ImagesEntity`: Array of available firmware images
- Version information
- Download URLs

---

### 6. Check Adapters
**Endpoint**: `/api/<session_id>/check_adapters`  
**Method**: GET  
**Description**: Checks available network adapters on the device

---

### 7. Check Packages
**Endpoint**: `/api/<session_id>/check_packages`  
**Method**: GET  
**Description**: Checks installed packages/applications

---

### 8. Check Validation
**Endpoint**: `/api/<session_id>/check_validation`  
**Method**: GET  
**Description**: Validates the current device configuration

**Constant**: `CHECK_VALIDATION`

---

### 9. Get Firmware Version
**Endpoint**: `/api/<session_id>/get_fw_version`  
**Method**: GET  
**Description**: Retrieves the current firmware version

---

### 10. Get FON MAC Address
**Endpoint**: `/api/<session_id>/get_fonmac`  
**Method**: GET  
**Description**: Retrieves the device's MAC address

---

### 11. Get SSIDs
**Endpoint**: `/api/<session_id>/get_ssids`  
**Method**: GET  
**Description**: Scans and returns available WiFi networks

**Response**: List of visible SSIDs with their details

---

### 12. Status
**Endpoint**: `/api/<session_id>/status`  
**Method**: GET  
**Description**: Gets the current device status

---

### 13. Configure Gramofon
**Method**: `configureGramofon`  
**Description**: Main configuration method that orchestrates device setup

---

## Session Management

The API uses a 32-character hexadecimal session ID in the URL path:
- **Pattern**: `/api/00000000000000000000000000000000/<endpoint>`
- **Placeholder**: `@gw_sessid@` is used in code as a template

The session ID appears to be a placeholder or default value. You may need to:
1. Obtain a session ID first (possibly through an initial handshake)
2. Use a fixed session ID if the device uses a simple authentication scheme

## Key Configuration Parameters

### WiFi Configuration
- **SSID**: Network name to connect to
- **Password**: Network password
- **Security Type**: Encryption method (WPA/WPA2, etc.)
- **Network Extras**: Additional network parameters

### Device Configuration
- **Gramofon Name**: Friendly device name
- **Fonera Mode**: Operating mode setting

## Response Codes

Based on the constants found:
- `STATUS_OK`: Operation successful
- `STATUS_FAILED`: Operation failed
- `BAD_PASSWORD`: Invalid WiFi password
- `NETWORK_ERROR`: Network connectivity issue

## Error Messages

- "No responde la gramofon" - Device not responding
- "Time out, fonera no accesible" - Device timeout/not accessible
- "...no network connectivity" - No network connection

## Important Notes

### Connection Flow
1. **Connect to Device AP**: The Gramofon creates its own WiFi network when unconfigured
2. **Access Web Interface**: Navigate to `http://192.168.10.1`
3. **Get Available Networks**: Call `get_ssids` to scan for WiFi networks
4. **Configure WiFi**: Use `set_wiface` with SSID and password
5. **Set Device Name**: Optionally call `set_gramofonname`
6. **Verify Connection**: Check status with `status` endpoint

### Model Classes

The app uses these data models for API responses:
- `GetWifaceResponse`: WiFi configuration response
- `CheckUpgradesResponse`: Firmware upgrade information
- `GramofonInfo`: Device information model
- `SetupFunnelData`: Setup process tracking data

### Service Implementation

The API services are implemented in the package:
`com.fon.gramofonsetup.services`

Key service classes handle different aspects:
- Network configuration
- Device settings
- Firmware updates
- Status monitoring

## Example Usage

### Python Example - Get WiFi Configuration

```python
import requests

DEVICE_IP = "192.168.10.1"
SESSION_ID = "00000000000000000000000000000000"  # May need to obtain this
BASE_URL = f"http://{DEVICE_IP}/api/{SESSION_ID}"

# Get current WiFi configuration
response = requests.get(f"{BASE_URL}/get_wiface")
print(response.json())

# Get available networks
response = requests.get(f"{BASE_URL}/get_ssids")
networks = response.json()
print(f"Found {len(networks)} networks")

# Configure WiFi
config = {
    "ssid": "YourWiFiNetwork",
    "password": "YourPassword"
}
response = requests.post(f"{BASE_URL}/set_wiface", json=config)
print(response.json())

# Set device name
name_data = {"gramofon_name": "Living Room Gramofon"}
response = requests.post(f"{BASE_URL}/set_gramofonname", json=name_data)
print(response.json())

# Check status
response = requests.get(f"{BASE_URL}/status")
print(response.json())
```

### Bash Example - Simple Status Check

```bash
#!/bin/bash

DEVICE_IP="192.168.10.1"
SESSION_ID="00000000000000000000000000000000"
BASE_URL="http://${DEVICE_IP}/api/${SESSION_ID}"

# Get status
curl "${BASE_URL}/status"

# Get firmware version
curl "${BASE_URL}/get_fw_version"

# Get device name
curl "${BASE_URL}/get_gramofonname"

# Scan for networks
curl "${BASE_URL}/get_ssids"
```

## Testing Recommendations

1. **Start Simple**: Try the GET endpoints first (`status`, `get_fw_version`, `get_gramofonname`)
2. **Check Session ID**: The session ID format may need adjustment based on actual device responses
3. **Monitor Network Traffic**: Use Wireshark or similar to capture actual API calls if needed
4. **Test in Safe Environment**: Test on a device you don't mind resetting
5. **Document Responses**: Save actual API responses to understand the exact JSON structure

## Additional Investigation Needed

The following areas may require further investigation:

1. **Session ID Generation**: How the 32-character session ID is generated or obtained
2. **Authentication**: Whether any authentication headers are required
3. **Request Format**: Whether parameters should be in JSON body, form data, or URL parameters
4. **Response Format**: The exact JSON structure of responses
5. **Error Handling**: Detailed error response format
6. **Fonera Mode**: What the different "fonera modes" are and how to switch between them

## Resources

- Original APK: `Gramofon_Setup_114602.apk`
- Package: `com.fon.gramofonsetup`
- Device IP: `192.168.10.1`
- Device Manufacturer: Fon/Gramofon (defunct)

## Legal Note

This documentation is created for the purpose of maintaining compatibility with legacy hardware whose manufacturer has ceased operations. The reverse engineering was performed solely to enable continued use of already-purchased hardware.
