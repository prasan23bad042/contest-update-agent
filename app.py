from flask import Flask, render_template, request, jsonify
from agents.codeforces_agent import generate_codeforces_report
from agents.codechef_agent import generate_codechef_report
from agents.leetcode_module import generate_leetcode_report
import threading

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
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
    app.run(debug=True, port=5000)
