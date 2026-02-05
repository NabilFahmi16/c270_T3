from flask import Flask, jsonify, request, redirect, render_template_string
from datetime import datetime
import string
import random

app = Flask(__name__)

# Enhanced in-memory storage with metadata
url_map = {
    "ci": {
        "url": "https://github.com/NabilFahmi16/c270_T3/actions",
        "created": "2024-01-01 00:00:00",
        "clicks": 0
    },
    "repo": {
        "url": "https://github.com/NabilFahmi16/c270_T3",
        "created": "2024-01-01 00:00:00",
        "clicks": 0
    }
}

# HTML Template with embedded CSS
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Shortener - DevOps Project</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
            animation: fadeInDown 0.6s ease-out;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            animation: fadeInUp 0.6s ease-out;
        }
        
        .card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: all 0.3s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .links-grid {
            display: grid;
            gap: 15px;
        }
        
        .link-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            transition: all 0.3s;
        }
        
        .link-item:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .link-alias {
            font-size: 1.3em;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 8px;
        }
        
        .link-url {
            color: #666;
            word-break: break-all;
            margin-bottom: 8px;
        }
        
        .link-meta {
            display: flex;
            gap: 20px;
            font-size: 0.9em;
            color: #999;
            margin-top: 10px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .copy-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            margin-top: 10px;
            transition: all 0.3s;
        }
        
        .copy-btn:hover {
            background: #218838;
        }
        
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }
            
            .card {
                padding: 20px;
            }
            
            .link-meta {
                flex-direction: column;
                gap: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔗 URL Shortener</h1>
            <p>DevOps CI/CD Project - Fast & Simple Link Management</p>
        </div>
        
        <div class="card">
            <h2>📊 Statistics</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{{ total_links }}</div>
                    <div class="stat-label">Total Links</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ total_clicks }}</div>
                    <div class="stat-label">Total Clicks</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>✨ Create Short Link</h2>
            <div id="alert" class="alert"></div>
            <form id="shortenForm">
                <div class="form-group">
                    <label for="alias">Short Alias</label>
                    <input type="text" id="alias" name="alias" placeholder="e.g., github, docs, api" required>
                </div>
                <div class="form-group">
                    <label for="url">Destination URL</label>
                    <input type="url" id="url" name="url" placeholder="https://example.com" required>
                </div>
                <button type="submit" class="btn">🚀 Create Short Link</button>
            </form>
        </div>
        
        <div class="card">
            <h2>📋 Your Links</h2>
            <div id="linksList" class="links-grid">
                {% if links %}
                    {% for alias, data in links.items() %}
                    <div class="link-item">
                        <div class="link-alias">{{ request.host_url }}go/{{ alias }}</div>
                        <div class="link-url">→ {{ data.url }}</div>
                        <div class="link-meta">
                            <span>👁️ {{ data.clicks }} clicks</span>
                            <span>📅 Created: {{ data.created }}</span>
                        </div>
                        <button class="copy-btn" onclick="copyLink('{{ request.host_url }}go/{{ alias }}')">
                            📋 Copy Link
                        </button>
                    </div>
                    {% endfor %}
                {% else %}
                    <p style="text-align: center; color: #999;">No links yet. Create your first one above!</p>
                {% endif %}
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('shortenForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const alias = document.getElementById('alias').value;
            const url = document.getElementById('url').value;
            const alert = document.getElementById('alert');
            
            try {
                const response = await fetch('/shorten', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ alias, url })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    alert.className = 'alert alert-success';
                    alert.textContent = '✅ Link created successfully! Refreshing...';
                    alert.style.display = 'block';
                    
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    alert.className = 'alert alert-error';
                    alert.textContent = '❌ ' + data.error;
                    alert.style.display = 'block';
                }
            } catch (error) {
                alert.className = 'alert alert-error';
                alert.textContent = '❌ Error creating link. Please try again.';
                alert.style.display = 'block';
            }
        });
        
        function copyLink(link) {
            navigator.clipboard.writeText(link).then(() => {
                alert('✅ Link copied to clipboard!');
            }).catch(() => {
                alert('❌ Failed to copy link');
            });
        }
    </script>
</body>
</html>
"""

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/')
def home():
    total_links = len(url_map)
    total_clicks = sum(data['clicks'] for data in url_map.values())
    
    return render_template_string(
        HOME_TEMPLATE,
        links=url_map,
        total_links=total_links,
        total_clicks=total_clicks
    )

@app.route('/links')
def list_links():
    return jsonify(url_map), 200

@app.route('/shorten', methods=['POST'])
def shorten():
    data = request.get_json()
    
    if not data or 'alias' not in data or 'url' not in data:
        return jsonify({"error": "Missing alias or url"}), 400
    
    alias = data['alias']
    url = data['url']
    
    # Validate alias (alphanumeric and hyphens only)
    if not all(c.isalnum() or c in '-_' for c in alias):
        return jsonify({"error": "Alias can only contain letters, numbers, hyphens, and underscores"}), 400
    
    # Check if alias already exists
    if alias in url_map:
        return jsonify({"error": "Alias already exists. Please choose a different one."}), 409
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        return jsonify({"error": "URL must start with http:// or https://"}), 400
    
    url_map[alias] = {
        "url": url,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "clicks": 0
    }
    
    return jsonify({
        "message": "Link created successfully",
        "alias": alias,
        "short_url": f"/go/123"
    }), 201

@app.route('/go/<alias>')
def go(alias):
    if alias in url_map:
        # Increment click counter
        url_map[alias]['clicks'] += 1
        return redirect(url_map[alias]['url'])
    return jsonify({"error": "Link not found"}), 404

@app.route('/delete/<alias>', methods=['DELETE'])
def delete_link(alias):
    if alias in url_map:
        del url_map[alias]
        return jsonify({"message": "Link deleted successfully"}), 200
    return jsonify({"error": "Link not found"}), 404

@app.route('/stats')
def stats():
    total_links = len(url_map)
    total_clicks = sum(data['clicks'] for data in url_map.values())
    
    return jsonify({
        "total_links": total_links,
        "total_clicks": total_clicks,
        "links": url_map
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
