from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from agents.codeforces_agent import generate_codeforces_report
from agents.codechef_agent import generate_codechef_report
from agents.leetcode_module import generate_leetcode_report
import threading
import os

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "message": "API is running"})

@app.route("/generate", methods=["POST"])
@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    cf_id = data.get("cf_id")
    cc_id = data.get("cc_id")
    lc_id = data.get("lc_id")
    
    reports = {}
    
    # Use threads to fetch data concurrently to speed up report generation
    def fetch_cf():
        if cf_id:
            reports["codeforces"] = generate_codeforces_report(cf_id)
            
    def fetch_cc():
        if cc_id:
            reports["codechef"] = generate_codechef_report(cc_id)
            
    def fetch_lc():
        if lc_id:
            reports["leetcode"] = generate_leetcode_report(lc_id)
            
    threads = []
    if cf_id: threads.append(threading.Thread(target=fetch_cf))
    if cc_id: threads.append(threading.Thread(target=fetch_cc))
    if lc_id: threads.append(threading.Thread(target=fetch_lc))
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    return jsonify(reports)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
