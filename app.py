# app.py (BASIC VERSION)
from flask import Flask, jsonify, request, redirect

app = Flask(__name__)

url_map = {
    "ci": "https://github.com/NabilFahmi16/c270_T3/actions",
    "repo": "https://github.com/NabilFahmi16/c270_T3"
}

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/links')
def list_links():
    return jsonify(url_map), 200

@app.route('/shorten', methods=['POST'])
def shorten():
    data = request.get_json()
    if not data or 'alias' not in data or 'url' not in 
        return jsonify({"error": "Missing alias or url"}), 400
    url_map[data['alias']] = data['url']
    return jsonify({"message": "Added"}), 201

@app.route('/go/<alias>')
def go(alias):
    if alias in url_map:
        return redirect(url_map[alias])
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)