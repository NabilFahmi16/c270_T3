import json
import os
import string
import random
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request, redirect, render_template_string, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-123')

# --- CONFIGURATION ---
DATA_FILE = "urls.json"
USER_FILE = "users.json"

# --- PERSISTENCE LOGIC ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"links": {}, "analytics": {}}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(url_data, f, indent=4)

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

url_data = load_data()
users = load_users()

# --- HELPER FUNCTIONS ---
def generate_random_alias(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        new_alias = ''.join(random.choice(chars) for _ in range(length))
        if new_alias not in url_data["links"]:
            return new_alias

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# --- HTML TEMPLATES ---
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - URL Shortener</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; display: flex; justify-content: center; align-items: center; }
        .login-box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); width: 300px; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 100%; padding: 10px; background: #4a90e2; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .tabs { display: flex; margin-bottom: 20px; }
        .tab { flex: 1; text-align: center; padding: 10px; cursor: pointer; border-bottom: 2px solid transparent; }
        .tab.active { border-bottom-color: #4a90e2; font-weight: bold; }
    </style>
</head>
<body>
    <div class="login-box">
        <div class="tabs">
            <div class="tab active" onclick="showLogin()">Login</div>
            <div class="tab" onclick="showRegister()">Register</div>
        </div>
        
        <div id="loginForm">
            <h2>Login</h2>
            <form action="/login" method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        </div>
        
        <div id="registerForm" style="display:none;">
            <h2>Register</h2>
            <form action="/register" method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Register</button>
            </form>
        </div>
    </div>
    
    <script>
        function showLogin() {
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('registerForm').style.display = 'none';
            document.querySelectorAll('.tab')[0].classList.add('active');
            document.querySelectorAll('.tab')[1].classList.remove('active');
        }
        function showRegister() {
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('registerForm').style.display = 'block';
            document.querySelectorAll('.tab')[0].classList.remove('active');
            document.querySelectorAll('.tab')[1].classList.add('active');
        }
    </script>
</body>
</html>
"""

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Shortener Pro v2.0</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #4a90e2;
            margin: 10px 0;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 30px;
        }
        
        .create-card, .links-card {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #444;
        }
        
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #4a90e2;
        }
        
        .btn {
            background: #4a90e2;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #357abd;
        }
        
        .btn-danger {
            background: #e74c3c;
        }
        
        .btn-danger:hover {
            background: #c0392b;
        }
        
        .btn-success {
            background: #2ecc71;
        }
        
        .btn-success:hover {
            background: #27ae60;
        }
        
        .link-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #4a90e2;
        }
        
        .link-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .short-url {
            font-weight: bold;
            color: #4a90e2;
            font-size: 1.1em;
        }
        
        .original-url {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            word-break: break-all;
        }
        
        .link-meta {
            display: flex;
            gap: 20px;
            font-size: 0.85em;
            color: #888;
            margin-top: 10px;
        }
        
        .link-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .qr-container {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
        
        .qr-code {
            width: 100px;
            height: 100px;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 5px;
            background: white;
        }
        
        .analytics-chart {
            height: 200px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-top: 15px;
            padding: 15px;
        }
        
        .expiry-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        
        .expiry-soon {
            background: #ffeaa7;
            color: #e17055;
        }
        
        .expiry-expired {
            background: #fab1a0;
            color: #d63031;
        }
        
        .feature-badge {
            display: inline-block;
            padding: 4px 8px;
            background: #dfe6e9;
            border-radius: 12px;
            font-size: 0.8em;
            margin-left: 5px;
        }
        
        .dropdown {
            position: relative;
            display: inline-block;
        }
        
        .dropdown-content {
            display: none;
            position: absolute;
            background: white;
            min-width: 160px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            border-radius: 8px;
            z-index: 1;
        }
        
        .dropdown:hover .dropdown-content {
            display: block;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔗 URL Shortener Pro v2.0</h1>
            <div class="user-info">
                <span>Welcome, <strong>{{ username }}</strong>!</span>
                <a href="/logout" class="btn btn-danger">Logout</a>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Links</div>
                <div class="stat-number">{{ stats.total_links }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Clicks</div>
                <div class="stat-number">{{ stats.total_clicks }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Active Links</div>
                <div class="stat-number">{{ stats.active_links }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Expiring Soon</div>
                <div class="stat-number">{{ stats.expiring_soon }}</div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="create-card">
                <h2 style="margin-bottom: 25px;">✨ Create New Short Link</h2>
                <form id="shortenForm">
                    <div class="form-group">
                        <label for="url">Destination URL *</label>
                        <input type="url" id="url" placeholder="https://example.com" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="alias">Custom Alias (Optional)</label>
                        <input type="text" id="alias" placeholder="my-custom-alias">
                        <small style="color: #666; display: block; margin-top: 5px;">Leave empty for auto-generated alias</small>
                    </div>
                    
                    <div class="form-group">
                        <label for="expiry">Link Expiry</label>
                        <select id="expiry">
                            <option value="never">Never</option>
                            <option value="1day">1 Day</option>
                            <option value="7days">7 Days</option>
                            <option value="30days">30 Days</option>
                            <option value="custom">Custom Date</option>
                        </select>
                    </div>
                    
                    <div class="form-group" id="customDateGroup" style="display:none;">
                        <label for="customDate">Custom Expiry Date</label>
                        <input type="date" id="customDate">
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Password Protect (Optional)</label>
                        <input type="text" id="password" placeholder="Set access password">
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="utm_tracking"> Enable UTM Tracking
                        </label>
                    </div>
                    
                    <button type="submit" class="btn" style="width: 100%; padding: 15px; font-size: 16px;">
                        🚀 Create Short Link
                    </button>
                </form>
                
                <div id="result" style="margin-top: 20px; display: none;">
                    <div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 8px;">
                        <strong>✅ Link Created Successfully!</strong>
                        <div style="margin-top: 10px;">
                            Short URL: <span id="shortUrl" style="font-weight: bold;"></span>
                            <button onclick="copyToClipboard()" class="btn btn-success" style="margin-left: 10px; padding: 5px 15px;">
                                📋 Copy
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="links-card">
                <h2 style="margin-bottom: 25px;">📋 Your Links ({{ links|length }})</h2>
                
                <div style="margin-bottom: 20px;">
                    <input type="text" id="searchLinks" placeholder="🔍 Search links..." style="width: 100%;">
                </div>
                
                {% for alias, data in links.items() %}
                <div class="link-item" data-alias="{{ alias }}">
                    <div class="link-header">
                        <div>
                            <span class="short-url">{{ request.host_url }}go/{{ alias }}</span>
                            {% if data.expires_at %}
                                {% if data.expires_at == 'expired' %}
                                <span class="expiry-badge expiry-expired">Expired</span>
                                {% elif data.expires_at == 'soon' %}
                                <span class="expiry-badge expiry-soon">Expires Soon</span>
                                {% endif %}
                            {% endif %}
                            {% if data.password %}
                            <span class="feature-badge">🔒</span>
                            {% endif %}
                        </div>
                        <div class="dropdown">
                            <button class="btn" style="padding: 8px 16px;">⋯</button>
                            <div class="dropdown-content">
                                <button onclick="copyLink('{{ alias }}')" style="width: 100%; text-align: left; padding: 10px; border: none; background: none; cursor: pointer;">📋 Copy</button>
                                <button onclick="showAnalytics('{{ alias }}')" style="width: 100%; text-align: left; padding: 10px; border: none; background: none; cursor: pointer;">📊 Analytics</button>
                                <button onclick="deleteLink('{{ alias }}')" style="width: 100%; text-align: left; padding: 10px; border: none; background: none; cursor: pointer; color: #e74c3c;">🗑️ Delete</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="original-url">{{ data.url }}</div>
                    
                    <div class="link-meta">
                        <span>👆 {{ data.clicks }} clicks</span>
                        <span>📅 Created: {{ data.created }}</span>
                        {% if data.expiry_date %}
                        <span>⏰ Expires: {{ data.expiry_date }}</span>
                        {% endif %}
                    </div>
                    
                    <div class="link-actions">
                        <button onclick="toggleQR('{{ alias }}')" class="btn">📱 Show QR</button>
                        <a href="/analytics/{{ alias }}" target="_blank" class="btn">📈 View Analytics</a>
                    </div>
                    
                    <div class="qr-container" id="qr-{{ alias }}" style="display:none;">
                        <img class="qr-code" src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{ request.host_url }}go/{{ alias }}" alt="QR Code">
                        <div>
                            <div style="font-weight: bold; margin-bottom: 5px;">QR Code</div>
                            <div style="font-size: 0.9em; color: #666;">Scan to visit: {{ request.host_url }}go/{{ alias }}</div>
                            <button onclick="downloadQR('{{ alias }}')" class="btn" style="margin-top: 10px; padding: 8px 16px;">⬇ Download QR</button>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        // Custom date toggle
        document.getElementById('expiry').addEventListener('change', function() {
            document.getElementById('customDateGroup').style.display = 
                this.value === 'custom' ? 'block' : 'none';
        });
        
        // Form submission
        document.getElementById('shortenForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const url = document.getElementById('url').value;
            const alias = document.getElementById('alias').value;
            const expiry = document.getElementById('expiry').value;
            const customDate = document.getElementById('customDate').value;
            const password = document.getElementById('password').value;
            const utmTracking = document.getElementById('utm_tracking').checked;
            
            const payload = {
                url,
                alias: alias || undefined,
                expiry: expiry === 'custom' ? customDate : expiry,
                password: password || undefined,
                utm_tracking: utmTracking
            };
            
            try {
                const response = await fetch('/api/shorten', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    document.getElementById('shortUrl').textContent = 
                        window.location.origin + '/go/' + result.alias;
                    document.getElementById('result').style.display = 'block';
                    setTimeout(() => window.location.reload(), 2000);
                } else {
                    const error = await response.json();
                    alert('Error: ' + error.error);
                }
            } catch (err) {
                alert('Network error: ' + err.message);
            }
        });
        
        // Search functionality
        document.getElementById('searchLinks').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            document.querySelectorAll('.link-item').forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(searchTerm) ? 'block' : 'none';
            });
        });
        
        // Helper functions
        function copyToClipboard() {
            const text = document.getElementById('shortUrl').textContent;
            navigator.clipboard.writeText(text);
            alert('Copied to clipboard!');
        }
        
        function copyLink(alias) {
            navigator.clipboard.writeText(window.location.origin + '/go/' + alias);
            alert('Link copied!');
        }
        
        function toggleQR(alias) {
            const qrDiv = document.getElementById('qr-' + alias);
            qrDiv.style.display = qrDiv.style.display === 'none' ? 'flex' : 'none';
        }
        
        function downloadQR(alias) {
            const link = document.createElement('a');
            link.href = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${window.location.origin}/go/${alias}`;
            link.download = `qr-${alias}.png`;
            link.click();
        }
        
        function deleteLink(alias) {
            if(confirm('Are you sure you want to delete this link?')) {
                fetch(`/api/delete/${alias}`, { method: 'DELETE' })
                    .then(() => window.location.reload());
            }
        }
        
        function showAnalytics(alias) {
            window.open(`/analytics/${alias}`, '_blank');
        }
    </script>
</body>
</html>
"""

# --- ROUTES ---
@app.route('/')
@login_required
def home():
    # Filter links by user
    user_links = {}
    for alias, data in url_data["links"].items():
        if data.get("user_id") == session['user_id']:
            user_links[alias] = data
    
    # Calculate statistics
    stats = {
        "total_links": len(user_links),
        "total_clicks": sum(link.get("clicks", 0) for link in user_links.values()),
        "active_links": sum(1 for link in user_links.values() if not is_expired(link)),
        "expiring_soon": sum(1 for link in user_links.values() if is_expiring_soon(link))
    }
    
    return render_template_string(HOME_TEMPLATE, 
                                  links=user_links,
                                  stats=stats,
                                  username=session.get('username', 'Guest'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        
        if username in users and users[username]['password'] == password:
            session['user_id'] = users[username]['id']
            session['username'] = username
            return redirect('/')
        return "Invalid credentials", 401
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = hash_password(request.form['password'])
    
    if username in users:
        return "Username already exists", 400
    
    user_id = generate_random_alias(8)
    users[username] = {
        'id': user_id,
        'email': email,
        'password': password,
        'created_at': datetime.now().isoformat()
    }
    save_users()
    
    session['user_id'] = user_id
    session['username'] = username
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/api/shorten', methods=['POST'])
@login_required
def api_shorten():
    data = request.get_json()
    url = data.get('url')
    alias = data.get('alias') or generate_random_alias()
    expiry = data.get('expiry')
    password = data.get('password')
    
    if not url.startswith(('http://', 'https://')):
        return jsonify({"error": "Invalid URL"}), 400
    
    if alias in url_data["links"]:
        return jsonify({"error": "Alias already exists"}), 409
    
    # Calculate expiry date
    expiry_date = None
    if expiry and expiry != 'never':
        if expiry == '1day':
            expiry_date = (datetime.now() + timedelta(days=1)).isoformat()
        elif expiry == '7days':
            expiry_date = (datetime.now() + timedelta(days=7)).isoformat()
        elif expiry == '30days':
            expiry_date = (datetime.now() + timedelta(days=30)).isoformat()
        elif expiry and expiry != 'custom':
            try:
                expiry_date = datetime.fromisoformat(expiry).isoformat()
            except:
                pass
    
    link_data = {
        "url": url,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "clicks": 0,
        "user_id": session['user_id'],
        "expiry_date": expiry_date,
        "password": password,
        "utm_tracking": data.get('utm_tracking', False)
    }
    
    url_data["links"][alias] = link_data
    url_data["analytics"][alias] = {
        "clicks": [],
        "referrers": {},
        "countries": {},
        "browsers": {}
    }
    save_data()
    
    return jsonify({
        "alias": alias,
        "short_url": f"{request.host_url}go/{alias}",
        "expires_at": expiry_date
    }), 201

@app.route('/go/<alias>')
def go(alias):
    if alias not in url_data["links"]:
        return "Link not found", 404
    
    link = url_data["links"][alias]
    
    # Check if link is expired
    if is_expired(link):
        return "This link has expired", 410
    
    # Check password protection
    if link.get("password"):
        if 'password' not in request.args or request.args['password'] != link['password']:
            return '''
            <form method="GET">
                <input type="password" name="password" placeholder="Enter password" required>
                <button type="submit">Access Link</button>
            </form>
            ''', 403
    
    # Track analytics
    url_data["links"][alias]['clicks'] += 1
    
    # Record analytics data
    if alias in url_data["analytics"]:
        analytics = url_data["analytics"][alias]
        analytics["clicks"].append({
            "timestamp": datetime.now().isoformat(),
            "ip": request.remote_addr,
            "user_agent": request.user_agent.string,
            "referrer": request.referrer
        })
        
        # Update referrers
        ref = request.referrer or "direct"
        analytics["referrers"][ref] = analytics["referrers"].get(ref, 0) + 1
    
    save_data()
    
    # Add UTM parameters if enabled
    url = link['url']
    if link.get('utm_tracking'):
        utm_params = {
            'utm_source': 'url_shortener',
            'utm_medium': 'redirect',
            'utm_campaign': alias,
            'utm_term': request.remote_addr
        }
        url = add_url_params(url, utm_params)
    
    return redirect(url)

@app.route('/api/delete/<alias>', methods=['DELETE'])
@login_required
def api_delete(alias):
    if alias in url_data["links"] and url_data["links"][alias].get("user_id") == session['user_id']:
        del url_data["links"][alias]
        if alias in url_data["analytics"]:
            del url_data["analytics"][alias]
        save_data()
        return jsonify({"success": True}), 200
    return jsonify({"error": "Not found or unauthorized"}), 404

@app.route('/analytics/<alias>')
@login_required
def analytics(alias):
    if alias not in url_data["links"] or url_data["links"][alias].get("user_id") != session['user_id']:
        return "Unauthorized", 403
    
    link = url_data["links"][alias]
    analytics_data = url_data["analytics"].get(alias, {})
    
    return f'''
    <h2>Analytics for {alias}</h2>
    <p>Total Clicks: {link['clicks']}</p>
    <p>Created: {link['created']}</p>
    <canvas id="clicksChart"></canvas>
    <script>
        const ctx = document.getElementById('clicksChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(list(range(1, len(analytics_data.get("clicks", [])) + 1)))},
                datasets: [{{
                    label: 'Clicks',
                    data: {json.dumps([i+1 for i in range(len(analytics_data.get("clicks", [])))])},
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }}]
            }}
        }});
    </script>
    '''

# --- HELPER FUNCTIONS ---
def is_expired(link):
    expiry = link.get('expiry_date')
    if not expiry:
        return False
    try:
        expiry_date = datetime.fromisoformat(expiry)
        return datetime.now() > expiry_date
    except:
        return False

def is_expiring_soon(link):
    expiry = link.get('expiry_date')
    if not expiry:
        return False
    try:
        expiry_date = datetime.fromisoformat(expiry)
        return datetime.now() < expiry_date < (datetime.now() + timedelta(days=7))
    except:
        return False

def add_url_params(url, params):
    from urllib.parse import urlparse, urlencode, parse_qs
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query.update(params)
    return parsed._replace(query=urlencode(query, doseq=True)).geturl()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
