import sqlite3
import requests
from flask import g

DB = 'sqlite.db'

def get_url_from_name(name: str) -> str:
    link = query_db("SELECT url FROM link WHERE name = ?", [name], one=True)
    return None if link is None else link["url"]

def get_all_links(limit: int = 100) -> list[sqlite3.Row]:
    links = query_db("""SELECT * FROM link
      ORDER BY description IS NOT NULL DESC, id ASC
      LIMIT ?""", [limit])
    return links

def delete_link(id: int):
    modify_db("DELETE FROM link WHERE id = ?", [id])

def rename_link(id: int, newName: str):
    modify_db("UPDATE link SET description = ? WHERE id = ?", [newName, id])

def create_url(name: str, url: str):
    modify_db("INSERT INTO link (name, url) VALUES (?, ?)", (name, url))

def get_link_from_id(id: int) -> str:
    return query_db("SELECT url FROM link WHERE id = ?", [id], one=True)

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
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

def _get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB)
        db.row_factory = sqlite3.Row
    return db
