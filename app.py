import json
import os
import secrets
import sys
from io import BytesIO
from urllib.parse import urlparse

from flask import Flask, Response, abort, jsonify, redirect, render_template, request, send_file

import db

app = Flask(__name__)
app.url_map.strict_slashes = False  # Disable strict slashes
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload cap
DOMAIN = "go"

ALLOWED_EXTENSIONS = {"json"}

""" MAIN ROUTES """


@app.route("/", methods=["GET"])
def root(error: str | None = None, newlink: dict | None = None):
    links = db.get_all_links()
    return render_template(
        "submitlink.html", domain=DOMAIN, links=links, error=error, newlink=newlink,
        deleted=request.args.get("deleted"),
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
        if db.get_link(name) is None:
            db.create_url(name, f"/note/{name}", description="🟨")
        db.set_note(name, request.form.get("content", ""), request.form.get("markdown") is not None)
        return redirect(f"/note/{name}")
    link = db.get_link(name)
    meta = json.loads(link["metadata"] or "{}") if link else {}
    return render_template(
        "note.html", domain=DOMAIN, name=name,
        content=meta.get("note", ""),
        markdown=meta.get("markdown", False),
        conflict=link is not None and link["url"] != f"/note/{name}",
        id=link["id"] if link else None,
        created=link["created_date"] if link else None,
    )


@app.route("/newnote", defaults={"name": ""})
@app.route("/newnote/<name>")
def newnote(name):
    return redirect(f"/note/{name}" if name else "/note")


@app.route("/note/upload_image", methods=["POST"])
def upload_image():
    file = request.files.get("image")
    if file is None or not file.mimetype.startswith("image/"):
        return "Invalid image", 400
    img_id = secrets.token_urlsafe(8)
    db.save_image(img_id, file.mimetype, file.read())
    return {"url": f"/note/img/{img_id}"}


@app.route("/note/img/<img_id>")
def image(img_id):
    img = db.get_image(img_id)
    if img is None:
        abort(404)
    return send_file(BytesIO(img["data"]), mimetype=img["content_type"], max_age=31536000)


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_file("favicon.ico")


@app.route("/settings", methods=["GET"])
def settings():
    return render_template("settings.html", domain=DOMAIN,
                           images=db.count_images(), cleaned=request.args.get("cleaned"))


@app.route("/cleanup_images", methods=["POST"])
def cleanup_images():
    count = db.delete_unused_images()
    return redirect(f"/settings?cleaned={count}")


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

    if action == "restore":
        db.restore_link(
            request.form.get("name"),
            request.form.get("url"),
            request.form.get("description"),  # None -> stays NULL
            request.form.get("metadata"),
        )
        return redirect("/")

    if not id or not id.isnumeric():
        return root("Error: Invalid ID."), 400

    if action == "delete":
        link = db.get_link_by_id(int(id))
        db.delete_link(int(id))
        return jsonify(dict(link)) if link else ("Not found", 404)

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
