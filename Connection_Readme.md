# Remote Access and Networking

## Overview

The Refrigeration-Sensor-Hub is designed for fully unattended deployment inside a refrigerated transport vehicle.

Because the Raspberry Pi operates remotely over a mobile data connection, direct public SSH exposure is not practical or secure. Mobile providers typically place devices behind Carrier Grade NAT (CGNAT), preventing inbound access using public IP addresses.

To solve this, the platform uses a secure private VPN overlay.

Remote access architecture:

```text
Laptop
      ↓
Tailscale VPN
      ↓
Internet
      ↓
4G Mobile Network
      ↓
SIM7600G-H USB Modem
      ↓
Raspberry Pi
```

This enables secure SSH access to the Raspberry Pi from anywhere without:

- public IP configuration
- router port forwarding
- Dynamic DNS
- exposing SSH to the public internet

---

# Networking Architecture

Linux networking stack:

```text
Netplan
   ↓
NetworkManager
   ↓
ModemManager
   ↓
SIM7600 USB Modem
   ↓
4G Mobile Network
```

Component responsibilities:

### Netplan

Provides baseline interface definitions.

Interfaces:

```text
eth0   Ethernet
wlan0  Wi-Fi
```

---

### NetworkManager

Manages connection profiles:

- Ethernet
- Wi-Fi
- GSM / 4G mobile profiles

Useful commands:

```bash
nmcli device status
nmcli connection show
nmcli connection show --active
```

---

### ModemManager

Handles:

- modem detection
- SIM card management
- APN configuration
- WWAN connectivity

Useful command:

```bash
mmcli -L
```

Expected modem:

```text
SIMCOM_SIM7600G-H
```

---

### Tailscale

Provides secure remote VPN access.

VPN interface:

```text
tailscale0
```

---

# Active Network Interfaces

```text
eth0        Ethernet
wlan0       Wi-Fi
cdc-wdm0    modem control interface
wwan0       4G data interface
tailscale0  VPN tunnel
```

Check interfaces:

```bash
ip a
```

Check routing:

```bash
ip route
```

---

# 4G Mobile Connectivity

## Hardware

```text
SIM7600G-H USB LTE modem
giffgaff SIM card
```

Recommended USB arrangement:

```text
SIM7600 → Raspberry Pi USB 2.0 port (Black ports)
```

---

## Modem Configuration

Create / modify the mobile connection profile:

```bash
sudo nmcli connection modify giffgaff-4g connection.autoconnect yes
sudo nmcli connection modify giffgaff-4g connection.autoconnect-retries -1
sudo nmcli connection modify giffgaff-4g gsm.apn giffgaff.com
sudo nmcli connection modify giffgaff-4g ipv4.route-metric 100
sudo nmcli connection modify giffgaff-4g ipv6.method ignore
```

Reconnect profile:

```bash
sudo nmcli connection down giffgaff-4g
sudo nmcli connection up giffgaff-4g
```

---

## Validation

Check active connections:

```bash
nmcli connection show --active
```

Expected:

```text
giffgaff-4g
tailscale0
```

Check modem:

```bash
mmcli -L
```

Expected:

```text
SIMCOM_SIM7600G-H
```

Check USB devices:

```bash
lsusb
```

Expected modem detection:

```text
Qualcomm / Option SimTech
```

Check routes:

```bash
ip route
```

Expected:

```text
default via <mobile gateway> dev wwan0
```

---

# Tailscale Remote Access

## Raspberry Pi Installation

Install:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

Enable service:

```bash
sudo systemctl enable tailscaled
sudo systemctl start tailscaled
```

Authenticate:

```bash
sudo tailscale up --ssh
```

Open the provided browser login URL and authenticate using your Tailscale account.

Verify:

```bash
tailscale status
```

Expected:

```text
pi-sensorhub
```

---

## Laptop Installation

Install Tailscale on engineering laptop.

Linux:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Windows:

Install Tailscale desktop client and authenticate using the same account.

---

# Remote SSH Access

Connect by hostname:

```bash
ssh pi@pi-sensorhub
```

or:

```bash
tailscale ssh pi@pi-sensorhub
```

Connect by Tailscale IP:

```bash
ssh pi@100.x.x.x
```
