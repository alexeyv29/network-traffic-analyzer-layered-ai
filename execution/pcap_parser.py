"""
Directive 01: PCAP Pre-Processor
Parses a .pcap file and extracts network communication flows into a structured JSON.
"""
import os
import sys
import json
from collections import defaultdict

# Ensure scapy is available
try:
    from scapy.all import rdpcap, IP, TCP, UDP
except ImportError:
    print("[!] scapy not installed. Installing...")
    os.system(f"{sys.executable} -m pip install scapy")
    from scapy.all import rdpcap, IP, TCP, UDP

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(BASE_DIR, "tmp")
PCAP_FILE = os.path.join(TMP_DIR, "sample.pcap")
OUTPUT_FILE = os.path.join(TMP_DIR, "flows_summary.json")


def parse_pcap(pcap_path: str) -> dict:
    """Parse a pcap file and group packets into logical flows."""
    
    if not os.path.exists(pcap_path):
        raise FileNotFoundError(
            f"[!] PCAP file not found at: {pcap_path}\n"
            f"    Please place a sample capture file in the tmp/ directory."
        )
    
    print(f"[*] Reading PCAP file: {pcap_path}")
    packets = rdpcap(pcap_path)
    print(f"[*] Loaded {len(packets)} packets")
    
    # Group packets into flows: (src_ip, dst_ip, protocol)
    flows = defaultdict(lambda: {
        "packets": [],
        "total_bytes": 0,
        "start_time": None,
        "end_time": None,
        "dst_ports": set(),
    })
    
    for pkt in packets:
        if not pkt.haslayer(IP):
            continue
        
        ip_layer = pkt[IP]
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst
        
        # Determine protocol
        if pkt.haslayer(TCP):
            protocol = "TCP"
            dst_port = pkt[TCP].dport
        elif pkt.haslayer(UDP):
            protocol = "UDP"
            dst_port = pkt[UDP].dport
        else:
            protocol = str(ip_layer.proto)
            dst_port = 0
        
        flow_key = f"{src_ip} -> {dst_ip} [{protocol}]"
        flow = flows[flow_key]
        
        pkt_time = float(pkt.time)
        pkt_size = len(pkt)
        
        flow["packets"].append(pkt_time)
        flow["total_bytes"] += pkt_size
        flow["dst_ports"].add(dst_port)
        
        if flow["start_time"] is None or pkt_time < flow["start_time"]:
            flow["start_time"] = pkt_time
        if flow["end_time"] is None or pkt_time > flow["end_time"]:
            flow["end_time"] = pkt_time
    
    # Build output structure
    flows_list = []
    for flow_key, data in flows.items():
        duration = round(data["end_time"] - data["start_time"], 4) if data["start_time"] != data["end_time"] else 0
        
        flows_list.append({
            "flow": flow_key,
            "total_packets": len(data["packets"]),
            "total_bytes": data["total_bytes"],
            "duration_seconds": duration,
            "destination_ports": sorted(list(data["dst_ports"])),
            "avg_packet_size": round(data["total_bytes"] / len(data["packets"]), 2),
        })
    
    # Sort by packet count descending
    flows_list.sort(key=lambda x: x["total_packets"], reverse=True)
    
    return {
        "source_file": os.path.basename(pcap_path),
        "total_packets_parsed": len(packets),
        "total_flows": len(flows_list),
        "flows": flows_list,
    }


def main():
    print("=" * 60)
    print("  PCAP Pre-Processor — Directive 01")
    print("=" * 60)
    
    result = parse_pcap(PCAP_FILE)
    
    os.makedirs(TMP_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n[+] SUCCESS: Parsed {result['total_packets_parsed']} packets into {result['total_flows']} flows")
    print(f"[+] Output saved to: {OUTPUT_FILE}")
    
    # Print summary
    print("\n--- Flow Summary ---")
    for flow in result["flows"][:5]:
        print(f"  {flow['flow']}: {flow['total_packets']} pkts, {flow['total_bytes']} bytes, {flow['duration_seconds']}s")
    if len(result["flows"]) > 5:
        print(f"  ... and {len(result['flows']) - 5} more flows")


if __name__ == "__main__":
    main()
