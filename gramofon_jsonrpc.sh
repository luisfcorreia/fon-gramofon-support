#!/bin/bash
#
# Gramofon Device Configuration Script (JSON-RPC 2.0)
# Based on verified decompiled APK source code
#

# Configuration
DEVICE_IP="${GRAMOFON_IP:-192.168.10.1}"
SID=""
TIMEOUT=30

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# JSON-RPC call function
jsonrpc_call() {
    local module="$1"
    local method="$2"
    local params="$3"
    
    local url="http://${DEVICE_IP}/api/${SID:-00000000000000000000000000000000}"
    
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
        -H "Accept: application/json" \
        --max-time "$TIMEOUT" \
        -d "$payload"
}

# Login and get session ID
login() {
    echo -e "${YELLOW}Logging in...${NC}"
    
    local params='{"username":"admin","password":"admin"}'
    local response=$(jsonrpc_call "session" "login" "$params")
    
    # Extract session ID using grep/sed (works without jq)
    SID=$(echo "$response" | grep -o '"sid":"[^"]*"' | sed 's/"sid":"\([^"]*\)"/\1/')
    
    if [ -z "$SID" ]; then
        echo -e "${RED}Login failed${NC}"
        echo "$response"
        exit 1
    fi
    
    echo -e "${GREEN}Logged in successfully${NC}"
    echo -e "Session ID: ${SID}"
}

# Get device status
get_status() {
    echo -e "${YELLOW}Getting device status...${NC}"
    local response=$(jsonrpc_call "anet" "status" "{}")
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
}

# Get MAC address
get_mac() {
    echo -e "${YELLOW}Getting MAC address...${NC}"
    local response=$(jsonrpc_call "mfgd" "get_fonmac" "{}")
    echo "$response" | jq -r '.result[1].fonmac' 2>/dev/null || echo "$response"
}

# Get device name
get_name() {
    echo -e "${YELLOW}Getting device name...${NC}"
    local response=$(jsonrpc_call "anet" "get_gramofonname" "{}")
    echo "$response" | jq -r '.result[1].spotifyname' 2>/dev/null || echo "$response"
}

# Set device name
set_name() {
    local name="$1"
    echo -e "${YELLOW}Setting device name to: ${name}${NC}"
    
    local params="{\"mdnsname\":\"$name\",\"spotifyname\":\"$name\"}"
    local response=$(jsonrpc_call "anet" "set_gramofonname" "$params")
    
    if echo "$response" | grep -q '"result":\[0'; then
        echo -e "${GREEN}Device name set successfully${NC}"
    else
        echo -e "${RED}Failed to set device name${NC}"
        echo "$response"
    fi
}

# Scan for WiFi networks
scan_networks() {
    echo -e "${YELLOW}Starting WiFi scan...${NC}"
    
    # Start scan
    local params='{"iface":"radio"}'
    jsonrpc_call "anet" "ssid_scan" "$params" > /dev/null
    
    # Wait for scan to complete
    echo "Waiting for scan to complete..."
    sleep 2
    
    # Get results
    echo -e "${YELLOW}Getting scan results...${NC}"
    local response=$(jsonrpc_call "anet" "get_ssids" "{}")
    
    # Parse and display networks
    if command -v jq > /dev/null 2>&1; then
        echo -e "\n${GREEN}Available networks:${NC}\n"
        echo "$response" | jq -r '.result[1].results[] | "\(.ssid) - \(.encryption) - Quality: \(.quality)/\(.quality_max)"' 2>/dev/null
    else
        echo "$response"
    fi
}

# Get WiFi configuration
get_wifi() {
    echo -e "${YELLOW}Getting WiFi configuration...${NC}"
    local params='{"name":"private"}'
    local response=$(jsonrpc_call "wifid" "get_wiface" "$params")
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
}

# Configure WiFi
configure_wifi() {
    local ssid="$1"
    local password="$2"
    local device_name="$3"
    
    echo -e "${YELLOW}Configuring WiFi...${NC}"
    echo -e "  SSID: ${ssid}"
    echo -e "  Password: ${password//?/*}"
    [ -n "$device_name" ] && echo -e "  Device Name: ${device_name}"
    
    # Build params
    local params="{\"netmode\":\"wcliclone\",\"ssid\":\"$ssid\",\"key\":\"$password\",\"encryption\":\"psk2\",\"ap_disabled\":false"
    
    if [ -n "$device_name" ]; then
        params="${params},\"gramofon_name\":\"$device_name\""
    fi
    
    params="${params}}"
    
    # Send configuration
    local response=$(jsonrpc_call "anet" "doeasysetup" "$params")
    
    if echo "$response" | grep -q '"result":\[0'; then
        echo -e "${GREEN}WiFi configuration sent successfully${NC}"
        
        # Reload WiFi
        echo -e "${YELLOW}Reloading WiFi configuration...${NC}"
        jsonrpc_call "wifid" "reload" "{}" > /dev/null
        echo -e "${GREEN}WiFi reloaded${NC}"
    else
        echo -e "${RED}Failed to configure WiFi${NC}"
        echo "$response"
        return 1
    fi
}

# Reload WiFi
reload_wifi() {
    echo -e "${YELLOW}Reloading WiFi configuration...${NC}"
    local response=$(jsonrpc_call "wifid" "reload" "{}")
    
    if echo "$response" | grep -q '"result":\[0'; then
        echo -e "${GREEN}WiFi reloaded successfully${NC}"
    else
        echo -e "${RED}Failed to reload WiFi${NC}"
        echo "$response"
    fi
}

# Check for upgrades
check_upgrades() {
    echo -e "${YELLOW}Checking for firmware upgrades...${NC}"
    local response=$(jsonrpc_call "mfgd" "check_upgrades" "{}")
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
}

