import os
import psycopg
from psycopg.rows import dict_row

class Config:
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/meeting_room')
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'

def get_db_connection():
    
    db_connections = psycopg.connect(Config.DATABASE_URL, row_factory=dict_row)
    return db_connections

def init_db():
    db_connections = get_db_connection()
    try:
        with db_connections.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    capacity INTEGER NOT NULL CHECK (capacity >= 1),
                    floor INTEGER,
                    amenities TEXT[]
                );
            """)
            cur.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS uq_room_name ON rooms (lower(name));
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id SERIAL PRIMARY KEY,
                    room_id INTEGER NOT NULL REFERENCES rooms(id),
                    title VARCHAR NOT NULL,
                    organizer_email VARCHAR NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    status VARCHAR DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'cancelled')),
                    CONSTRAINT check_start_before_end CHECK (start_time < end_time)
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS idempotency_keys (
                    key VARCHAR,
                    organizer_email VARCHAR,
                    response_status INTEGER,
                    response_body TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (key, organizer_email)
                );
            """)
            db_connections.commit()
    finally:
        db_connections.close()
