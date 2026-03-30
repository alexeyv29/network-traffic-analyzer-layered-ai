# Directive 03: Build the Web UI and API Backend

**Goal:** Create a lightweight web interface where a user can upload a PCAP file, trigger the analysis pipeline, and view the results dynamically.

**Execution Steps:**
1. Write a lightweight Python web server (using Flask or FastAPI) named `app.py` in the `/execution/` directory.
2. Create an `index.html` file (you can place this in a `templates` or `static` folder as required by your chosen framework).
3. The HTML page must include: 
   - A modern file upload form for `.pcap` or `.pcapng` files.
   - A loading indicator.
   - A text area to display the LLM insights.
   - A dedicated `div` to render the Mermaid.js diagram (you must include the official Mermaid.js CDN script in the HTML header).
4. The backend `app.py` must have an endpoint that handles the file upload:
   - Saves the uploaded file as `/.tmp/sample.pcap` (overwriting any old ones).
   - Triggers the execution of `pcap_parser.py`.
   - Triggers the execution of `llm_analyzer.py`.
   - Reads `/.tmp/analysis_result.json` and returns it as a JSON response to the frontend.
5. Start the web server. **Self-Anneal Rule:** Test the entire flow. If there are CORS errors, missing template errors, or if the Mermaid graph fails to render on the frontend, read the logs, fix the code, and restart the server until the page works perfectly.