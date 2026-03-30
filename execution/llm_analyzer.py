"""
Directive 02: AI Analyst (LLM Integration)
Reads parsed network data and uses Gemini to generate insights and Mermaid.js diagrams.
"""
import os
import sys
import json

# Ensure dependencies
for pkg in ["google-generativeai", "python-dotenv"]:
    try:
        if pkg == "google-generativeai":
            import google.generativeai
        elif pkg == "python-dotenv":
            import dotenv
    except ImportError:
        print(f"[!] {pkg} not installed. Installing...")
        os.system(f"{sys.executable} -m pip install {pkg}")

from dotenv import load_dotenv
import google.generativeai as genai

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(BASE_DIR, "tmp")
INPUT_FILE = os.path.join(TMP_DIR, "flows_summary.json")
OUTPUT_FILE = os.path.join(TMP_DIR, "analysis_result.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")


def analyze_with_llm(flows_data: dict) -> dict:
    """Send parsed flow data to Gemini and get insights + Mermaid diagram."""
    
    # Load API key
    load_dotenv(ENV_FILE)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("[!] GEMINI_API_KEY not found in .env file!")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Build the prompt
    flows_json = json.dumps(flows_data, indent=2)
    
    prompt = f"""You are a network security expert analyzing captured network traffic.

Below is a JSON summary of network communication flows extracted from a PCAP file:

```json
{flows_json}
```

Please provide your analysis in the following EXACT JSON format (no markdown, no code fences, just raw JSON):

{{
  "insights": [
    "Insight 1: ...",
    "Insight 2: ...",
    "Insight 3: ...",
    "Insight 4: ..."
  ],
  "mermaid_code": "graph LR\\n  A[192.168.1.100] -->|TCP:80| B[93.184.216.34]\\n  ..."
}}

Rules for your analysis:
1. Provide exactly 3-4 bullet-point insights about the traffic patterns, anomalies, potential security concerns, or notable behaviors.
2. Generate valid Mermaid.js graph code (using `graph LR` or `graph TD`) showing the communication topology. Label edges VERY STRICTLY using the syntax `A -->|protocol:port| B`. DO NOT use colons for labels like `A --> B: label`.
3. Make the Mermaid code clean and renderable. Use simple node IDs (A, B, C, etc.) with IP addresses as labels.
4. CRITICAL: Return ONLY the raw JSON object. No markdown formatting, no ```json``` blocks, nothing else.
"""
    
    print("[*] Sending data to Gemini 2.5 Flash for analysis...")
    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    
    # Clean up response — strip markdown code fences if present
    if raw_text.startswith("```"):
        # Remove first line (```json) and last line (```)
        lines = raw_text.split("\n")
        raw_text = "\n".join(lines[1:-1]).strip()
    
    print(f"[*] Received response ({len(raw_text)} chars)")
    
    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"[!] Warning: Failed to parse LLM response as JSON: {e}")
        print(f"[*] Raw response:\n{raw_text[:500]}")
        # Fallback: try to extract JSON from the response
        import re
        json_match = re.search(r'\{[\s\S]*\}', raw_text)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {
                "insights": ["Analysis completed but response format was unexpected. Raw response saved."],
                "mermaid_code": "graph LR\n  A[Error] --> B[Could not parse]",
                "raw_response": raw_text
            }
    
    # Validate structure
    if "insights" not in result:
        result["insights"] = ["No insights could be extracted from the LLM response."]
    if "mermaid_code" not in result:
        result["mermaid_code"] = "graph LR\n  A[No diagram generated]"
    
    return result


def main():
    print("=" * 60)
    print("  AI Analyst (LLM Integration) — Directive 02")
    print("=" * 60)
    
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(
            f"[!] flows_summary.json not found at: {INPUT_FILE}\n"
            f"    Run pcap_parser.py first (Directive 01)."
        )
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        flows_data = json.load(f)
    
    print(f"[*] Loaded {flows_data['total_flows']} flows from {flows_data['source_file']}")
    
    result = analyze_with_llm(flows_data)
    
    os.makedirs(TMP_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n[+] SUCCESS: Analysis complete")
    print(f"[+] Output saved to: {OUTPUT_FILE}")
    print(f"\n--- Insights ---")
    for insight in result.get("insights", []):
        print(f"  • {insight}")
    print(f"\n--- Mermaid Code Preview ---")
    mermaid = result.get("mermaid_code", "")
    print(f"  {mermaid[:200]}{'...' if len(mermaid) > 200 else ''}")


if __name__ == "__main__":
    main()
