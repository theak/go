import requests
from flask import Flask, g, render_template, request
import db

app = Flask(__name__)

''' MAIN ROUTES '''
@app.route('/', methods=['GET'])
def root():
    return render_template("submitlink.html")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    url = db.get_url_from_name(path)
    if url is None:
      return "URL not found"
    else:
      return str(url["url"])

# Endpoint to handle the form submission
@app.route('/submit_link', methods=['POST'])
def submit_link():
    name = request.form.get('name')
    url = request.form.get('url')

    if not name or not url:
        return "Both name and URL are required.", 400

    db.create_url(name, url)
    return 'Name: ' + name + ' Url: ' + url

''' PING ROUTES '''
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

if __name__ == '__main__':
    db.init_db(app)
    app.run(debug=True)
