#!/usr/bin/env bash
# Configure iptables NAT Port Hopping for Hysteria 2
# Enables UDP port range 20000-50000 redirecting to target Hysteria port

TARGET_PORT=${1:-28443}
HOPPING_RANGE=${2:-"20000:50000"}

echo "[+] Setting up Port Hopping: UDP $HOPPING_RANGE -> UDP $TARGET_PORT"

# Check if iptables is available
if ! command -v iptables &> /dev/null; then
    echo "[-] iptables command not found, please install iptables."
    exit 1
fi

# Add NAT redirect rules
iptables -t nat -A PREROUTING -p udp --dport "$HOPPING_RANGE" -j REDIRECT --to-ports "$TARGET_PORT"
iptables -t nat -A PREROUTING -p udp --dport 443 -j REDIRECT --to-ports "$TARGET_PORT" 2>/dev/null || true

echo "[+] Port hopping iptables rules applied successfully."
echo "[+] Active NAT PREROUTING rules:"
iptables -t nat -L PREROUTING -n -v --line-numbers | grep -E "REDIRECT|to-ports"
