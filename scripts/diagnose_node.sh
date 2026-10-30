#!/usr/bin/env bash
# Quick VPS network connectivity & censorship diagnosis tool
set -e

TARGET_IP=${1:-""}

if [ -z "$TARGET_IP" ]; then
    echo "Usage: $0 <VPS_IP_OR_DOMAIN>"
    exit 1
fi

echo "=========================================="
echo " Anti-Censorship Node Diagnostic: $TARGET_IP"
echo "=========================================="

echo "[1/3] Testing ICMP Ping (3 packets)..."
if ping -c 3 -W 2 "$TARGET_IP" > /dev/null 2>&1; then
    echo "  -> [PASS] ICMP Ping responded. Server is alive and IP is not null-routed."
else
    echo "  -> [FAIL/WARN] ICMP Ping timed out. GFW may have blocked the IP or ICMP is disabled."
fi

echo "[2/3] Checking Common TCP Ports (22, 443, 2095)..."
for PORT in 22 443 2095; do
    if nc -z -v -w 2 "$TARGET_IP" $PORT > /dev/null 2>&1; then
        echo "  -> TCP Port $PORT: [OPEN / ACCESSIBLE]"
    else
        echo "  -> TCP Port $PORT: [BLOCKED / FILTERED / CLOSED]"
    fi
done

echo "[3/3] Diagnosis Summary:"
echo "  * If Ping works but TCP 443/8443 is blocked: Port blocked by GFW (change port/enable Reality)."
echo "  * If all ports & Ping timeout from CN but work from abroad: IP blocked (GFW Blacklist)."
echo "  * If UDP Hysteria drops packets after 10s: UDP QoS triggered (enable port-hopping 20000-50000)."
echo "=========================================="
