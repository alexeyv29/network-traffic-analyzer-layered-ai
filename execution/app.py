"""
Directive 03: Web UI & API Backend
Flask server that serves the frontend and orchestrates the analysis pipeline.
"""
import os
import sys
import json
import subprocess
import traceback

# Ensure flask is available
try:
    from flask import Flask, render_template, request, jsonify
except ImportError:
    print("[!] Flask not installed. Installing...")
    os.system(f"{sys.executable} -m pip install flask")
    from flask import Flask, render_template, request, jsonify

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXECUTION_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(BASE_DIR, "tmp")
TEMPLATES_DIR = os.path.join(EXECUTION_DIR, "templates")
STATIC_DIR = os.path.join(EXECUTION_DIR, "static")

os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,
    static_folder=STATIC_DIR,
)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB max upload


@app.route("/")
def index():
    """Serve the main UI page."""
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Handle file upload and trigger the full analysis pipeline."""
    try:
        # 1. Validate upload
        if "pcap_file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files["pcap_file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.lower().endswith((".pcap", ".pcapng")):
            return jsonify({"error": "Only .pcap and .pcapng files are supported"}), 400
        
        # 2. Save uploaded file as sample.pcap
        pcap_path = os.path.join(TMP_DIR, "sample.pcap")
        file.save(pcap_path)
        file_size = os.path.getsize(pcap_path)
        print(f"[+] Saved uploaded file: {file.filename} ({file_size} bytes)")
        
        # 3. Run pcap_parser.py
        print("[*] Running PCAP parser...")
        parser_script = os.path.join(EXECUTION_DIR, "pcap_parser.py")
        result = subprocess.run(
            [sys.executable, parser_script],
            capture_output=True, text=True, timeout=120,
            cwd=BASE_DIR,
        )
        if result.returncode != 0:
            print(f"[!] Parser error:\n{result.stderr}")
            return jsonify({"error": f"PCAP parsing failed: {result.stderr[-500:]}"}), 500
        print(f"[+] Parser output:\n{result.stdout}")
        
        # 4. Run llm_analyzer.py
        print("[*] Running LLM analyzer...")
        analyzer_script = os.path.join(EXECUTION_DIR, "llm_analyzer.py")
        result = subprocess.run(
            [sys.executable, analyzer_script],
            capture_output=True, text=True, timeout=180,
            cwd=BASE_DIR,
        )
        if result.returncode != 0:
            print(f"[!] Analyzer error:\n{result.stderr}")
            return jsonify({"error": f"LLM analysis failed: {result.stderr[-500:]}"}), 500
        print(f"[+] Analyzer output:\n{result.stdout}")
        
        # 5. Read and return analysis_result.json
        analysis_path = os.path.join(TMP_DIR, "analysis_result.json")
        if not os.path.exists(analysis_path):
            return jsonify({"error": "Analysis output file not found"}), 500
        
        with open(analysis_path, "r", encoding="utf-8") as f:
            analysis = json.load(f)
        
        # Also include the flows summary for the frontend
        flows_path = os.path.join(TMP_DIR, "flows_summary.json")
        flows = {}
        if os.path.exists(flows_path):
            with open(flows_path, "r", encoding="utf-8") as f:
                flows = json.load(f)
        
        return jsonify({
            "success": True,
            "analysis": analysis,
            "flows": flows,
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Analysis timed out. The file may be too large."}), 504
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 60)
    print("  Network Traffic Analyzer — Web Server")
    print("=" * 60)
    print(f"  Templates: {TEMPLATES_DIR}")
    print(f"  Static:    {STATIC_DIR}")
    print(f"  Temp:      {TMP_DIR}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
