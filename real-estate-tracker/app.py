import json

from flask import Flask, g, redirect, render_template, request, url_for

import criteria
import db

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = db.get_connection()
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


@app.route("/")
def index():
    conn = get_db()
    status = request.args.get("status") or None
    order_by = request.args.get("order_by", "date_added")
    descending = request.args.get("dir", "desc") != "asc"
    only_qualifying = request.args.get("qualifying") == "1"

    blue_chip_suburbs = db.get_blue_chip_suburbs(conn)
    listings = db.list_listings(conn, status=status, order_by=order_by, descending=descending)

    rows = []
    for listing in listings:
        checks = criteria.evaluate(listing, blue_chip_suburbs)
        qualifies = criteria.qualifies(checks)
        if only_qualifying and not qualifies:
            continue
        rows.append({"listing": listing, "checks": checks, "qualifies": qualifies})

    return render_template(
        "index.html",
        rows=rows,
        status=status,
        order_by=order_by,
        descending=descending,
        only_qualifying=only_qualifying,
        status_choices=db.STATUS_CHOICES,
    )


def _form_to_data(form):
    def to_int(name):
        value = form.get(name, "").strip()
        return int(value) if value else None

    def to_float(name):
        value = form.get(name, "").strip()
        return float(value) if value else None

    return {
        "address": form.get("address", "").strip(),
        "suburb": form.get("suburb", "").strip(),
        "price_text": form.get("price_text", "").strip() or None,
        "price_numeric": to_float("price_numeric"),
        "bedrooms": to_int("bedrooms"),
        "bathrooms": to_int("bathrooms"),
        "car_spaces": to_int("car_spaces"),
        "land_size_sqm": to_float("land_size_sqm"),
        "nearest_station": form.get("nearest_station", "").strip() or None,
        "distance_to_station_m": to_int("distance_to_station_m"),
        "commute_to_flinders_min": to_int("commute_to_flinders_min"),
        "aspect": form.get("aspect", "").strip() or None,
        "full_of_light": 1 if form.get("full_of_light") == "on" else 0,
        "listing_url": form.get("listing_url", "").strip() or None,
        "agent_name": form.get("agent_name", "").strip() or None,
        "agent_phone": form.get("agent_phone", "").strip() or None,
        "inspection_date": form.get("inspection_date", "").strip() or None,
        "status": form.get("status", "watching"),
        "notes": form.get("notes", "").strip() or None,
    }


@app.route("/listings/new", methods=["GET", "POST"])
def new_listing():
    if request.method == "POST":
        conn = get_db()
        listing_id = db.create_listing(conn, _form_to_data(request.form))
        return redirect(url_for("view_listing", listing_id=listing_id))
    return render_template("listing_form.html", listing=None, status_choices=db.STATUS_CHOICES)


@app.route("/listings/<int:listing_id>")
def view_listing(listing_id):
    conn = get_db()
    listing = db.get_listing(conn, listing_id)
    if listing is None:
        return redirect(url_for("index"))
    blue_chip_suburbs = db.get_blue_chip_suburbs(conn)
    checks = criteria.evaluate(listing, blue_chip_suburbs)
    qualifies = criteria.qualifies(checks)
    return render_template("listing_detail.html", listing=listing, checks=checks, qualifies=qualifies)


@app.route("/listings/<int:listing_id>/edit", methods=["GET", "POST"])
def edit_listing(listing_id):
    conn = get_db()
    if request.method == "POST":
        db.update_listing(conn, listing_id, _form_to_data(request.form))
        return redirect(url_for("view_listing", listing_id=listing_id))
    listing = db.get_listing(conn, listing_id)
    if listing is None:
        return redirect(url_for("index"))
    return render_template("listing_form.html", listing=listing, status_choices=db.STATUS_CHOICES)


@app.route("/listings/<int:listing_id>/delete", methods=["POST"])
def delete_listing(listing_id):
    conn = get_db()
    db.delete_listing(conn, listing_id)
    return redirect(url_for("index"))


@app.route("/settings", methods=["GET", "POST"])
def settings():
    conn = get_db()
    if request.method == "POST":
        suburbs = [s.strip() for s in request.form.get("blue_chip_suburbs", "").split("\n") if s.strip()]
        db.set_setting(conn, "blue_chip_suburbs", json.dumps(suburbs))
        conn.commit()
        return redirect(url_for("settings"))
    blue_chip_suburbs = db.get_blue_chip_suburbs(conn)
    return render_template(
        "settings.html",
        blue_chip_suburbs="\n".join(blue_chip_suburbs),
        criteria=criteria,
    )


with app.app_context():
    db.init_db()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
