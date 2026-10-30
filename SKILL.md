---
name: anti-censorship-matrix
description: 跨多云架构的多节点多协议抗封锁防失联方案（S-UI/3X-UI + Hysteria2 + VLESS-Reality/TLS + 统一智能订阅聚合）。涵盖域名解析申请、Oracle/搬瓦工/绿云等多VPS集群互备部署、端口跳跃抗封锁、国内智能分流与防探测排错指南。
---

# Anti-Censorship Matrix（抗封锁矩阵节点与统一订阅集成技能）

本 Skill 沉淀并封装了高可用、跨多云厂商（Oracle 永久免费 + 搬瓦工 + 绿云等）、多协议互备（Hysteria 2 UDP + VLESS-Reality/TLS + VMess）的生产级自建代理体系。

核心设计哲学：**“永远不要把所有鸡蛋放在同一个篮子里”**。单一机房、单一协议、单点订阅在防火墙（GFW）的周期性地毯式封锁下必定遭遇断连。通过本套矩阵方案，无论 GFW 是封锁特定端口、封杀特定 IP，还是干扰 TLS 握手，都能实现“自动分流、无感容灾”。

---

## 目录结构与快速工具

* `scripts/gen_sub.py`：高性能多线程订阅生成器模板，内置 Clash 规则分组（Crypto/AI/媒体/直连/漏网之鱼）与 Base64 小火箭自适应。
* `scripts/setup_hy2.sh`：一键部署 Hysteria 2 并开启 `iptables` 动态端口跳跃（Port Hopping）。
* `scripts/diagnose_node.sh`：国内/国际双向网络诊断脚本（精准区分 IP 被墙 vs 端口被封 vs 服务挂掉）。

---

## 一、网络封锁底层原理与技术破局

### 1. GFW 封锁的 3 个阶段演进
1. **第一阶段：针对 VMess/老旧协议的主动探测与特征阻断**
   * *现象*：VMess-WS、Shadowsocks 几乎全灭。
   * *原因*：TLS 握手特征或流量熵值异常被 GFW 深度包检测（DPI）识别，直接向客户端或服务端注入 TCP RST 重置包。
2. **第二阶段：单向墙与黑名单 IP 封杀**
   * *现象*：境外互相访问正常（从国外 ping/curl 都是 200），但国内直连全部丢包。
   * *原因*：机房（如搬瓦工、DMIT）IP 进入 GFW 路由黑名单，骨干网出口直接丢弃 TCP 握手。
3. **第三阶段：UDP 端口精准压制与 QoS**
   * *现象*：Hysteria 2 节点测速显示 300ms（握手包通过），但一刷推特或油管就卡死断网。
   * *原因*：443 等常用 UDP 端口被重点盯防，一旦检测到持续大流量 UDP QUIC 数据，触发精准丢包（Packet Drop），丢包率飙升至 80%~100%。

### 2. 矩阵破解之道
* **协议隔离**：
  * **Hysteria 2（UDP）**：抗高丢包，利用伪装网站（Masquerade）和动态高位端口/端口跳跃（Port Hopping）击穿 QoS。
  * **VLESS-Reality / TLS（TCP）**：无私钥证书借用（如 AMD/Amazon 真实 SNI），消除证书特征。
* **厂商与机房隔离**：
  * **🇸🇬 甲骨文（新加坡）**：永久免费，作为中枢订阅服务 + 免费备用通道。
  * **🇯🇵 绿云（日本东京）**：全新干净 IP，低延迟（<50ms 骨干网），主力生产节点。
  * **🇺🇸 搬瓦工（美西）**：老牌机房，作为大带宽下载与容灾备用。

---

## 二、多节点集群部署全流程指南

### 1. 域名与 DNS 解析
* **获取域名**：可在 Namesilo、Cloudflare Registrar 或免费二级域名平台申请。
* **解析配置**（关闭 Cloudflare 橙色云朵，仅 DNS 解析）：
  * `of.yourdomain.xyz` ➔ 甲骨文 IPv4
  * `ly.yourdomain.xyz` ➔ 绿云 IPv4
  * `bwg.yourdomain.xyz` ➔ 搬瓦工 IPv4
* **证书申请**：使用 `acme.sh` 申请泛域名或单域名 ECC 证书：
  ```bash
  curl https://get.acme.sh | sh
  ~/.acme.sh/acme.sh --register-account -m your@email.com
  ~/.acme.sh/acme.sh --issue -d of.yourdomain.xyz --standalone
  ```