# Reboot device
reboot_device() {
    echo -e "${YELLOW}Rebooting device...${NC}"
    local response=$(jsonrpc_call "mfgd" "reboot" "{}")
    echo -e "${GREEN}Reboot command sent${NC}"
}

# Reset to factory defaults
factory_reset() {
    echo -e "${RED}WARNING: This will reset the device to factory defaults!${NC}"
    read -p "Are you sure? (yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        echo -e "${YELLOW}Resetting to factory defaults...${NC}"
        local response=$(jsonrpc_call "mfgd" "reset_defaults" "{}")
        echo -e "${GREEN}Factory reset initiated${NC}"
    else
        echo "Cancelled"
    fi
}

# LED control
led_status() {
    echo -e "${YELLOW}Getting LED status...${NC}"
    local response=$(jsonrpc_call "ledd" "get" "{}")
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
}

led_on() {
    echo -e "${YELLOW}Turning LED on...${NC}"
    local params='{"status":"enable"}'
    jsonrpc_call "ledd" "switch" "$params" > /dev/null
    echo -e "${GREEN}LED turned on${NC}"
}

led_off() {
    echo -e "${YELLOW}Turning LED off...${NC}"
    local params='{"status":"disable"}'
    jsonrpc_call "ledd" "switch" "$params" > /dev/null
    echo -e "${GREEN}LED turned off${NC}"
}

# Show device info
show_info() {
    echo -e "${GREEN}=== Gramofon Device Information ===${NC}\n"
    
    login
    echo ""
    
    echo -e "${BLUE}Status:${NC}"
    get_status
    echo ""
    
    echo -e "${BLUE}MAC Address:${NC}"
    get_mac
    echo ""
    
    echo -e "${BLUE}Device Name:${NC}"
    get_name
    echo ""
    
    echo -e "${BLUE}WiFi Configuration:${NC}"
    get_wifi
    echo ""
}

# Complete device configuration
complete_setup() {
    local ssid="$1"
    local password="$2"
    local device_name="$3"
    
    if [ -z "$ssid" ] || [ -z "$password" ]; then
        echo -e "${RED}Error: SSID and password required${NC}"
        echo "Usage: $0 configure SSID PASSWORD [DEVICE_NAME]"
        return 1
    fi
    
    echo -e "${GREEN}=== Starting Gramofon Configuration ===${NC}\n"
    
    # Step 1: Login (critical)
    echo -e "${YELLOW}Step 1: Logging in...${NC}"
    login
    if [ -z "$SID" ]; then
        echo -e "${RED}Failed to login. Aborting.${NC}"
        return 1
    fi
    echo ""
    
    # Step 2: Configure WiFi (critical)
    echo -e "${YELLOW}Step 2: Configuring WiFi${NC}"
    if configure_wifi "$ssid" "$password" "$device_name"; then
        echo ""
    else
        echo -e "${RED}WiFi configuration failed. Aborting.${NC}"
        return 1
    fi
    
    # Success message
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           ✓ Configuration Complete!                   ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Wait 30-60 seconds for device to apply settings"
    echo "  2. 'Gramofon Configuration' network will disappear"
    echo "  3. Device will connect to your home WiFi"
    echo "  4. You can now disconnect from Gramofon and reconnect to your WiFi"
    echo ""
}

# Print usage
usage() {
    cat << EOF
${GREEN}Gramofon Device Configuration Script (JSON-RPC 2.0)${NC}

Usage: $0 [command] [options]

${YELLOW}Commands:${NC}
    status              Get device status
    mac                 Get MAC address
    name [NAME]         Get or set device name
    
    scan                Scan for WiFi networks
    wifi-get            Get current WiFi configuration
    wifi-set SSID PASS  Configure WiFi
    wifi-reload         Reload WiFi configuration
    
    led-status          Get LED status
    led-on              Turn LED on
    led-off             Turn LED off
    
    upgrades            Check for firmware upgrades
    reboot              Reboot device
    reset               Factory reset (confirmation required)
    
    info                Show all device information
    configure SSID PASS [NAME]  Complete device setup

${YELLOW}Environment Variables:${NC}
    GRAMOFON_IP         Device IP address (default: 192.168.10.1)

${YELLOW}Examples:${NC}
    # Get device info
    $0 info

    # Scan for networks
    $0 scan

    # Configure WiFi
    $0 wifi-set "MyNetwork" "MyPassword"

    # Complete setup with device name
    $0 configure "MyNetwork" "MyPassword" "Living Room"

    # Use different IP
    GRAMOFON_IP=192.168.1.100 $0 status

EOF
}

# Main script logic
case "$1" in
    status)
        login && get_status
        ;;
    mac)
        login && get_mac
        ;;
    name)
        login
        if [ -n "$2" ]; then
            set_name "$2"
        else
            get_name
        fi
        ;;
    scan)
        login && scan_networks
        ;;
    wifi-get)
        login && get_wifi
        ;;
    wifi-set)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}Error: SSID and password required${NC}"
            echo "Usage: $0 wifi-set SSID PASSWORD"
            exit 1
        fi
        login && configure_wifi "$2" "$3"
        ;;
    wifi-reload)
        login && reload_wifi
        ;;
    led-status)
        login && led_status
        ;;
    led-on)
        login && led_on
        ;;
    led-off)
        login && led_off
        ;;
    upgrades)
        login && check_upgrades
        ;;
    reboot)
        login && reboot_device
        ;;
    reset)
        login && factory_reset
        ;;
    info)
        show_info
        ;;
    configure)
        complete_setup "$2" "$3" "$4"
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
