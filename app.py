import json
import os
import sys
from urllib.parse import urlparse

from flask import Flask, Response, redirect, render_template, request, send_file

import db

app = Flask(__name__)
app.url_map.strict_slashes = False  # Disable strict slashes
DOMAIN = "go"

ALLOWED_EXTENSIONS = {"json"}

""" MAIN ROUTES """


@app.route("/", methods=["GET"])
def root(error: str | None = None, newlink: dict | None = None):
    links = db.get_all_links()
    return render_template(
        "submitlink.html", domain=DOMAIN, links=links, error=error, newlink=newlink
    )


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    split_path = path.split("/", 1)
    name = split_path[0]
    url = db.get_url_from_name(name)
    if url is None:
        return render_template("submitlink.html", name=name, domain=DOMAIN)
    else:
        if len(split_path) > 1:
            url += split_path[1]
        return redirect(url)


@app.route("/note/<name>", methods=["GET", "POST"])
def note(name):
    if request.method == "POST":
        if db.get_url_from_name(name) is None:
            db.create_url(name, f"/note/{name}", description="🟨")
        db.set_note(name, request.form.get("content", ""))
    return render_template(
        "note.html", domain=DOMAIN, name=name, content=db.get_note(name) or ""
    )


@app.route("/newnote")
def newnote():
    return redirect("/note")


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_file("favicon.ico")


@app.route("/settings", methods=["GET"])
def settings():
    return render_template("settings.html", domain=DOMAIN)


@app.route("/backup", methods=["GET"])
def backup():
    json_data = db.export_links_json()
    return Response(json_data, mimetype="application/json",
                    headers={"Content-Disposition": "attachment;filename=links.json"})


@app.route("/restore", methods=["POST"])
def restore():
    if "file" not in request.files:
        return "No file", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400
    if not _allowed_file(file.filename):
        return "File type not allowed", 400

    try:
        json_str = file.read().decode("utf-8")
        db.import_links_json(json_str)
        return redirect("/")
    except (json.JSONDecodeError, KeyError) as e:
        return f"Invalid JSON: {e}", 400


@app.route("/reset", methods=["POST"])
def reset():
    db.reset_db(app)
    return redirect("/")


@app.route("/submit_link", methods=["POST"])
def submit_link():
    name = request.form.get("name")
    url = request.form.get("url")

    if not name:
        return root("Error: Name is required."), 400
    if db.get_url_from_name(name):
        return root(
            f"Error: {DOMAIN}/{name} already exists. If you're trying to modify it, delete it first."
        ), 400
    if not url:
        db.create_url(name, f"/note/{name}", description="🟨")
        return redirect(f"/note/{name}")
    if not _is_valid_url(url):
        return root("Error: Invalid URL"), 400

    db.create_url(name, url)
    return root(newlink={"name": name, "url": url})


@app.route("/update_link", methods=["POST"])
def update_link():
    id = request.form.get("id")
    action = request.form.get("action")

    if not id or not id.isnumeric():
        return root("Error: Invalid ID."), 400

    if action == "delete":
        db.delete_link(int(id))

    if action == "rename":
        db.rename_link(int(id), request.form.get("newName"))

    if action == "edit_url":
        db.update_url(int(id), request.form.get("newUrl"))

    return redirect("/")


""" MISC ROUTES """


@app.route("/robots.txt", methods=["GET"])
def robots():
    return Response("User-agent: *\nDisallow: /", mimetype="text/plain")


""" DATABASE """


@app.teardown_appcontext
def close_connection(exception):
    return db.close_connection(exception)


""" HELPER FUNCTIONS """


def _is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc or result.path])
    except ValueError:
        return False


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    db.init_db(app)
    if sys.argv[-1] != "init_db":
        app.run(debug=True)
