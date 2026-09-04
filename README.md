# Booking Checker – Property Booking Management System

## Overview

Booking Checker is a simple Property Booking Management System built to help manage room reservations and prevent double bookings.

The application provides separate interfaces for customers and administrators. Customers can browse available rooms and make reservations, while administrators can add new rooms and view booking history.

## Problems and Solution

The main problem I wanted to solve was **managing property reservations and preventing multiple customers from booking the same room for overlapping dates**.

In a booking system, it is important to track room availability accurately. Without proper validation, multiple customers could reserve the same property for the same dates, creating a double-booking problem.

To address this, I designed the system around two main entities: **Properties and Bookings**.

The system allows users to:

- Browse available rooms
- View room prices and photos
- Select check-in and check-out dates
- Create reservations
- Automatically check room availability
- Prevent overlapping bookings
- Calculate the total booking price

The system checks existing bookings before creating a new reservation. If the selected dates conflict with an existing booking, the reservation is rejected and the user receives a clear message.

I also separated the application into two different areas: a **Customer Interface** and an **Admin Dashboard**.

The customer can:

- Browse rooms
- Select booking dates
- Enter their name
- Create a reservation

The administrator can:

- Log in to the admin dashboard
- Add new rooms
- Set room prices
- Select room photos
- View all booking history

For data persistence, I used JSON files to store property and booking information. This allows the application to keep its data even after the program is restarted.

The project also separates the core booking logic from the web interface, making the application easier to maintain and extend.

## Technologies Used

- **Python** – Main backend programming language
- **Flask** – Web framework and application logic
- **HTML & CSS** – User interface and styling
- **JSON** – Data persistence
- **unittest** – Automated testing


## Project Architecture

The application is organized into separate components:

- `models.py` – Defines the Property and Booking entities
- `booking_system.py` – Contains the core booking and availability logic
- `app.py` – Connects the booking system with the Flask web application
- `templates/` – Contains the customer and administrator interfaces
- `data.json` – Stores properties and booking data
- `photos.json` – Stores room photo information
- `test_booking_system.py` – Contains automated tests

## Admin Access

The application includes a separate admin area for managing rooms and viewing booking history.

To access the admin dashboard:

1. Open the main application
2. Click **Staff Login**
3. Enter the demo password:

```text
Password: admin123
