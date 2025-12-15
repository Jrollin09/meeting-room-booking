import datetime

from helpers.db import get_db_connection
from helpers.map_booking import map_booking

def list_bookings_service(room_id=None, start=None, end=None, limit=10, offset=0):
    start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00')) if start else None
    end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00')) if end else None
    
    db_connections = get_db_connection()
    try:
        query = "SELECT * FROM bookings WHERE TRUE"
        params = []
        
        if room_id:
            query += " AND room_id = %s"
            params.append(room_id)
        if start_dt:
            query += " AND end_time > %s"
            params.append(start_dt)
        if end_dt:
            query += " AND start_time < %s"
            params.append(end_dt)
            
        count_query = f"SELECT COUNT(*) as count FROM ({query}) as sub"
        with db_connections.cursor() as cur:
            cur.execute(count_query, params)
            total = cur.fetchone()['count']
            
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            cur.execute(query, params)
            items = cur.fetchall()
            
            return [map_booking(b) for b in items], total
    finally:
        db_connections.close()
