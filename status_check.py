import requests

import db

def set_status_check(id: int, status_check: bool):
    db.modify_db("UPDATE link SET status_check = ? WHERE id = ?", [status_check, id])

def get_statuses() -> dict[int, int]:
    statuses = db.query_db("""SELECT link_id, status
      FROM status_checks
      WHERE (link_id, created_date) IN (
          SELECT link_id, MAX(created_date)
          FROM status_checks
          GROUP BY link_id
      );
      """,)
    out = {}
    for status in statuses:
      out[int(status["link_id"])] = int(status["status"])
    return out

def get_last_downtimes() -> dict[int, int]:
    links = db.query_db("""SELECT link_id, MAX(created_date) as last_downtime
      FROM status_checks
      WHERE status >= 400
      GROUP BY link_id;
      """,)
    out = {}
    for link in links:
      out[int(link["link_id"])] = link["last_downtime"]
    return out

def update_all_statuses():
    for link in db.get_all_links(status_check=True):
      update_status(link["id"])

def update_status(link_id) -> bool:
    link = db.get_link_from_id(link_id)
    status = False
    if link is not None:
      status = requests.get(link["url"]).status_code
      db.modify_db("INSERT INTO status_checks (link_id, status) VALUES (?, ?)", (link_id, status))
    return status
