import json
import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "listings.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

DEFAULT_BLUE_CHIP_SUBURBS = [
    "Toorak", "Malvern", "Camberwell", "Hawthorn", "Kew", "Brighton",
    "Armadale", "South Yarra", "Canterbury", "Balwyn",
]

STATUS_CHOICES = [
    "watching", "inspected", "offer_made", "rejected", "withdrawn", "purchased",
]


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    if get_setting(conn, "blue_chip_suburbs") is None:
        set_setting(conn, "blue_chip_suburbs", json.dumps(DEFAULT_BLUE_CHIP_SUBURBS))
    conn.commit()
    conn.close()


def get_setting(conn, key):
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def set_setting(conn, key, value):
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def get_blue_chip_suburbs(conn):
    return json.loads(get_setting(conn, "blue_chip_suburbs") or "[]")


def list_listings(conn, status=None, order_by="date_added", descending=True):
    valid_columns = {
        "date_added", "price_numeric", "bedrooms", "bathrooms",
        "distance_to_station_m", "commute_to_flinders_min", "suburb",
    }
    if order_by not in valid_columns:
        order_by = "date_added"
    direction = "DESC" if descending else "ASC"
    sql = f"SELECT * FROM listings"
    params = ()
    if status:
        sql += " WHERE status = ?"
        params = (status,)
    sql += f" ORDER BY {order_by} {direction}"
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def get_listing(conn, listing_id):
    row = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    return dict(row) if row else None


LISTING_FIELDS = [
    "address", "suburb", "price_text", "price_numeric", "bedrooms", "bathrooms",
    "car_spaces", "land_size_sqm", "nearest_station", "distance_to_station_m",
    "commute_to_flinders_min", "aspect", "full_of_light", "listing_url",
    "agent_name", "agent_phone", "inspection_date", "status", "notes",
]


def create_listing(conn, data):
    now = datetime.now(timezone.utc).isoformat()
    values = {field: data.get(field) for field in LISTING_FIELDS}
    columns = ", ".join(values.keys())
    placeholders = ", ".join(["?"] * len(values))
    cur = conn.execute(
        f"INSERT INTO listings ({columns}, date_added, date_updated) "
        f"VALUES ({placeholders}, ?, ?)",
        (*values.values(), now, now),
    )
    conn.commit()
    return cur.lastrowid


def update_listing(conn, listing_id, data):
    now = datetime.now(timezone.utc).isoformat()
    values = {field: data.get(field) for field in LISTING_FIELDS}
    assignments = ", ".join(f"{field} = ?" for field in values.keys())
    conn.execute(
        f"UPDATE listings SET {assignments}, date_updated = ? WHERE id = ?",
        (*values.values(), now, listing_id),
    )
    conn.commit()


def delete_listing(conn, listing_id):
    conn.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
    conn.commit()
