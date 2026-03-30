"""
Generate a sample .pcap file for testing the Network Traffic Analyzer.
Creates realistic network traffic with multiple protocols and flows.
"""
import os
import sys

# Ensure scapy is available
try:
    from scapy.all import (
        Ether, IP, TCP, UDP, DNS, DNSQR, Raw, wrpcap
    )
except ImportError:
    print("[!] scapy not installed. Installing...")
    os.system(f"{sys.executable} -m pip install scapy")
    from scapy.all import (
        Ether, IP, TCP, UDP, DNS, DNSQR, Raw, wrpcap
    )

import random
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(BASE_DIR, "tmp")
os.makedirs(TMP_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(TMP_DIR, "sample.pcap")

packets = []
base_time = time.time()

# --- Flow 1: HTTP-like TCP traffic (Client -> Web Server) ---
for i in range(25):
    pkt = (
        Ether() /
        IP(src="192.168.1.100", dst="93.184.216.34") /
        TCP(sport=random.randint(49152, 65535), dport=80, flags="PA") /
        Raw(load=f"GET /page{i} HTTP/1.1\r\nHost: example.com\r\n\r\n".encode())
    )
    pkt.time = base_time + i * 0.15
    packets.append(pkt)

# Response packets
for i in range(25):
    pkt = (
        Ether() /
        IP(src="93.184.216.34", dst="192.168.1.100") /
        TCP(sport=80, dport=random.randint(49152, 65535), flags="PA") /
        Raw(load=f"HTTP/1.1 200 OK\r\nContent-Length: {random.randint(200,5000)}\r\n\r\n<html>Response {i}</html>".encode())
    )
    pkt.time = base_time + i * 0.15 + 0.05
    packets.append(pkt)

# --- Flow 2: DNS queries ---
domains = ["example.com", "google.com", "github.com", "api.openai.com", "cdn.jsdelivr.net"]
for i, domain in enumerate(domains):
    pkt = (
        Ether() /
        IP(src="192.168.1.100", dst="8.8.8.8") /
        UDP(sport=random.randint(49152, 65535), dport=53) /
        DNS(rd=1, qd=DNSQR(qname=domain))
    )
    pkt.time = base_time + i * 0.5
    packets.append(pkt)

# --- Flow 3: HTTPS traffic (Client -> API Server) ---
for i in range(15):
    pkt = (
        Ether() /
        IP(src="192.168.1.100", dst="142.250.185.206") /
        TCP(sport=random.randint(49152, 65535), dport=443, flags="PA") /
        Raw(load=os.urandom(random.randint(100, 1500)))
    )
    pkt.time = base_time + 2 + i * 0.2
    packets.append(pkt)

# --- Flow 4: Internal LAN communication ---
for i in range(10):
    pkt = (
        Ether() /
        IP(src="192.168.1.100", dst="192.168.1.1") /
        UDP(sport=random.randint(49152, 65535), dport=5353) /
        Raw(load=f"mDNS query {i}".encode())
    )
    pkt.time = base_time + 3 + i * 0.3
    packets.append(pkt)

# --- Flow 5: Suspicious high-volume traffic (simulated scan) ---
for i in range(20):
    pkt = (
        Ether() /
        IP(src="10.0.0.55", dst="192.168.1.100") /
        TCP(sport=random.randint(1024, 65535), dport=random.choice([22, 23, 80, 443, 3389, 8080]), flags="S")
    )
    pkt.time = base_time + 4 + i * 0.05
    packets.append(pkt)

# Sort by timestamp
packets.sort(key=lambda p: p.time)

wrpcap(OUTPUT_FILE, packets)
print(f"[+] Generated {len(packets)} packets -> {OUTPUT_FILE}")
