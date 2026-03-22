import json
from datetime import datetime


BOOKING_FILE = "bookings.jsonl"


def save_booking(name, party_size, booking_time, booking_date, file_path=BOOKING_FILE):
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
