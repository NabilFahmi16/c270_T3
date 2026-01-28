import json
import os
import string
import random
from datetime import datetime
from flask import Flask, jsonify, request, redirect, render_template_string

app = Flask(__name__)

# --- CONFIGURATION ---
DATA_FILE = "urls.json"

# --- PERSISTENCE LOGIC ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(url_map, f, indent=4)

url_map = load_data()

# --- HELPER FUNCTIONS ---
def generate_random_alias(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        new_alias = ''.join(random.choice(chars) for _ in range(length))
        if new_alias not in url_map:
            return new_alias

# HTML Template (Updated with QR code support and better UX)
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Shortener Pro</title>
    <style>
        /* ... (Keep your original CSS here) ... */
        body { font-family: 'Segoe UI', sans-serif; background: #f4f7f6; padding: 20px; color: #333; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .btn { background: #4a90e2; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
        .link-item { border-bottom: 1px solid #eee; padding: 15px 0; display: flex; justify-content: space-between; align-items: center; }
        .qr-img { width: 80px; height: 80px; margin-left: 15px; border: 1px solid #ddd; }
        .alias-text { font-weight: bold; color: #4a90e2; }
        input { padding: 10px; border: 1px solid #ddd; border-radius: 4px; width: 200px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 URL Shortener Pro</h1>
        
        <div class="card">
            <h2>✨ Create Link</h2>
            <form id="shortenForm">
                <input type="text" id="url" placeholder="Paste long URL here..." required style="width: 60%;">
                <input type="text" id="alias" placeholder="Custom alias (optional)">
                <button type="submit" class="btn">Shorten</button>
            </form>
        </div>

        <div class="card">
            <h2>📋 Active Links</h2>
            {% for alias, data in links.items() %}
            <div class="link-item">
                <div>
                    <div class="alias-text">{{ request.host_url }}go/{{ alias }}</div>
                    <div style="font-size: 0.8em; color: #666;">Original: {{ data.url }}</div>
                    <div style="font-size: 0.8em; color: #999;">Clicks: {{ data.clicks }} | Created: {{ data.created }}</div>
                </div>
                <div style="display: flex; align-items: center;">
                    <img class="qr-img" src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{ request.host_url }}go/{{ alias }}" alt="QR">
                    <button class="btn" style="background:#e74c3c; margin-left:10px;" onclick="deleteLink('{{ alias }}')">Delete</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        document.getElementById('shortenForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const alias = document.getElementById('alias').value;
            const url = document.getElementById('url').value;
            
            const response = await fetch('/shorten', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ alias, url })
            });
            
            if (response.ok) window.location.reload();
            else alert("Error creating link");
        });

        async function deleteLink(alias) {
            if(confirm("Delete this link?")) {
                await fetch(`/delete/${alias}`, { method: 'DELETE' });
                window.location.reload();
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE, links=url_map)

@app.route('/shorten', methods=['POST'])
def shorten():
    data = request.get_json()
    url = data.get('url')
    alias = data.get('alias') or generate_random_alias()
    
    if not url.startswith(('http://', 'https://')):
        return jsonify({"error": "Invalid URL"}), 400
    
    if alias in url_map:
        return jsonify({"error": "Alias already exists"}), 409
    
    url_map[alias] = {
        "url": url,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "clicks": 0
    }
    save_data() # Save to file
    return jsonify({"alias": alias}), 201

@app.route('/go/<alias>')
def go(alias):
    if alias in url_map:
        url_map[alias]['clicks'] += 1
        save_data() # Update clicks in file
        return redirect(url_map[alias]['url'])
    return "Link not found", 404

@app.route('/delete/<alias>', methods=['DELETE'])
def delete_link(alias):
    if alias in url_map:
        del url_map[alias]
        save_data()
        return jsonify({"success": True}), 200
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)