import json
import os, shutil
import sqlite3
from flask import g

DB = 'db/sqlite.db'

name_value_cache = {}

def get_url_from_name(name: str) -> str:
    link = query_db("SELECT url FROM link WHERE name = ?", [name], one=True)
    return None if link is None else link["url"]

def get_all_links(limit: int = 1000) -> list[sqlite3.Row]:
    links = query_db("""SELECT * FROM link
      ORDER BY description IS NOT NULL DESC, id ASC
      LIMIT ?""", [limit])
    return links

def get_value(name: str) -> str:
    cached_name = name_value_cache.get(name)
    if cached_name is not None: return cached_name
    value_row = query_db("SELECT value FROM name_values WHERE name = ?", [name], one=True)
    if value_row is not None:
      name_value_cache[name] = value_row['value']
      return value_row['value']

def update_value(name: str, value: str) -> str:
    modify_db("UPDATE name_values SET value = ? WHERE name = ?", [value, name])
    name_value_cache[name] = value

def delete_link(id: int):
    modify_db("DELETE FROM link WHERE id = ?", [id])

def rename_link(id: int, newName: str):
    modify_db("UPDATE link SET description = ? WHERE id = ?", [newName, id])

def update_url(id: int, new_url: str):
    modify_db("UPDATE link SET url = ? WHERE id = ?", [new_url, id])

def create_url(name: str, url: str, description: str = None):
    modify_db("INSERT INTO link (name, url, description) VALUES (?, ?, ?)", (name, url, description))

def get_link(name: str):
    return query_db("SELECT * FROM link WHERE name = ?", [name], one=True)

def set_note(name: str, content: str, markdown: bool = False):
    modify_db("UPDATE link SET metadata = json_set(metadata, '$.note', ?, '$.markdown', ?) WHERE name = ?",
              [content, markdown, name])

def save_image(id: str, content_type: str, data: bytes):
    modify_db("INSERT INTO image (id, content_type, data) VALUES (?, ?, ?)",
              (id, content_type, data))

def get_image(id: str):
    return query_db("SELECT content_type, data FROM image WHERE id = ?", [id], one=True)

def count_images() -> int:
    return query_db("SELECT count(*) AS c FROM image", one=True)["c"]

def delete_unused_images() -> int:
    notes = query_db("SELECT json_extract(metadata, '$.note') AS note FROM link")
    text = "\n".join(n["note"] or "" for n in notes)
    unused = [img["id"] for img in query_db("SELECT id FROM image") if img["id"] not in text]
    if unused:
        modify_db(f"DELETE FROM image WHERE id IN ({','.join('?' * len(unused))})", unused)
    return len(unused)

def export_links_json() -> str:
    links = query_db("SELECT name, url, description, metadata FROM link")
    return json.dumps({
        "version": 1,
        "links": [{"name": l["name"], "url": l["url"], "description": l["description"], "metadata": l["metadata"]} for l in links]
    }, indent=2)

def import_links_json(json_str: str) -> int:
    data = json.loads(json_str)
    for link in data.get("links", []):
        modify_db("""
            INSERT INTO link (name, url, description, metadata) VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET url=excluded.url, description=excluded.description, metadata=excluded.metadata
        """, (link["name"], link["url"], link.get("description"), link.get("metadata") or '{}'))
    return len(data.get("links", []))

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        os.makedirs(os.path.dirname(DB), exist_ok=True)
        db = _get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    cur = _get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def modify_db(query, args=()):
    db = _get_db()
    cur = db.cursor()
    cur.execute(query, args)
    db.commit()

def get_db_path():
    return os.path.join(os.getcwd(), DB)

def reset_db(app, new_db = None):
  os.remove(DB)
  if new_db is not None:
    shutil.copy(new_db, DB)
  name_value_cache = {}
  init_db(app)

def _get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB)
        db.row_factory = sqlite3.Row
    return db
