# Directive 01: Build PCAP Pre-Processor

**Goal:** Write a Python script that parses a `.pcap` file and outputs a summarized JSON file containing network communication flows, which will eventually be fed to an LLM.

**Execution Steps:**
1. Check the `/.tmp/` directory for a test file named `sample.pcap`. If it does not exist, pause and instruct the user to place a small sample capture file there before continuing.
2. Write a Python script named `pcap_parser.py` inside the `/execution/` directory.
3. Use a suitable Python library (like `scapy` or `pyshark`) to read `/.tmp/sample.pcap`.
4. The script must group the raw packets into logical communication flows (e.g., Source IP -> Dest IP, Protocol).
5. For each flow, calculate and extract: total packets, duration (time taken), protocol used (TCP/UDP), and basic payload size. 
6. Save this structured data into a file named `flows_summary.json` inside the `/.tmp/` directory.
7. Run the script. **Self-Anneal Rule:** If you are missing libraries, install them. If the parsing fails, read the error, fix `pcap_parser.py`, and run it again until `flows_summary.json` is successfully generated.