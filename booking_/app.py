
import json
import os
import uuid
from datetime import date
from functools import wraps
from urllib.parse import urlencode

from flask import Flask, flash, redirect, render_template, request, session, url_for

from booking_system import BookingSystem, NotAvailableError, PropertyNotFoundError

app = Flask(__name__)
app.secret_key = "dev-secret-key"

system = BookingSystem(data_file="data.json")

ADMIN_PASSWORD = "admin123"

PHOTOS_FILE = "photos.json"
AMENITIES_FILE = "amenities.json"

# Each entry is a pair of photos for one room (customer can flip between them)
PLACEHOLDER_IMAGE_SETS = [
    [
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=500&q=80",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=500&q=80",
    ],
    [
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=500&q=80",
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=500&q=80",
    ],
    [
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=500&q=80",
        "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?w=500&q=80",
    ],
    [
        "https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=500&q=80",
        "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=500&q=80",
    ],
    [
        "https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?w=500&q=80",
        "https://images.unsplash.com/photo-1571508601891-ca5e7a713859?w=500&q=80",
    ],
    [
        "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?w=500&q=80",
        "https://images.unsplash.com/photo-1598928506311-c55ded91a20c?w=500&q=80",
    ],
    [
        "https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=500&q=80",
        "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=500&q=80",
    ],
    [
        "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=500&q=80",
        "https://images.unsplash.com/photo-1560185893-a55cbc8c57e8?w=500&q=80",
    ],
    [
        "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=500&q=80",
        "https://images.unsplash.com/photo-1560449017-7d5c1de65a63?w=500&q=80",
    ],
    [
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500&q=80",
        "https://images.unsplash.com/photo-1615529182904-14819c35db37?w=500&q=80",
    ],
]


