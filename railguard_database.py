import sqlite3, os
from datetime import datetime
from config import DATABASE_PATH, TRACK


def db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    c = sqlite3.connect(DATABASE_PATH, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    c = db()
    c.execute("""CREATE TABLE IF NOT EXISTS detections(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp TEXT NOT NULL,
      object_type TEXT NOT NULL,
      label TEXT NOT NULL,
      confidence REAL NOT NULL,
      risk TEXT NOT NULL,
      camera_id TEXT NOT NULL,
      track_id TEXT NOT NULL,
      location TEXT NOT NULL,
      zone TEXT NOT NULL,
      status TEXT DEFAULT 'Active')""")
    c.execute("""CREATE TABLE IF NOT EXISTS alerts(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp TEXT NOT NULL,
      title TEXT NOT NULL,
      message TEXT NOT NULL,
      severity TEXT NOT NULL,
      object_type TEXT NOT NULL,
      camera_id TEXT NOT NULL,
      track_id TEXT NOT NULL,
      status TEXT DEFAULT 'New')""")
    c.commit(); c.close()


def add_detection(kind, label, conf, risk):
    c = db()
    c.execute("""INSERT INTO detections
      (timestamp,object_type,label,confidence,risk,camera_id,track_id,location,zone)
      VALUES(?,?,?,?,?,?,?,?,?)""", (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), kind, label, conf, risk,
        TRACK["camera_id"], TRACK["track_id"], TRACK["location"], TRACK["zone"]))
    c.commit(); c.close()


def add_alert(title, msg, severity, kind):
    c = db()
    c.execute("""INSERT INTO alerts
      (timestamp,title,message,severity,object_type,camera_id,track_id)
      VALUES(?,?,?,?,?,?,?)""", (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), title, msg, severity, kind,
        TRACK["camera_id"], TRACK["track_id"]))
    c.commit(); c.close()


def detections(limit=300, object_type=None, risk=None):
    c = db()
    sql = "SELECT * FROM detections WHERE 1=1"
    params = []
    if object_type in ("Human", "Animal"):
        sql += " AND object_type=?"; params.append(object_type)
    if risk in ("High", "Medium", "Low"):
        sql += " AND risk=?"; params.append(risk)
    sql += " ORDER BY id DESC LIMIT ?"; params.append(int(limit))
    rows = c.execute(sql, params).fetchall(); c.close()
    return [dict(x) for x in rows]


def alerts(limit=100, unread_only=False):
    c = db()
    sql = "SELECT * FROM alerts"
    params = []
    if unread_only:
        sql += " WHERE status='New'"
    sql += " ORDER BY id DESC LIMIT ?"; params.append(int(limit))
    rows = c.execute(sql, params).fetchall(); c.close()
    return [dict(x) for x in rows]


def stats():
    c = db()
    total = c.execute("SELECT COUNT(*) FROM detections").fetchone()[0]
    humans = c.execute("SELECT COUNT(*) FROM detections WHERE object_type='Human'").fetchone()[0]
    animals = c.execute("SELECT COUNT(*) FROM detections WHERE object_type='Animal'").fetchone()[0]
    high = c.execute("SELECT COUNT(*) FROM detections WHERE risk='High'").fetchone()[0]
    avg = c.execute("SELECT AVG(confidence) FROM detections").fetchone()[0]
    active = c.execute("SELECT COUNT(*) FROM alerts WHERE status='New'").fetchone()[0]
    latest = c.execute("SELECT * FROM detections ORDER BY id DESC LIMIT 1").fetchone()
    c.close()
    latest = dict(latest) if latest else None
    risk_zone = "CRITICAL" if high else ("ELEVATED" if total else "CLEAR")
    return {
        "total": total, "humans": humans, "animals": animals, "high": high,
        "active": active, "accuracy": round((avg or 0) * 100, 1),
        "risk_zone": risk_zone, "latest": latest,
    }


def read_alert(i):
    c = db(); c.execute("UPDATE alerts SET status='Read' WHERE id=?", (i,)); c.commit(); c.close()


def clear_history():
    c = db(); c.execute("DELETE FROM detections"); c.execute("DELETE FROM alerts"); c.commit(); c.close()
