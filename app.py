# app.py
from flask import Flask, jsonify, request, redirect, render_template_string

app = Flask(__name__)

# In-memory storage (preloaded with your links)
url_map = {
    "ci": "https://github.com/NabilFahmi16/c270_T3/actions",
    "repo": "https://github.com/NabilFahmi16/c270_T3"
}

# HTML Template (embedded for simplicity)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>C270 DevOps URL Shortener</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8f9fa; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #34495e; }
        input[type="text"] { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-size: 16px; }
        button { background: #3498db; color: white; border: none; padding: 12px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%; }
        button:hover { background: #2980b9; }
        .result { margin-top: 20px; padding: 15px; background: #e8f4fc; border-left: 4px solid #3498db; }
        .links { margin-top: 30px; }
        .link-item { padding: 8px 0; border-bottom: 1px solid #eee; }
        .link-url { color: #3498db; text-decoration: none; }
        .link-url:hover { text-decoration: underline; }
        footer { text-align: center; margin-top: 30px; color: #7f8c8d; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 C270 DevOps URL Shortener</h1>
        
        <div class="form-group">
            <label for="alias">Short Alias (e.g., "demo")</label>
            <input type="text" id="alias" placeholder="Enter alias" />
        </div>
        <div class="form-group">
            <label for="url">Full URL (must start with http:// or https://)</label>
            <input type="text" id="url" placeholder="https://example.com" />
        </div>
        <button onclick="shorten()">Create Short Link</button>

        <div id="result"></div>

        <div class="links">
            <h2>📌 Predefined Short Links</h2>
            {% for alias, full_url in url_map.items() %}
            <div class="link-item">
                <strong>/go/{{ alias }}</strong> → 
                <a class="link-url" href="/go/{{ alias }}" target="_blank">{{ full_url }}</a>
            </div>
            {% endfor %}
        </div>

        <footer>
            Built for Republic Polytechnic • C270 DevOps Fundamentals AY2025
        </footer>
    </div>

    <script>
        async function shorten() {
            const alias = document.getElementById('alias').value.trim();
            const url = document.getElementById('url').value.trim();
            const resultDiv = document.getElementById('result');

            if (!alias || !url) {
                resultDiv.innerHTML = '<div style="color:red;">⚠️ Please fill both fields.</div>';
                return;
            }

            const response = await fetch('/shorten', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ alias, url })
            });

            const data = await response.json();
            if (response.ok) {
                resultDiv.innerHTML = `
                    <div class="result">
                        ✅ Short link created!<br>
                        <strong>Use:</strong> <a href="/go/${alias}" target="_blank">http://localhost:5000/go/${alias}</a>
                    </div>
                `;
                document.getElementById('alias').value = '';
                document.getElementById('url').value = '';
                setTimeout(() => location.reload(), 1000);
            } else {
                resultDiv.innerHTML = `<div style="color:red;">❌ ${data.error}</div>`;
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return jsonify({
        "message": "C270 DevOps URL Shortener - Nabil Fahmi",
        "status": "running"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/links')
def list_links():
    return jsonify(url_map), 200

@app.route('/shorten', methods=['POST'])
def shorten():
    data = request.get_json()
    if not data or 'alias' not in data or 'url' not in data:
        return jsonify({"error": "Missing 'alias' or 'url'"}), 400

    alias = data['alias'].strip()
    url   = data['url'].strip()

    if not alias:
        return jsonify({"error": "Alias cannot be empty"}), 400

    if alias in ["health", "links", "go", ""]:  # protect system routes
        return jsonify({"error": "This alias is reserved"}), 400

    if not url.startswith(('http://', 'https://')):
        return jsonify({"error": "URL must start with http:// or https://"}), 400

    if alias in url_map:
        return jsonify({"warning": "Alias already exists — it has been updated"}), 200

    url_map[alias] = url
    return jsonify({"short_url": f"/go/{alias}"}), 201

@app.route('/go/<alias>')
def redirect_to_url(alias):
    if alias in url_map:
        return redirect(url_map[alias], code=302)
    return jsonify({"error": "Alias not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)