# Anti-Censorship Matrix (抗封锁防失联多云节点矩阵与统一智能分流系统)

[![GitHub License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Protocol](https://img.shields.io/badge/protocols-Hysteria2%20%7C%20VLESS--Reality%20%7C%20VMess-success)](https://github.com/xiqing21/anti-censorship-matrix)

<p align="center">
  <img src="cover.jpg" width="100%" alt="Anti-Censorship Matrix Architecture"/>
</p>
[![Antigravity Skill](https://img.shields.io/badge/agent--skill-compatible-orange)](SKILL.md)

生产级、跨多云厂商互备（Oracle 永久免费 + 搬瓦工 + 绿云等）、多协议容灾（Hysteria 2 UDP 端口跳跃 + VLESS-Reality/TLS + VMess）的自建科学上网体系。

核心设计哲学：**“永远不要把所有鸡蛋放在同一个篮子里”**。单一机房、单一协议、单点订阅在防火墙（GFW）的周期性封锁下必定遭遇断连。通过本套矩阵方案，无论 GFW 是封锁特定端口、封杀特定机房 IP，还是对特定协议干扰，都能实现“自动分流、无感容灾”。

---

## 架构拓扑概览

```
                            [ 用户终端 (小火箭 / Clash / Surge) ]
                                            │
                                  (统一自适应智能订阅链接)
                                            ▼
                           🇸🇬 甲骨文 (Oracle Singapore)
                       [ 永久免费 / 订阅中枢 / ThreadingHTTPServer ]
                                            │
                ┌───────────────────────────┼───────────────────────────┐
                ▼                           ▼                           ▼
    🇸🇬 甲骨文 (免费兜底)               🇯🇵 绿云 (日本东京主力)         🇺🇸 搬瓦工 (美西容灾)
    • Hysteria 2 (UDP 443)      • Hysteria 2 (极速低延迟)       • Hysteria 2 (端口跳跃)
    • VLESS-TLS (XTLS-Vision)   • VLESS-Reality (反探测)        • NAT 20000-50000
    • VMess-WS (备用通道)       • 纯净新 IP，延迟 <50ms         • 规避黑名单 QoS 压制
```

---

## 核心特性

1. **多厂商多协议互备**：
   * **TCP 协议族**：VLESS-Reality（借用真实巨头域名证书如 AMD / Amazon，无私钥自签名特征）。
   * **UDP 协议族**：Hysteria 2（基于标准 QUIC，高丢包网络提速，自带 Masquerade 伪装网站）。
2. **Hysteria 2 动态端口跳跃（Port Hopping）**：
   * 针对 GFW 对单一 UDP 443 端口的精准 QoS 限速与丢包压制，通过 `iptables` NAT 将 `20000:50000` 端口段映射至主程序，让客户端在数万个端口中动态随机穿透。
3. **高并发多线程防卡死订阅分发**：
   * 采用 `ThreadingHTTPServer`，内嵌 15 秒 Socket 熔断机制，彻底解决公网恶意爬虫慢速握手导致整个订阅服务瘫痪的历史痛点。
   * 支持客户端 User-Agent 智能自适应：
     * **Shadowrocket / v2rayN / Surge** ➔ 自动下发 Base64 明文节点；
     * **Clash / Meta / FLClash / Verge** ➔ 自动生成包含智能分流规则的完整 YAML。
4. **业务场景精准分流**：
   * 🪙 **加密货币 (Binance/OKX/Metamask)** ➔ 绑定日本绿云（极低延迟、固定干净 IP 防止风控）。
   * 🤖 **国际 AI (ChatGPT/Claude/Perplexity)** ➔ 智能调度至新加坡/美西。
   * 🎯 **国内流量 (网银/微信/淘宝/B站)** ➔ 走 `DIRECT` 直连不消耗节点流量。
   * 🐟 **漏网之鱼** ➔ 自动延迟探针测速（`url-test`）切换最优线路。

---

## 快速上手与部署流程

### 第一步：准备域名与 DNS 解析
1. 申请一个域名（可在 Namesilo、Cloudflare Registrar 等平台）。
2. 在 Cloudflare 中为三台服务器分别配置子域名解析（**务必关闭橙色云朵，仅 DNS 解析**）：
   * `oracle.yourdomain.xyz` ➔ 甲骨文 IPv4
   * `ly.yourdomain.xyz` ➔ 绿云 IPv4
   * `bwg.yourdomain.xyz` ➔ 搬瓦工 IPv4

### 第二步：部署主控面板与节点
在各 VPS 上安装轻量级面板 S-UI 或 3X-UI：
```bash
# S-UI 安装（基于 Sing-box）
bash <(curl -Ls https://raw.githubusercontent.com/Teminuosi/s-ui/master/install.sh)

# 或 3X-UI 安装（基于 Xray）
bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
```

### 第三步：配置 Hysteria 2 动态端口跳跃（抗封锁核心）
在容易被重点盯防的服务器（如搬瓦工）上执行：
```bash
# 下载本项目脚本
chmod +x scripts/setup_port_hopping.sh
sudo ./scripts/setup_port_hopping.sh 28443 "20000:50000"
```
在客户端链接或订阅中指定 `mport=20000-50000`。

### 第四步：部署统一订阅服务（甲骨文永久免费机）
1. 将 `scripts/gen_sub.py` 复制到甲骨文服务器 `/usr/local/bin/unified_sub.py`。
2. 配置 systemd 守护进程：
```ini
[Unit]
Description=Universal Subscription Service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /usr/local/bin/unified_sub.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload && sudo systemctl enable --now unified-sub
```

---

## 常见排错速查手册 (FAQ)

### 1. 甲骨文（Oracle Cloud）节点搭建完成却全红超时？
* **原因**：甲骨文实例外层有一层 **OCI 控制台安全列表（Security List）**，默认只放行了 22 端口，外部 TCP/UDP 全被阻断。
* **解决**：进入 Oracle Cloud 控制台 ➔ “计算” ➔ “实例” ➔ 点击子网 ➔ “默认安全列表” ➔ 添加入站规则：源 `0.0.0.0/0`，IP 协议选择 `所有协议`，目标端口留空。

### 2. 小火箭导入节点显示“萨摩亚国旗 (🇼🇸)”？
* **原因**：当节点使用 WebSocket（`ws`）协议传输时，小火箭的历史解析器将其误识别为萨摩亚的 ISO 双字国家代码 `WS`。
* **解决**：在订阅节点名称开头显式加上 Emoji 和中文国家名称（例如 `🇸🇬 甲骨文[新加坡]`），小火箭会优先按文本渲染。

### 3. 搬瓦工 Hysteria 2 测速显示 300ms，连上却打不开网页？
* **原因**：IP 已经被 GFW 放入单向黑名单，常规 TCP 已死；且 443 UDP 端口被深度包检测识别，触发了精确限速丢包。
* **解决**：将 Hysteria 2 主端口更换为冷门高位端口（如 `28443`），并开启 `20000:50000` 动态端口跳跃。

---

## 贡献与反馈

欢迎提交 Issue 和 Pull Request！如果你觉得本方案对你有帮助，请给项目点个 ⭐️ **Star**！
