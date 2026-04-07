import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SERVICE_DATABASE_DIR = BASE_DIR / "service_database"
BOOKING_FILE = SERVICE_DATABASE_DIR / "bookings.jsonl"
DELIVERY_FILE = SERVICE_DATABASE_DIR / "deliveries.jsonl"


def save_booking(name, party_size, booking_time, booking_date, file_path=BOOKING_FILE):
    SERVICE_DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    booking = {
        "name": name,
        "party_size": party_size,
        "time": booking_time,
        "date": booking_date,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    with open(file_path, "a", encoding="utf-8") as booking_file:
        booking_file.write(json.dumps(booking) + "\n")

    return booking


def save_delivery(name, address, order=None, total=0, file_path=DELIVERY_FILE):
    SERVICE_DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    delivery = {
        "name": name,
        "address": address,
        "order": order or [],
        "total": total,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    with open(file_path, "a", encoding="utf-8") as delivery_file:
        delivery_file.write(json.dumps(delivery) + "\n")

    return delivery
