#!/bin/bash
#
# Gramofon LED Control Script
# Quick tool to control LED on configured Gramofon devices
#

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

DEVICE_IP="${1:-}"
TIMEOUT=5

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

# Login to device
login() {
    local ip="$1"
    local params='{"username":"admin","password":"admin"}'
    local response=$(jsonrpc_call "$ip" "session" "login" "$params")
    
    # Extract session ID
    echo "$response" | grep -o '"sid":"[^"]*"' | sed 's/"sid":"\([^"]*\)"/\1/'
}

# Get device name
get_name() {
    local ip="$1"
    local sid="$2"
    local response=$(jsonrpc_call "$ip" "anet" "get_gramofonname" "{}" "$sid")
    echo "$response" | grep -o '"spotifyname":"[^"]*"' | sed 's/"spotifyname":"\([^"]*\)"/\1/'
}

# Turn LED on
led_on() {
    local ip="$1"
    local sid="$2"
    local params='{"status":"enable"}'
    jsonrpc_call "$ip" "ledd" "switch" "$params" "$sid" > /dev/null
}

# Turn LED off
led_off() {
    local ip="$1"
    local sid="$2"
    local params='{"status":"disable"}'
    jsonrpc_call "$ip" "ledd" "switch" "$params" "$sid" > /dev/null
}

# Get LED status
led_status() {
    local ip="$1"
    local sid="$2"
    jsonrpc_call "$ip" "ledd" "get" "{}" "$sid"
}

# Check if IP is a Gramofon
check_gramofon() {
    local ip="$1"
    local sid=$(login "$ip" 2>/dev/null)
    
    if [ -n "$sid" ]; then
        local name=$(get_name "$ip" "$sid" 2>/dev/null)
        if [ -n "$name" ]; then
            echo "$sid|$name"
            return 0
        fi
    fi
    return 1
}

# Scan network for Gramofondevices
scan_network() {
    local network_prefix="$1"
    
    echo -e "${YELLOW}Scanning network ${network_prefix}.0/24...${NC}"
    echo "This may take 1-2 minutes..."
    echo ""
    
    local found=0
    
    for i in {1..254}; do
        local ip="${network_prefix}.${i}"
        
        # Show progress
        if [ $((i % 50)) -eq 0 ]; then
            echo -ne "  Checked $i/254 addresses...\r"
        fi
        
        # Check if it's a Gramofon (timeout per IP)
        local result=$(timeout 2 bash -c "$(declare -f check_gramofon login get_name jsonrpc_call); check_gramofon $ip" 2>/dev/null)
        
        if [ -n "$result" ]; then
            local sid=$(echo "$result" | cut -d'|' -f1)
            local name=$(echo "$result" | cut -d'|' -f2)
            echo -e "\n  ${GREEN}✓ Found: $ip - $name${NC}"
            echo "$ip|$sid|$name" >> /tmp/gramofon_devices.txt
            found=$((found + 1))
        fi
    done
    
    echo -e "\n\n${GREEN}Scan complete. Found $found device(s).${NC}\n"
}

# Main menu
show_menu() {
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         Gramofon LED Control Tool                     ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Usage
usage() {
    cat << EOF
Gramofon LED Control Script

Usage: 
  $0 <IP> <command>
  $0 scan <network_prefix>

Commands:
  on            Turn LED on
  off           Turn LED off
  status        Get LED status
  scan          Scan network for Gramofon devices

Examples:
  # Turn off LED on specific device
  $0 192.168.1.100 off
  
  # Turn on LED
  $0 192.168.1.100 on
  
  # Get LED status
  $0 192.168.1.100 status
  
  # Scan network
  $0 scan 192.168.1
  
  # Turn off all devices found on network
  $0 scan 192.168.1 | grep Found | while read line; do
      ip=\$(echo \$line | awk '{print \$3}')
      $0 \$ip off
  done

EOF
}

# Main logic
main() {
    local ip="$1"
    local command="$2"
    
    if [ -z "$ip" ]; then
        usage
        exit 1
    fi
    
    # Scan mode
    if [ "$ip" = "scan" ]; then
        if [ -z "$command" ]; then
            echo -e "${RED}Error: Network prefix required${NC}"
            echo "Example: $0 scan 192.168.1"
            exit 1
        fi
        
        rm -f /tmp/gramofon_devices.txt
        scan_network "$command"
        
        if [ -f /tmp/gramofon_devices.txt ]; then
            echo "Found devices:"
            cat /tmp/gramofon_devices.txt | while IFS='|' read ip sid name; do
                echo "  $ip - $name"
            done
        fi
        exit 0
    fi
    
    # Device control mode
    if [ -z "$command" ]; then
        echo -e "${RED}Error: Command required${NC}"
        usage
        exit 1
    fi
    
    # Login to device
    echo -e "${YELLOW}Connecting to $ip...${NC}"
    local sid=$(login "$ip")
    
    if [ -z "$sid" ]; then
        echo -e "${RED}✗ Failed to connect to device${NC}"
        echo "Make sure:"
        echo "  - Device is powered on"
        echo "  - Device is on the network"
        echo "  - IP address is correct"
        exit 1
    fi
    
    local name=$(get_name "$ip" "$sid")
    echo -e "${GREEN}✓ Connected to: $name ($ip)${NC}"
    echo ""
    
    # Execute command
    case "$command" in
        on)
            echo -e "${YELLOW}Turning LED on...${NC}"
            led_on "$ip" "$sid"
            echo -e "${GREEN}✓ LED turned ON${NC}"
            ;;
        off)
            echo -e "${YELLOW}Turning LED off...${NC}"
            led_off "$ip" "$sid"
            echo -e "${GREEN}✓ LED turned OFF${NC}"
            ;;
        status)
            echo -e "${YELLOW}Getting LED status...${NC}"
            local status=$(led_status "$ip" "$sid")
            echo "$status" | jq '.' 2>/dev/null || echo "$status"
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            usage
            exit 1
            ;;
    esac
}

main "$@"
