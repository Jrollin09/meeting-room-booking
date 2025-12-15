import datetime

from datetime import timedelta,timezone

from helpers.db import get_db_connection
from helpers.map_booking import map_booking

def cancel_booking_service(booking_id):
    db_connections = get_db_connection()
    try:
        with db_connections.cursor() as cur:
            cur.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
            booking = cur.fetchone()
            if not booking:
                raise KeyError("Unknown booking")
            
            now = datetime.datetime.now(timezone.utc).replace(tzinfo=None)
            if booking['start_time'] - now < timedelta(hours=1):
                 if booking['status'] != 'cancelled': 
                    raise ValueError("Cannot cancel within 1 hour of start time")

            if booking['status'] != 'cancelled':
                cur.execute("UPDATE bookings SET status = 'cancelled' WHERE id = %s RETURNING *", (booking_id,))
                booking = cur.fetchone()
                db_connections.commit()
            
            return map_booking(booking)
    finally:
        db_connections.close()