def load_json(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_property_id() -> str:
    return uuid.uuid4().hex[:8]


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


def build_search_url(overrides: dict) -> str:
    """
    Takes the current query string and applies overrides (a key set to
    None is removed). Used to build one-click filter/sort links that
    keep the rest of the search intact.
    """
    args = request.args.to_dict(flat=True)
    for key, value in overrides.items():
        if value is None:
            args.pop(key, None)
        else:
            args[key] = value
    query = urlencode(args)
    return url_for("index") + ("?" + query if query else "")


# ---------------------------------------------------------------------
# Customer-facing pages
# ---------------------------------------------------------------------

@app.route("/")
def index():
    check_in_raw = request.args.get("check_in", "").strip()
    check_out_raw = request.args.get("check_out", "").strip()
    country_query = request.args.get("country", "").strip()
    guests = request.args.get("guests", "").strip()
    sort_by = request.args.get("sort", "")
    want_breakfast = request.args.get("breakfast") == "on"
    want_parking = request.args.get("parking") == "on"
    want_central = request.args.get("central") == "on"

    searched = bool(check_in_raw and check_out_raw)

    all_properties = system.list_properties()
    photos = load_json(PHOTOS_FILE)
    amenities = load_json(AMENITIES_FILE)

    def get_photos(pid):
        return photos.get(pid, PLACEHOLDER_IMAGE_SETS[0])

    def get_amenities(pid):
        return amenities.get(pid, {"country": "", "breakfast": False, "parking": False, "central": False})

    rooms = []
    search_error = None
    candidates = all_properties

    if searched:
        try:
            check_in = date.fromisoformat(check_in_raw)
            check_out = date.fromisoformat(check_out_raw)
            if check_in >= check_out:
                search_error = "Check-out must be after check-in."
                candidates = []
        except ValueError:
            search_error = "Please enter valid dates."
            candidates = []

    for p in candidates:
        meta = get_amenities(p.property_id)

        if country_query and country_query.lower() not in meta["country"].lower():
            continue
        if want_breakfast and not meta["breakfast"]:
            continue
        if want_parking and not meta["parking"]:
            continue
        if want_central and not meta["central"]:
            continue

        total_price = None
        if searched and not search_error:
            if not system.is_available(p.property_id, check_in, check_out):
                continue
            total_price = system.calculate_price(p.property_id, check_in, check_out)

        rooms.append({
            "prop": p,
            "photos": get_photos(p.property_id),
            "meta": meta,
            "total_price": total_price,
        })

    if sort_by == "price_asc":
        rooms.sort(key=lambda r: r["total_price"] if r["total_price"] is not None else r["prop"].price_per_night)
    elif sort_by == "price_desc":
        rooms.sort(key=lambda r: r["total_price"] if r["total_price"] is not None else r["prop"].price_per_night, reverse=True)

    # one-click links (no Apply button, no JS)
    urls = {
        "breakfast": build_search_url({"breakfast": None if want_breakfast else "on"}),
        "parking": build_search_url({"parking": None if want_parking else "on"}),
        "central": build_search_url({"central": None if want_central else "on"}),
        "sort_asc": build_search_url({"sort": None if sort_by == "price_asc" else "price_asc"}),
        "sort_desc": build_search_url({"sort": None if sort_by == "price_desc" else "price_desc"}),
    }

    return render_template(
        "index.html",
        rooms=rooms,
        searched=searched,
        search_error=search_error,
        check_in=check_in_raw,
        check_out=check_out_raw,
        country=country_query,
        guests=guests,
        sort_by=sort_by,
        want_breakfast=want_breakfast,
        want_parking=want_parking,
        want_central=want_central,
        urls=urls,
        has_any_rooms=bool(all_properties),
    )


@app.route("/book", methods=["POST"])
def book():
    property_id = request.form.get("property_id", "")
    guest_name = request.form.get("guest_name", "").strip()
    guests = request.form.get("guests", "").strip()
    check_in_raw = request.form.get("check_in", "")
    check_out_raw = request.form.get("check_out", "")

    if not guest_name:
        flash("Please enter your name to reserve.", "err")
        return redirect(url_for("index", check_in=check_in_raw, check_out=check_out_raw))

    try:
        check_in = date.fromisoformat(check_in_raw)
        check_out = date.fromisoformat(check_out_raw)
        booking = system.book(property_id, guest_name, check_in, check_out)
        price = system.calculate_price(property_id, check_in, check_out)
        guest_note = f" for {guests} guest(s)" if guests else ""
        flash(
            f"Reserved{guest_note}! {booking.check_in} \u2192 {booking.check_out} "
            f"({booking.nights()} nights) \u2014 total ${price}",
            "ok",
        )
        return redirect(url_for("index"))

    except NotAvailableError:
        flash("Sorry — this room was just booked for those dates. Please try different dates.", "err")
    except PropertyNotFoundError:
        flash("This room no longer exists.", "err")
    except ValueError:
        flash("Something went wrong with those dates. Please try again.", "err")

    return redirect(url_for("index", check_in=check_in_raw, check_out=check_out_raw))


# ---------------------------------------------------------------------
# Admin pages
# ---------------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Incorrect password.", "err")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    properties = system.list_properties()
    amenities = load_json(AMENITIES_FILE)
    rows = [{"prop": p, "meta": amenities.get(p.property_id, {})} for p in properties]
    return render_template("admin.html", rows=rows)


@app.route("/admin/add-property", methods=["POST"])
@admin_required
def add_property():
    name = request.form.get("name", "").strip()
    price_raw = request.form.get("price_per_night", "").strip()
    photo_choice = request.form.get("photo_choice", "0")
    country = request.form.get("country", "").strip()
    breakfast = request.form.get("breakfast") == "on"
    parking = request.form.get("parking") == "on"
    central = request.form.get("central") == "on"

    if not name:
        flash("Please enter a room name.", "err")
        return redirect(url_for("admin_dashboard"))

    try:
        price = float(price_raw)
        new_id = generate_property_id()
        system.add_property(new_id, name, price)

        photos = load_json(PHOTOS_FILE)
        try:
            idx = int(photo_choice) % len(PLACEHOLDER_IMAGE_SETS)
        except ValueError:
            idx = 0
        photos[new_id] = PLACEHOLDER_IMAGE_SETS[idx]
        save_json(PHOTOS_FILE, photos)

        amenities = load_json(AMENITIES_FILE)
        amenities[new_id] = {
            "country": country,
            "breakfast": breakfast,
            "parking": parking,
            "central": central,
        }
        save_json(AMENITIES_FILE, amenities)

        flash(f"'{name}' was added.", "ok")
    except ValueError:
        flash("Could not add the room. Please check the price (must be a number greater than 0).", "err")

    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
