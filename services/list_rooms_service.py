from helpers.db import get_db_connection

def list_rooms_service(min_capacity=None, amenities=None):
    db_connections = get_db_connection()
    try:
        query = "SELECT * FROM rooms WHERE TRUE"
        params = []
        if min_capacity:
            query += " AND capacity >= %s"
            params.append(min_capacity)
        if amenities:
            query += " AND amenities @> %s"
            params.append(amenities)
        
        with db_connections.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        db_connections.close()
