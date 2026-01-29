#!/bin/bash
#
# Gramofon Factory Reset Script
# Resets device to factory defaults with double confirmation
#

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BOLD='\033[1m'
NC='\033[0m'

DEVICE_IP="$1"
TIMEOUT=30

if [ -z "$DEVICE_IP" ]; then
    echo "Usage: $0 <device_ip>"
    echo ""
    echo "Example:"
    echo "  $0 192.168.1.100"
    echo ""
    echo "To find your device IP, run:"
    echo "  python gramofon_discovery.py --list"
    exit 1
fi

# JSON-RPC call function
jsonrpc_call() {
    local ip="$1"
    local module="$2"
    local method="$3"
    local params="$4"
    local sid="$5"
    
    local url="http://${ip}/api/${sid:-00000000000000000000000000000000}"
    
    local payload=$(cat <<EOF
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call",
  "params": ["$module", "$method", $params]
}
EOF
)
    
    curl -s -X POST "$url" \
        -H "Content-Type: application/json" \
        --max-time "$TIMEOUT" \
        -d "$payload"
}

# Login
login() {
    local ip="$1"
    local params='{"username":"admin","password":"admin"}'
    local response=$(jsonrpc_call "$ip" "session" "login" "$params")
    echo "$response" | grep -o '"sid":"[^"]*"' | sed 's/"sid":"\([^"]*\)"/\1/'
}

# Get device name
get_name() {
    local ip="$1"
    local sid="$2"
    local response=$(jsonrpc_call "$ip" "anet" "get_gramofonname" "{}" "$sid")
    echo "$response" | grep -o '"spotifyname":"[^"]*"' | sed 's/"spotifyname":"\([^"]*\)"/\1/'
}

# Get MAC address
get_mac() {
    local ip="$1"
    local sid="$2"
    local response=$(jsonrpc_call "$ip" "mfgd" "get_fonmac" "{}" "$sid")
    echo "$response" | grep -o '"fonmac":"[^"]*"' | sed 's/"fonmac":"\([^"]*\)"/\1/'
}

# Factory reset
factory_reset() {
    local ip="$1"
    local sid="$2"
    local response=$(jsonrpc_call "$ip" "mfgd" "reset_defaults" "{}" "$sid")
    echo "$response" | grep -q '"result":\[0'
}

# Warning banner
print_warning() {
    echo ""
    echo -e "${RED}======================================================================"
    echo -e "             ⚠️  WARNING: FACTORY RESET ⚠️"
    echo -e "======================================================================${NC}"
    echo ""
    echo "This will:"
    echo "  • Erase ALL configuration from the device"
    echo "  • Remove WiFi settings (device will disconnect from your network)"
    echo "  • Reset device name to default"
    echo '  • Create "Gramofon Configuration" WiFi network again'
    echo "  • Require you to reconfigure the device from scratch"
    echo ""
    echo -e "${BOLD}This action CANNOT BE UNDONE!${NC}"
    echo ""
    echo -e "${RED}======================================================================${NC}"
    echo ""
}

# Main
main() {
    # Connect to device
    echo -e "${YELLOW}Connecting to ${DEVICE_IP}...${NC}"
    SID=$(login "$DEVICE_IP")
    
    if [ -z "$SID" ]; then
        echo -e "${RED}✗ Could not connect to device${NC}"
        echo ""
        echo "Make sure:"
        echo "  - Device is powered on"
        echo "  - Device is on the network"
        echo "  - IP address is correct"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Connected successfully${NC}"
    echo ""
    
    # Get device info
    echo -e "${YELLOW}Getting device information...${NC}"
    DEVICE_NAME=$(get_name "$DEVICE_IP" "$SID")
    DEVICE_MAC=$(get_mac "$DEVICE_IP" "$SID")
    
    if [ -z "$DEVICE_NAME" ]; then
        DEVICE_NAME="Unknown Device"
    fi
    
    if [ -z "$DEVICE_MAC" ]; then
        DEVICE_MAC="Unknown"
    fi
    
    echo ""
    
    # Show warning
    print_warning
    
    # Show device info
    echo "Device Information:"
    echo "  Name: $DEVICE_NAME"
    echo "  IP:   $DEVICE_IP"
    echo "  MAC:  $DEVICE_MAC"
    echo ""
    
    # First confirmation
    echo -e "${RED}======================================================================${NC}"
    read -p "Are you SURE you want to factory reset this device? (yes/no): " confirm1
    
    if [ "$confirm1" != "yes" ]; then
        echo ""
        echo "Factory reset cancelled."
        exit 0
    fi
    
    # Second confirmation with device name
    echo ""
    echo -e "${RED}======================================================================"
    echo -e "                ⚠️  FINAL CONFIRMATION ⚠️"
    echo -e "======================================================================${NC}"
    echo ""
    echo "You are about to factory reset: $DEVICE_NAME"
    echo "All settings will be permanently erased."
    echo ""
    read -p "Type the device name '$DEVICE_NAME' to confirm: " confirm2
    
    if [ "$confirm2" != "$DEVICE_NAME" ]; then
        echo ""
        echo "Device name doesn't match. Factory reset cancelled."
        exit 0
    fi
    
    # Perform reset
    echo ""
    echo -e "${RED}======================================================================${NC}"
    echo -e "${YELLOW}Performing factory reset...${NC}"
    echo -e "${RED}======================================================================${NC}"
    echo ""
    
    if factory_reset "$DEVICE_IP" "$SID"; then
        echo -e "${GREEN}✓ Factory reset command sent successfully!${NC}"
        echo ""
        echo "Device is now resetting..."
        echo ""
        echo -e "${YELLOW}Next steps:${NC}"
        echo "  1. Wait 30-60 seconds for device to reboot"
        echo '  2. Look for "Gramofon Configuration" WiFi network'
        echo "  3. Connect to it and reconfigure the device"
        echo ""
        echo "You can now disconnect from the current network."
        echo ""
    else
        echo -e "${RED}✗ Factory reset failed!${NC}"
        echo "The device may not support this operation or connection was lost."
        exit 1
    fi
}

main
