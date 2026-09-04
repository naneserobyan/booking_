# Booking Availability Checker

A full-stack Python project simulating a vacation rental booking system,
with a booking-site-style search flow: country, dates, guests, filters,
and price sorting. Core logic (`models.py`, `booking_system.py`) is plain
Python and unchanged; `app.py` adds the web interface on top of it.

## Structure

- `models.py`, `booking_system.py` — core booking logic (unchanged)
- `cli.py` — terminal interface (unchanged)
- `app.py` — Flask web app (customer page + admin dashboard)
- `templates/` — `index.html` (customer), `admin.html` / `admin_login.html` (staff)
- `test_booking_system.py` — unit tests

## Run it

```bash
pip install -r requirements.txt
python app.py
```


### Customer flow
1. Enter a destination country, dates, and number of guests.
2. See only rooms that are actually available for those dates, filterable
   by breakfast / parking / city center, sortable by price.
3. Enter your name and reserve. If the room was just taken, you're told
   immediately and asked to pick different dates.

### Staff
Go to **/admin** (password: `admin123` for this demo) to add rooms
(with country, price, amenities, photos) and see every booking — this
page is never visible to customers.

## Tests

```bash
python -m unittest test_booking_system.py -v
```
