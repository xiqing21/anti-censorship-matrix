#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Multi-VPS Subscription Generator & Distributor
Supports:
  - Base64 plain text (Shadowrocket / v2rayN / Surge)
  - Clash / Meta / FLClash (Full YAML with smart rule groups)
Features:
  - ThreadingHTTPServer for high concurrency
  - 15s socket timeout protection against scanner exhaustion
  - Automatic User-Agent recognition
"""

import http.server
import ssl
import urllib.parse
import base64
import json
import yaml
import threading
import socket
import os
import sys

# Global timeout to eliminate hanging scanner connections
socket.setdefaulttimeout(15.0)

PORT_HTTP = int(os.environ.get("PORT_HTTP", 80))
PORT_HTTPS = int(os.environ.get("PORT_HTTPS", 2096))
CERT = os.environ.get("CERT_PATH", "/root/cert/yourdomain.xyz/fullchain.pem")
KEY = os.environ.get("KEY_PATH", "/root/cert/yourdomain.xyz/privkey.pem")

# Example node list (Replace domains, ports, and credentials with your own)
RAW_NODES = [
    # 🇸🇬 Oracle Singapore (Permanent Free)
    {
        "name": "🇸🇬 甲骨文[新加坡]-Hysteria2-UDP极速-永久有效",
        "type": "hysteria2",
        "region": "SG",
        "uri": f"hysteria2://your_password@oracle.yourdomain.xyz:443/?sni=oracle.yourdomain.xyz&insecure=0#{urllib.parse.quote('🇸🇬 甲骨文[新加坡]-Hysteria2-UDP极速-永久有效')}",
        "clash": {
            "name": "🇸🇬 甲骨文[新加坡]-Hysteria2-UDP极速-永久有效",
            "type": "hysteria2",
            "server": "oracle.yourdomain.xyz",
            "port": 443,
            "password": "your_password",
            "sni": "oracle.yourdomain.xyz",
            "skip-cert-verify": False,
        }
    },
    {
        "name": "🇸🇬 甲骨文[新加坡]-VLESS-TLS极速-永久有效",
        "type": "vless",
        "region": "SG",
        "uri": f"vless://your-uuid@oracle.yourdomain.xyz:443?alpn=h2%2Chttp%2F1.1&encryption=none&flow=xtls-rprx-vision&fp=chrome&security=tls&sni=oracle.yourdomain.xyz&type=tcp#{urllib.parse.quote('🇸🇬 甲骨文[新加坡]-VLESS-TLS极速-永久有效')}",
        "clash": {
            "name": "🇸🇬 甲骨文[新加坡]-VLESS-TLS极速-永久有效",
            "type": "vless",
            "server": "oracle.yourdomain.xyz",
            "port": 443,
            "uuid": "your-uuid",
            "network": "tcp",
            "tls": True,
            "udp": True,
            "flow": "xtls-rprx-vision",
            "client-fingerprint": "chrome",
            "servername": "oracle.yourdomain.xyz",
            "alpn": ["h2", "http/1.1"]
        }
    },
    # 🇯🇵 GreenCloud Tokyo (Clean IP / Low Latency)
    {
        "name": "🇯🇵 绿云[日本东京]-Hysteria2-UDP极速-年付有效",
        "type": "hysteria2",
        "region": "JP",
        "uri": f"hysteria2://your_password@ly.yourdomain.xyz:443/?sni=ly.yourdomain.xyz&insecure=0#{urllib.parse.quote('🇯🇵 绿云[日本东京]-Hysteria2-UDP极速-年付有效')}",
        "clash": {
            "name": "🇯🇵 绿云[日本东京]-Hysteria2-UDP极速-年付有效",
            "type": "hysteria2",
            "server": "ly.yourdomain.xyz",
            "port": 443,
            "password": "your_password",
            "sni": "ly.yourdomain.xyz",
            "skip-cert-verify": False,
        }
    },
    {
        "name": "🇯🇵 绿云[日本东京]-VLESS-Reality极速-年付有效",
        "type": "vless",
        "region": "JP",
        "uri": f"vless://your-uuid@ly.yourdomain.xyz:10522?encryption=none&flow=xtls-rprx-vision&fp=chrome&pbk=reality_public_key&security=reality&sid=c6&sni=www.amd.com&spx=%2F&type=tcp#{urllib.parse.quote('🇯🇵 绿云[日本东京]-VLESS-Reality极速-年付有效')}",
        "clash": {
            "name": "🇯🇵 绿云[日本东京]-VLESS-Reality极速-年付有效",
            "type": "vless",
            "server": "ly.yourdomain.xyz",
            "port": 10522,
            "uuid": "your-uuid",
            "network": "tcp",
            "tls": True,
            "udp": True,
            "flow": "xtls-rprx-vision",
            "client-fingerprint": "chrome",
            "servername": "www.amd.com",
            "reality-opts": {
                "public-key": "reality_public_key",
                "short-id": "c6"
            }
        }
    },
    # 🇺🇸 BandwagonHost US (Port-Hopping Anti-Censorship)
    {
        "name": "🇺🇸 搬瓦工[美国]-Hysteria2-UDP抗封锁-备用有效",
        "type": "hysteria2",
        "region": "US",
        "uri": f"hysteria2://your_password@bwg.yourdomain.xyz:28443/?mport=20000-50000&sni=bwg.yourdomain.xyz&insecure=0#{urllib.parse.quote('🇺🇸 搬瓦工[美国]-Hysteria2-UDP抗封锁-备用有效')}",
        "clash": {
            "name": "🇺🇸 搬瓦工[美国]-Hysteria2-UDP抗封锁-备用有效",
            "type": "hysteria2",
            "server": "bwg.yourdomain.xyz",
            "port": 28443,
            "ports": "20000-50000",
            "password": "your_password",
            "sni": "bwg.yourdomain.xyz",
            "skip-cert-verify": False,
        }
    }
]

def build_base64():
    uris = [node["uri"] for node in RAW_NODES]
    return base64.b64encode("\n".join(uris).encode("utf-8"))

def build_clash():
    proxies = [node["clash"] for node in RAW_NODES]
    all_names = [p["name"] for p in proxies]
    jp_names = [p["name"] for p in proxies if "绿云" in p["name"]]
    us_names = [p["name"] for p in proxies if "搬瓦工" in p["name"]]
    sg_names = [p["name"] for p in proxies if "甲骨文" in p["name"]]

    config = {
        "port": 7890,
        "socks-port": 7891,
        "allow-lan": False,
        "mode": "rule",
        "log-level": "info",
        "proxies": proxies,
        "proxy-groups": [
            {"name": "🚀 节点选择", "type": "select", "proxies": ["♻️ 自动优选"] + all_names + ["DIRECT"]},
            {"name": "♻️ 自动优选", "type": "url-test", "url": "http://www.gstatic.com/generate_204", "interval": 300, "tolerance": 50, "proxies": all_names},
            {"name": "🤖 国际AI", "type": "select", "proxies": us_names + sg_names + jp_names + ["🚀 节点选择"]},
            {"name": "🪙 加密货币", "type": "select", "proxies": jp_names + sg_names + us_names + ["🚀 节点选择"]},
            {"name": "📺 国际媒体", "type": "select", "proxies": ["🚀 节点选择", "♻️ 自动优选"] + all_names},
            {"name": "🎯 国内直连", "type": "select", "proxies": ["DIRECT", "🚀 节点选择"]},
            {"name": "🐟 漏网之鱼", "type": "select", "proxies": ["🚀 节点选择", "DIRECT"]}
        ],
        "rules": [
            "GEOIP,lan,🎯 国内直连,no-resolve",
            "DOMAIN-KEYWORD,openai,🤖 国际AI",
            "DOMAIN-KEYWORD,chatgpt,🤖 国际AI",
            "DOMAIN-KEYWORD,anthropic,🤖 国际AI",
            "DOMAIN-KEYWORD,claude,🤖 国际AI",
            "DOMAIN-KEYWORD,binance,🪙 加密货币",
            "DOMAIN-KEYWORD,okx,🪙 加密货币",
            "DOMAIN-KEYWORD,tradingview,🪙 加密货币",
            "DOMAIN-KEYWORD,youtube,📺 国际媒体",
            "DOMAIN-KEYWORD,netflix,📺 国际媒体",
            "DOMAIN-SUFFIX,cn,🎯 国内直连",
            "GEOIP,CN,🎯 国内直连",
            "MATCH,🐟 漏网之鱼"
        ]
    }
    return yaml.dump(config, allow_unicode=True, sort_keys=False).encode("utf-8")

class SubHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def do_HEAD(self): self.do_GET()
    def do_GET(self):
        ua = self.headers.get("User-Agent", "").lower()
        path = self.path.lower()
        is_clash = any(k in ua for k in ["clash", "meta", "flclash", "verge"]) or "/clash" in path

        data = build_clash() if is_clash else build_base64()
        self.send_response(200)
        self.send_header("Content-Type", "application/yaml; charset=utf-8" if is_clash else "text/plain; charset=utf-8")
        self.send_header("Profile-Update-Interval", "24")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def log_message(self, format, *args):
        pass

def main():
    t_http = threading.Thread(
        target=lambda: http.server.ThreadingHTTPServer(("0.0.0.0", PORT_HTTP), SubHandler).serve_forever(),
        daemon=True
    )
    t_http.start()
    print(f"[+] HTTP Subscription Service running on port {PORT_HTTP}...")

    if os.path.exists(CERT) and os.path.exists(KEY):
        srv_https = http.server.ThreadingHTTPServer(("0.0.0.0", PORT_HTTPS), SubHandler)
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(certfile=CERT, keyfile=KEY)
        srv_https.socket = ssl_ctx.wrap_socket(srv_https.socket, server_side=True)
        print(f"[+] HTTPS Subscription Service running on port {PORT_HTTPS}...")
        srv_https.serve_forever()
    else:
        print("[-] Cert/Key not found, HTTPS disabled, serving HTTP only.")
        t_http.join()

if __name__ == "__main__":
    main()
