import requests
from flask import Flask, g, render_template, request, redirect
import db, status_check
from urllib.parse import urlparse

app = Flask(__name__)
DOMAIN = "go"

''' MAIN ROUTES '''
@app.route('/', methods=['GET'])
def root(error: str|None = None):
    links = db.get_all_links()
    return render_template("submitlink.html", domain=DOMAIN, links=links, error=error)

@app.route('/status', methods=['GET'])
def status():
    status_check.update_all_statuses()
    links = db.get_all_links(status_check=False)
    status_links = db.get_all_links(status_check=True)
    statuses = status_check.get_statuses()
    downtimes = status_check.get_last_downtimes()
    return render_template("submitlink.html", domain=DOMAIN, links=links, status=True, status_links=status_links, statuses=statuses, downtimes=downtimes)

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

@app.route('/update_link', methods=['POST'])
def update_link():
    id = request.form.get('id')
    action = request.form.get('action')

    if not id or not id.isnumeric():
        return root("Error: Invalid ID."), 400

    if action == "delete":
      db.delete_link(int(id))
      return root()
    elif action == "add_status_check":
      status_check.set_status_check(int(id), True)
    elif action == "remove_status_check":
      status_check.set_status_check(int(id), False)
    return status()

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
def _is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

if __name__ == '__main__':
    db.init_db(app)
    app.run(debug=True)
