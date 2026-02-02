# ========== ADD THESE TEST ENDPOINTS TO YOUR APP.PY ==========

@app.route('/health')
def health():
    """Health check endpoint for tests"""
    return jsonify({"status": "ok", "message": "Service is healthy"})

@app.route('/links')
@login_required
def list_links():
    """List all links for the current user (for tests)"""
    user_links = {}
    for alias, data in url_data["links"].items():
        if data.get("user_id") == session['user_id']:
            user_links[alias] = {
                "url": data["url"],
                "created": data["created"],
                "clicks": data["clicks"],
                "expiry_date": data.get("expiry_date")
            }
    return jsonify(user_links)

@app.route('/shorten', methods=['POST'])
@login_required
def shorten():
    """Legacy shorten endpoint for backward compatibility with tests"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    url = data.get('url')
    alias = data.get('alias')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    if not url.startswith(('http://', 'https://')):
        return jsonify({"error": "Invalid URL"}), 400
    
    if alias and alias in url_data["links"]:
        return jsonify({"error": "Alias already exists"}), 409
    
    # Generate alias if not provided
    if not alias:
        alias = generate_random_alias()
    
    link_data = {
        "url": url,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "clicks": 0,
        "user_id": session['user_id'],
        "expiry_date": None,
        "password": None,
        "utm_tracking": False
    }
    
    url_data["links"][alias] = link_data
    save_data()
    
    return jsonify({"message": "Link created", "alias": alias}), 201

# ========== END TEST ENDPOINTS ==========
