import json
from helpers.db import get_db_connection
from services.create_booking_service import create_booking_service
from helpers.errors import ConflictError

def idempotency_check_service(data, idem_key=None, organizer=None):
    db_connections = get_db_connection()
    try:
        response_data = None
        status_code = 201
        
        if idem_key and organizer:
            with db_connections.cursor() as cur:
                cur.execute("""
                    INSERT INTO idempotency_keys (key, organizer_email) 
                    VALUES (%s, %s) 
                    ON CONFLICT (key, organizer_email) DO NOTHING
                """, (idem_key, organizer))
                
                cur.execute("""
                    SELECT * FROM idempotency_keys 
                    WHERE key = %s AND organizer_email = %s 
                """, (idem_key, organizer))
                record = cur.fetchone()
                
                if record and record['response_body']:
                    db_connections.commit()
                    return json.loads(record['response_body']), record['response_status']
                
                pass

        try:
             with db_connections.transaction():
                 booking = create_booking_service(data, db_connections=db_connections)
                 response_data = booking
                 status_code = 201
        except Exception as e:
             if isinstance(e, ValueError):
                 response_data = {"error": "ValidationError", "message": str(e)}
                 status_code = 400
             elif isinstance(e, KeyError):
                 response_data = {"error": "NotFoundError", "message": str(e)}
                 status_code = 404
             elif isinstance(e, ConflictError):
                 response_data = {"error": "ConflictError", "message": str(e)}
                 status_code = 409
             else:
                 response_data = {"error": "InternalServerError", "message": str(e)}
                 status_code = 500
            
        if idem_key and organizer:
             with db_connections.cursor() as cur:
                 cur.execute("""
                    UPDATE idempotency_keys 
                    SET response_status = %s, response_body = %s
                    WHERE key = %s AND organizer_email = %s
                 """, (status_code, json.dumps(response_data), idem_key, organizer))
        
        db_connections.commit()
        return response_data, status_code

    except Exception as e:
         db_connections.rollback()
         raise e
    finally:
        db_connections.close()
