from flask import Flask, g, render_template, request, redirect, send_file
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

@app.route('/settings', methods=['GET'])
def settings():
  return render_template("settings.html", domain=DOMAIN)

@app.route('/backup', methods=['GET'])
def backup():
  return send_file(db.get_db_path(), as_attachment=True, download_name='sqlite.db')

@app.route('/reset', methods=['POST'])
def reset():
  db.reset_db(app)
  return redirect('/')

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
    return redirect('/')

@app.route('/update_link', methods=['POST'])
def update_link():
    id = request.form.get('id')
    action = request.form.get('action')

    if not id or not id.isnumeric():
        return root("Error: Invalid ID."), 400

    if action == "delete":
      db.delete_link(int(id))

    if action == "rename":
      db.rename_link(int(id), request.form.get('newName'))

    return redirect('/')

''' MISC ROUTES '''
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
