#!/bin/bash
#
# Gramofon Device Configuration Script
# A simple bash script for interacting with Gramofon devices
#

# Configuration
DEVICE_IP="${GRAMOFON_IP:-192.168.10.1}"
SESSION_ID="${GRAMOFON_SESSION:-00000000000000000000000000000000}"
BASE_URL="http://${DEVICE_IP}/api/${SESSION_ID}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function to make API calls
api_get() {
    local endpoint="$1"
    local url="${BASE_URL}/${endpoint}"
    echo -e "${YELLOW}GET ${url}${NC}" >&2
    curl -s -X GET "${url}" 2>/dev/null || echo '{"error": "Failed to connect to device"}'
}

api_post() {
    local endpoint="$1"
    local data="$2"
    local url="${BASE_URL}/${endpoint}"
    echo -e "${YELLOW}POST ${url}${NC}" >&2
    curl -s -X POST "${url}" \
        -H "Content-Type: application/json" \
        -d "${data}" 2>/dev/null || echo '{"error": "Failed to connect to device"}'
}

# Print usage
usage() {
    cat << EOF
Gramofon Device Configuration Script

Usage: $0 [command] [options]

Commands:
    status                      Get device status
    version                     Get firmware version
    mac                         Get MAC address
    name [new_name]             Get or set device name
    scan                        Scan for WiFi networks
    wifi-get                    Get current WiFi configuration
    wifi-set <ssid> <password>  Configure WiFi
    upgrades                    Check for firmware upgrades
    info                        Show all device information
    configure <ssid> <password> [name]  Complete device setup

Environment Variables:
    GRAMOFON_IP      Device IP address (default: 192.168.10.1)
    GRAMOFON_SESSION Session ID (default: 32 zeros)

Examples:
    # Get device status
    $0 status

    # Set device name
    $0 name "Living Room Speaker"

    # Scan for networks
    $0 scan

    # Configure WiFi
    $0 wifi-set "MyNetwork" "MyPassword"

    # Complete setup
    $0 configure "MyNetwork" "MyPassword" "Living Room"

EOF
}

# Get device status
get_status() {
    echo -e "${GREEN}Getting device status...${NC}"
    api_get "status" | jq '.' 2>/dev/null || echo "Response received (jq not installed for formatting)"
}

# Get firmware version
get_version() {
    echo -e "${GREEN}Getting firmware version...${NC}"
    api_get "get_fw_version" | jq '.' 2>/dev/null || api_get "get_fw_version"
}

# Get MAC address
get_mac() {
    echo -e "${GREEN}Getting MAC address...${NC}"
    api_get "get_fonmac" | jq '.' 2>/dev/null || api_get "get_fonmac"
}

# Get device name
get_name() {
    echo -e "${GREEN}Getting device name...${NC}"
    api_get "get_gramofonname" | jq '.' 2>/dev/null || api_get "get_gramofonname"
}

# Set device name
set_name() {
    local name="$1"
    if [ -z "$name" ]; then
        echo -e "${RED}Error: Device name required${NC}"
        return 1
    fi
    echo -e "${GREEN}Setting device name to: ${name}${NC}"
    local data="{\"gramofon_name\": \"${name}\"}"
    api_post "set_gramofonname" "$data" | jq '.' 2>/dev/null || api_post "set_gramofonname" "$data"
}

# Scan for WiFi networks
scan_networks() {
    echo -e "${GREEN}Scanning for WiFi networks...${NC}"
    api_get "get_ssids" | jq '.' 2>/dev/null || api_get "get_ssids"
}

# Get WiFi configuration
get_wifi() {
    echo -e "${GREEN}Getting WiFi configuration...${NC}"
    api_get "get_wiface" | jq '.' 2>/dev/null || api_get "get_wiface"
}

# Set WiFi configuration
set_wifi() {
    local ssid="$1"
    local password="$2"
    
    if [ -z "$ssid" ] || [ -z "$password" ]; then
        echo -e "${RED}Error: SSID and password required${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Configuring WiFi...${NC}"
    echo -e "  SSID: ${ssid}"
    echo -e "  Password: ${password//?/*}"
    
    local data="{\"ssid\": \"${ssid}\", \"password\": \"${password}\"}"
    api_post "set_wiface" "$data" | jq '.' 2>/dev/null || api_post "set_wiface" "$data"
}

# Check for upgrades
check_upgrades() {
    echo -e "${GREEN}Checking for firmware upgrades...${NC}"
    api_get "check_upgrades" | jq '.' 2>/dev/null || api_get "check_upgrades"
}

# Show all device information
show_info() {
    echo -e "${GREEN}=== Gramofon Device Information ===${NC}\n"
    
    echo -e "${YELLOW}Status:${NC}"
    get_status
    echo ""
    
    echo -e "${YELLOW}Firmware Version:${NC}"
    get_version
    echo ""
    
    echo -e "${YELLOW}MAC Address:${NC}"
    get_mac
    echo ""
    
    echo -e "${YELLOW}Device Name:${NC}"
    get_name
    echo ""
    
    echo -e "${YELLOW}WiFi Configuration:${NC}"
    get_wifi
    echo ""
}

# Complete device configuration
configure_device() {
    local ssid="$1"
    local password="$2"
    local name="$3"
    
    if [ -z "$ssid" ] || [ -z "$password" ]; then
        echo -e "${RED}Error: SSID and password required${NC}"
        usage
        return 1
    fi
    
    echo -e "${GREEN}=== Starting Gramofon Configuration ===${NC}\n"
    
    # Get initial status
    echo -e "${YELLOW}1. Getting initial status...${NC}"
    get_status
    echo ""
    
    # Scan networks
    echo -e "${YELLOW}2. Scanning for networks...${NC}"
    scan_networks
    echo ""
    
    # Configure WiFi
    echo -e "${YELLOW}3. Configuring WiFi...${NC}"
    set_wifi "$ssid" "$password"
    echo ""
    
    # Set device name if provided
    if [ -n "$name" ]; then
        echo -e "${YELLOW}4. Setting device name...${NC}"
        set_name "$name"
        echo ""
    fi
    
    # Get final status
    echo -e "${YELLOW}5. Getting final status...${NC}"
    get_status
    echo ""
    
    echo -e "${GREEN}=== Configuration Complete ===${NC}"
}

# Main script logic
case "$1" in
    status)
        get_status
        ;;
    version)
        get_version
        ;;
    mac)
        get_mac
        ;;
    name)
        if [ -n "$2" ]; then
            set_name "$2"
        else
            get_name
        fi
        ;;
    scan)
        scan_networks
        ;;
    wifi-get)
        get_wifi
        ;;
    wifi-set)
        set_wifi "$2" "$3"
        ;;
    upgrades)
        check_upgrades
        ;;
    info)
        show_info
        ;;
    configure)
        configure_device "$2" "$3" "$4"
        ;;
    -h|--help|help|"")
        usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        usage
        exit 1
        ;;
esac
