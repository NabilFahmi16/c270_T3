from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

# In-memory storage
url_map = {
    "ci":   "https://github.com/NabilFahmi16/c270_T3/actions",
    "repo": "https://github.com/NabilFahmi16/c270_T3"
}

# Cleaned-up HTML template
HOME_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Simple URL Shortener</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f9f9f9; }
        h1 { color: #333; text-align: center; }
        .box { max-width: 640px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input, button { padding: 12px; font-size: 16px; border-radius: 4px; }
        input { width: 100%; margin: 10px 0; border: 1px solid #ccc; }
        button { background: #0066cc; color: white; border: none; cursor: pointer; width: 100%; }
        button:hover { background: #0055aa; }
        .msg { margin: 20px 0; padding: 12px; border-radius: 4px; }
        .success { background: #e0ffe0; border-left: 4px solid #28a745; }
        .error   { background: #ffe0e0; border-left: 4px solid #dc3545; }
        ul { padding-left: 20px; list-style: none; }
        li { margin: 10px 0; }
        .small { color: #555; font-size: 0.9em; margin-top: 40px; text-align: center; }
    </style>
</head>
<body>
    <div class="box">
        <h1>Simple URL Shortener</h1>

        {% if message %}
        <div class="msg {{ 'success' if not error else 'error' }}">
            {{ message }}
        </div>
        {% endif %}

        <form method="post">
            <input name="alias" placeholder="Short name (e.g. demo)" required autocomplete="off">
            <input name="url"   placeholder="Full URL[](https://example.com)" required>
            <button type="submit">Create Short Link</button>
        </form>

        <h3>Existing short links</h3>
        <ul>
        {% for alias, long_url in url_map.items() %}
            <li>
                <strong>/go/{{ alias }}</strong> →
                <a href="/go/{{ alias }}" target="_blank">{{ long_url }}</a>
            </li>
        {% endfor %}
        </ul>

        <div class="small">
            C270 DevOps • Republic Polytechnic • Local: http://localhost:5000/go/...
        </div>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    message = ""
    error = False

    if request.method == 'POST':
        alias = request.form.get('alias', '').strip()
        url   = request.form.get('url',   '').strip()

        if not alias or not url:
            message = "Please fill both fields."
            error = True
        elif not url.startswith(('http://', 'https://')):
            message = "URL must start with http:// or https://"
            error = True
        elif alias in url_map:
            message = f"Alias '{alias}' is already taken."
            error = True
        else:
            url_map[alias] = url
            message = f"Short link created! → <strong>http://localhost:5000/go/{alias}</strong>"
            # You can also do: message = f"Created! → /go/{alias}" if you prefer relative

    return render_template_string(HOME_PAGE, url_map=url_map, message=message, error=error)


@app.route('/go/<alias>')
def redirect_link(alias):
    if alias in url_map:
        return redirect(url_map[alias])
    return "Not found", 404


@app.route('/health')
def health():
    return {"status": "ok"}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)