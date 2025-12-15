import datetime
from datetime import timedelta
from helpers.db import get_db_connection
from helpers.map_booking import map_booking
from helpers.errors import ConflictError

def create_booking_service(data, db_connections=None):
    
    start = datetime.datetime.fromisoformat(data['startTime'].replace('Z', '+00:00'))
    end = datetime.datetime.fromisoformat(data['endTime'].replace('Z', '+00:00'))
    start = start.replace(tzinfo=None)
    end = end.replace(tzinfo=None)
    
    should_close = False
    if db_connections is None:
        db_connections = get_db_connection()
        should_close = True

    try:
        with db_connections.cursor() as cur:
            cur.execute("SELECT id FROM rooms WHERE id = %s", (data['roomId'],))
            if not cur.fetchone():
                raise KeyError("Unknown room")

            cur.execute("SELECT id FROM rooms WHERE id = %s FOR UPDATE", (data['roomId'],))

            cur.execute("""
                SELECT id FROM bookings
                WHERE room_id = %s
                AND status = 'confirmed'
                AND start_time < %s
                AND end_time > %s
            """, (data['roomId'], end, start))
            
            if cur.fetchone():
                if should_close: db_connections.rollback() 
                raise ConflictError("Overlapping booking")

            cur.execute("""
                INSERT INTO bookings (room_id, title, organizer_email, start_time, end_time)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, room_id, title, organizer_email, start_time, end_time, status
            """, (data['roomId'], data['title'], data['organizerEmail'], start, end))
            
            booking = cur.fetchone()
            if should_close: db_connections.commit()
            return map_booking(booking)
    except Exception as e:
        if should_close: db_connections.rollback()
        raise e
    finally:
        if should_close: db_connections.close()
