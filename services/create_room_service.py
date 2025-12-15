import psycopg

from helpers.db import get_db_connection

def create_room_service(data):
    
    db_connections = get_db_connection()
    try:
        with db_connections.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO rooms (name, capacity, floor, amenities)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, name, capacity, floor, amenities
                """, (
                    data['name'].strip(),
                    data['capacity'],
                    data.get('floor'),
                    data.get('amenities', [])
                ))
                room = cur.fetchone()
                db_connections.commit()
                return room
            except psycopg.errors.UniqueViolation:
                db_connections.rollback()
                raise ValueError("Room name must be unique")
            except Exception as e:
                db_connections.rollback()
                raise e
    finally:
        db_connections.close()