### 2. 面板选型与安装（S-UI / 3X-UI）
* **主控面板推荐**：S-UI（基于 Sing-box，轻量级）或 3X-UI（基于 Xray，Web 体验成熟）。
* **一键安装**：
  ```bash
  # S-UI
  bash <(curl -Ls https://raw.githubusercontent.com/Teminuosi/s-ui/master/install.sh)
  # 或 3X-UI
  bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
  ```

### 3. Hysteria 2 配置与动态端口跳跃（抗封锁核心）
不要将 Hysteria 2 仅暴露在单一 `443` 端口上！必须配置防火墙 NAT 端口转发实现端口跳跃：

1. **主配置文件 `/etc/hysteria/config.yaml`**：
   ```yaml
   listen: :28443
   tls:
     cert: /path/to/fullchain.pem
     key: /path/to/privkey.pem
   auth:
     type: password
     password: "YourStrongPassword"
   masquerade:
     type: proxy
     proxy:
       url: https://news.ycombinator.com/
       rewriteHost: true
   outbounds:
     - name: default
       type: direct
   ```
2. **开启多端口跳跃（Port Hopping）**：
   ```bash
   iptables -t nat -A PREROUTING -p udp --dport 20000:50000 -j REDIRECT --to-ports 28443
   iptables -t nat -A PREROUTING -p udp --dport 443 -j REDIRECT --to-ports 28443
   ```
3. **客户端链接参数**：
   ```text
   hysteria2://password@domain:28443/?mport=20000-50000&sni=domain#节点备注
   ```

---

## 三、踩坑与排错权威速查手册（FAQ）

### 坑 1：甲骨文（Oracle Cloud）节点全红 / 超时？
* **原因**：甲骨文系统外层还有一层 **OCI 安全列表（Security List）**，默认只放行了 SSH (22)。即使系统内 iptables 全开，外部流量依然会被阻挡！
* **解决步骤**：
  1. 登录 Oracle Cloud 控制台 ➔ “计算 (Compute)” ➔ “实例 (Instances)” ➔ 点击机器名。
  2. 点击所挂载的“虚拟云网络 (VCN)” ➔ “子网 (Subnet)” ➔ 点击“默认安全列表 (Default Security List)”。
  3. 点击“添加入站规则 (Add Ingress Rules)”：
     * 源 CIDR：`0.0.0.0/0`
     * IP 协议：`所有协议`（或针对性添加 `UDP` 和 `TCP`）
     * 目标端口：留空代表所有端口开放。

### 坑 2：小火箭导入 VMess 节点显示“萨摩亚国旗（🇼🇸）”？
* **原因**：小火箭客户端的一个历史解析 Bug——当节点传输协议标注为 `"net": "ws"`（WebSocket）时，其简写与南太平洋岛国萨摩亚（Samoa）的双字国家代码 `WS` 重合，误判定为国旗。
* **解决**：在备注名最前端显式添加国旗 Emoji 和中文国名（如 `🇸🇬 甲骨文[新加坡]`、`🇯🇵 绿云[日本东京]`），客户端会优先使用显式标注。

### 坑 3：自建订阅链接偶尔更新超时“网络连接失败”？
* **原因**：公网扫描机器人会向 80/2096 端口发送恶意慢速请求。如果自写 Python 订阅服务是单线程同步阻塞模式，一个恶意连接就会卡死整个进程。
* **解决**：必须使用高并发多线程架构（`http.server.ThreadingHTTPServer`），并配置全局 Socket 15 秒超时熔断。

---

## 四、统一智能分流订阅服务架构

将所有 VPS 节点聚合到甲骨文云上托管的独立订阅服务中（支持 Base64 与 Clash 自动自适应识别）：

### 智能分组策略配置（Clash 核心）：
* 🚀 **节点选择**：全局手动总控
* ♻️ **自动优选**：定时健康检查，自动切换最低延迟节点
* 🤖 **国际AI**：ChatGPT / Claude / Perplexity 走美国/新加坡/日本节点
* 🪙 **加密货币**：Binance / OKX / Metamask / TradingView 优选日本绿云（交易低延迟不串 IP）
* 📺 **国际媒体**：YouTube / Netflix 流媒体自动调度
* 🎯 **国内直连**：百度 / 微信 / 淘宝 / 银行网银等内网走 DIRECT
* 🐟 **漏网之鱼**：未匹配规则的海外流量默认代理
