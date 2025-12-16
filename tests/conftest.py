import pytest
import os
import psycopg
from flask import Flask
from dotenv import load_dotenv
load_dotenv()
from psycopg.rows import dict_row
from app import app as flask_app
from helpers.db import init_db

class TestConfig:
    DATABASE_URL = os.getenv('TEST_DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/test_meeting')

@pytest.fixture(scope='session')
def app():
    flask_app.config['TESTING'] = True
    
    from app import Config
    old_url = Config.DATABASE_URL
    Config.DATABASE_URL = TestConfig.DATABASE_URL
    
    init_db()
    
    yield flask_app
    
    Config.DATABASE_URL = old_url

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def clean_tables():
    conn = psycopg.connect(TestConfig.DATABASE_URL)
    try:
        with conn.cursor() as cur:
             cur.execute("TRUNCATE TABLE bookings, rooms, idempotency_keys RESTART IDENTITY CASCADE;")
        conn.commit()
    finally:
        conn.close()
