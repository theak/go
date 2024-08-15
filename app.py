import requests
from flask import Flask, g, render_template, request, redirect
import db
from urllib.parse import urlparse

app = Flask(__name__)
DOMAIN = "go"

''' MAIN ROUTES '''
@app.route('/', methods=['GET'])
def root(error: str|None = None):
    links = db.get_all_links()
    return render_template("submitlink.html", domain=DOMAIN, links=links, error=error)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    url = db.get_url_from_name(path)
    if url is None:
      return render_template("submitlink.html", name=path, domain=DOMAIN)
    else:
      return redirect(url)

@app.route('/submit_link', methods=['POST'])
def submit_link():
    name = request.form.get('name')
    url = request.form.get('url')

    if not name or not url:
        return root("Error: Both name and URL are required."), 400
    if db.get_url_from_name(name):
        return root(f"Error: {DOMAIN}/{name} already exists. If you're trying to modify it, delete it first."), 400
    if not _is_valid_url(url):
        return root("Error: Invalid URL"), 400

    db.create_url(name, url)
    return root()

@app.route('/delete_link', methods=['POST'])
def delete_link():
    id = request.form.get('id')

    if not id or not id.isnumeric():
        return root("Error: Invalid ID."), 400

    db.delete_link(int(id))
    return root()

''' MISC ROUTES '''
@app.route('/ping', methods=['GET'])
def ping():
    r = requests.get("http://192.168.0.155:8123")
    if r.status_code == 200:
        return 'OK'
    else:
        return "Error: %d" % r.status_code, 400

@app.route('/robots.txt', methods=['GET'])
def robots():
    return Response('User-agent: *\nDisallow: /', mimetype='text/plain')

''' DATABASE '''
@app.teardown_appcontext
def close_connection(exception):
    return db.close_connection(exception)

''' HELPER FUNCTIONS '''
def _is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

if __name__ == '__main__':
    db.init_db(app)
    app.run(debug=True)
