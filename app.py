from flask import Flask, jsonify, request, redirect, render_template_string

app = Flask(__name__)

url_map = {
    "ci":   "https://github.com/NabilFahmi16/c270_T3/actions",
    "repo": "https://github.com/NabilFahmi16/c270_T3"
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>C270 DevOps URL Shortener</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background:#f0f2f5; margin:0; padding:20px; }
        .container { max-width:900px; margin:auto; background:white; padding:30px; border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.08); }
        h1 { color:#1a3c5e; text-align:center; margin-bottom:28px; }
        .form-group { margin-bottom:20px; }
        label { display:block; margin-bottom:6px; font-weight:600; color:#2c3e50; }
        input[type="text"] { width:100%; padding:12px; border:1px solid #d1d9e0; border-radius:6px; font-size:16px; box-sizing:border-box; }
        button { background:#0066cc; color:white; border:none; padding:14px; border-radius:6px; cursor:pointer; font-size:16px; width:100%; font-weight:600; }
        button:hover { background:#0052a3; }
        #result { margin-top:24px; padding:16px; border-radius:6px; background:#e8f4ff; border-left:4px solid #0066cc; min-height:60px; }
        .links-section { margin-top:40px; }
        .link-item { display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid #eee; }
        .link-left { flex:1; }
        .short-code { font-family:monospace; color:#0066cc; font-weight:bold; }
        .full-url { color:#555; font-size:0.95em; word-break:break-all; }
        .copy-btn, .del-btn { padding:6px 12px; font-size:0.9em; border-radius:4px; cursor:pointer; margin-left:10px; }
        .copy-btn { background:#28a745; color:white; border:none; }
        .del-btn { background:#dc3545; color:white; border:none; }
        footer { text-align:center; margin-top:50px; color:#7f8c8d; font-size:0.95em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 C270 DevOps URL Shortener</h1>

        <div class="form-group">
            <label for="alias">Short Alias (e.g., project, demo, slides)</label>
            <input type="text" id="alias" placeholder="Enter short name" />
        </div>
        <div class="form-group">
            <label for="url">Target URL (must start with http/https)</label>
            <input type="text" id="url" placeholder="https://example.com/my-page" />
        </div>
        <button onclick="shorten()">Create / Update Short Link</button>

        <div id="result"></div>

        <div class="links-section">
            <h2>📌 All Short Links</h2>
            {% if url_map %}
                {% for alias, target in url_map.items() %}
                <div class="link-item">
                    <div class="link-left">
                        <div><span class="short-code">/{{ alias }}</span> → {{ target }}</div>
                    </div>
                    <div>
                        <button class="copy-btn" onclick="copyToClipboard('{{ request.host_url }}go/{{ alias }}')">Copy</button>
                        <button class="del-btn" onclick="deleteLink('{{ alias }}')">Delete</button>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p style="color:#777; text-align:center;">No custom links yet — create one above!</p>
            {% endif %}
        </div>

        <footer>
            Republic Polytechnic • C270 DevOps Fundamentals AY2025 • Nabil
        </footer>
    </div>

    <script>
        const BASE = "{{ request.host_url.rstrip('/') }}";

        async function shorten() {
            const alias = document.getElementById('alias').value.trim();
            const url = document.getElementById('url').value.trim();
            const result = document.getElementById('result');

            if (!alias) { result.innerHTML = '<span style="color:#c0392b;">Alias is required.</span>'; return; }
            if (!url)  { result.innerHTML = '<span style="color:#c0392b;">URL is required.</span>'; return; }
            if (!url.match(/^https?:\/\//i)) {
                result.innerHTML = '<span style="color:#c0392b;">URL must start with http:// or https://</span>'; return;
            }

            try {
                const res = await fetch('/shorten', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({alias, url})
                });
                const data = await res.json();

                if (res.ok) {
                    let msg = data.warning ? '✅ Link updated!' : '🎉 Short link created!';
                    result.innerHTML = `
                        ${msg}<br>
                        <strong>Short URL:</strong>
                        <a href="/go/${alias}" target="_blank">${BASE}/go/${alias}</a>
                        <button onclick="copyToClipboard('${BASE}/go/${alias}')" style="margin-left:10px;">Copy</button>
                    `;
                    setTimeout(() => location.reload(), 1400);
                } else {
                    result.innerHTML = `<span style="color:#c0392b;">❌ ${data.error || 'Something went wrong'}</span>`;
                }
            } catch(e) {
                result.innerHTML = '<span style="color:#c0392b;">Network error — try again</span>';
            }
        }

        async function deleteLink(alias) {
            if (!confirm(`Delete /${alias} ?`)) return;
            try {
                const res = await fetch(`/shorten/${alias}`, {method: 'DELETE'});
                if (res.ok) {
                    document.getElementById('result').innerHTML = `<span style="color:#27ae60;">Deleted /${alias} successfully</span>`;
                    setTimeout(() => location.reload(), 1200);
                } else {
                    const data = await res.json();
                    document.getElementById('result').innerHTML = `<span style="color:#c0392b;">${data.error || 'Failed to delete'}</span>`;
                }
            } catch(e) {
                document.getElementById('result').innerHTML = '<span style="color:#c0392b;">Network error</span>';
            }
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert('Copied to clipboard: ' + text);
            }).catch(() => {
                alert('Copy failed — please copy manually');
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, url_map=url_map)

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
        return jsonify({"error": "Missing alias or url"}), 400

    alias = data['alias'].strip()
    url   = data['url'].strip()

    if not alias:
        return jsonify({"error": "Alias cannot be empty"}), 400

    # Protect system routes
    reserved = {"health", "links", "go", "shorten", ""}
    if alias in reserved:
        return jsonify({"error": f"Alias '{alias}' is reserved"}), 400

    if not url.startswith(('http://', 'https://')):
        return jsonify({"error": "URL must start with http:// or https://"}), 400

    was_existing = alias in url_map
    url_map[alias] = url

    if was_existing:
        return jsonify({"warning": "Alias already existed → updated"}), 200
    else:
        return jsonify({"message": "Created"}), 201

@app.route('/shorten/<alias>', methods=['DELETE'])
def delete_link(alias):
    if alias in url_map:
        del url_map[alias]
        return jsonify({"message": f"Deleted /{alias}"}), 200
    return jsonify({"error": "Alias not found"}), 404

@app.route('/go/<alias>')
def redirect_to_url(alias):
    if alias in url_map:
        return redirect(url_map[alias], code=302)
    return jsonify({"error": "Not found"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
