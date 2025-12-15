import pytest
from datetime import datetime, timedelta, timezone
from helpers.schemas import LIST_ROOMS_SCHEMA


def test_create_room_success(client):
    res = client.post('/rooms', json={
        "name": "Room A",
        "capacity": 10,
        "floor": 1,
        "amenities": ["Projector"]
    })
    assert res.status_code == 201
    assert res.json['id'] is not None

def test_create_room_invalid(client):
    res = client.post('/rooms', json={"name": "Room B"})
    assert res.status_code == 400
    res = client.post('/rooms', json={"name": "Room C", "capacity": 0})
    assert res.status_code == 400

    client.post('/rooms', json={"name": "UniqueRoom", "capacity": 5})
    res = client.post('/rooms', json={"name": "UniqueRoom", "capacity": 10})
    assert res.status_code == 400
    assert "must be unique" in res.json['message']
    
    res = client.post('/rooms', json={"name": "uniqueroom", "capacity": 10})
    assert res.status_code == 400
    assert "must be unique" in res.json['message']


def test_list_rooms_filter(client):
    client.post('/rooms', json={"name": "Small", "capacity": 2})
    client.post('/rooms', json={"name": "TV Room", "capacity": 10, "amenities": ["TV"]})
    
    assert len(client.get('/rooms?minCapacity=5').json) == 1
    assert len(client.get('/rooms?amenities=TV').json) == 1
    assert len(client.get('/rooms?amenity=TV').json) == 1

def test_list_rooms_invalid_filter(client):
    assert client.get('/rooms?minCapacity=abc').status_code == 400
    assert client.get('/rooms?amenities=').status_code == 400


def test_create_booking_success(client):
    client.post('/rooms', json={"name": "B1", "capacity": 5})
    rid = client.get('/rooms').json[0]['id']
    
    today = datetime.now(timezone.utc)
    start = (today + timedelta(days=(7 - today.weekday()))).replace(hour=10, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)
    
    res = client.post('/bookings', json={
        "roomId": rid, "title": "Meeting", "organizerEmail": "test@test.com",
        "startTime": start.isoformat(), "endTime": end.isoformat()
    })
    assert res.status_code == 201

def test_create_booking_invalid_date(client):
    client.post('/rooms', json={"name": "B2", "capacity": 5})
    rid = client.get('/rooms').json[-1]['id']
    
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    res = client.post('/bookings', json={
        "roomId": rid, "title": "Past", "organizerEmail": "test@test.com",
        "startTime": past, "endTime": past
    })
    assert res.status_code == 400
    
    future = datetime.now(timezone.utc) + timedelta(days=30)
    res = client.post('/bookings', json={
        "roomId": rid, "title": "Inverted", "organizerEmail": "test@test.com",
        "startTime": (future + timedelta(hours=1)).isoformat(), 
        "endTime": future.isoformat()
    })
    assert res.status_code == 400

def test_create_booking_invalid_schema(client):
    res = client.post('/bookings', json={"title": "No Room"})
    assert res.status_code == 400
    res = client.post('/bookings', json={"roomId": 1, "organizerEmail": "invalid-email"})
    assert res.status_code == 400

def test_create_booking_conflict(client):
    client.post('/rooms', json={"name": "Conflict", "capacity": 5})
    rid = client.get('/rooms').json[-1]['id']
    
    today = datetime.now(timezone.utc)
    start = (today + timedelta(days=(7 - today.weekday()))).replace(hour=12, minute=0, second=0, microsecond=0)
    
    payload = {
        "roomId": rid, "title": "M1", "organizerEmail": "t@t.com",
        "startTime": start.isoformat(), "endTime": (start + timedelta(hours=1)).isoformat()
    }
    client.post('/bookings', json=payload)
    res = client.post('/bookings', json=payload)
    assert res.status_code == 409

def test_create_booking_business_hours(client):
    client.post('/rooms', json={"name": "Biz", "capacity": 5})
    rid = client.get('/rooms').json[-1]['id']
    
    today = datetime.now(timezone.utc)
    sunday = (today + timedelta(days=(6 - today.weekday()))).replace(hour=10, minute=0, second=0, microsecond=0)
    res = client.post('/bookings', json={
        "roomId": rid, "title": "Wknd", "organizerEmail": "t@t.com",
        "startTime": sunday.isoformat(), "endTime": (sunday + timedelta(hours=1)).isoformat()
    })
    assert res.status_code == 400


def test_list_bookings_validation(client):
    assert client.get('/bookings?limit=abc').status_code == 400
    assert client.get('/bookings?offset=-1').status_code == 400


def test_idempotency(client):
    client.post('/rooms', json={"name": "Idem", "capacity": 5})
    rid = client.get('/rooms').json[-1]['id']
    
    today = datetime.now(timezone.utc)
    start = (today + timedelta(days=(7 - today.weekday()))).replace(hour=14, minute=0, second=0, microsecond=0)
    
    payload = {
        "roomId": rid, "title": "I", "organizerEmail": "i@i.com",
        "startTime": start.isoformat(), "endTime": (start + timedelta(hours=1)).isoformat()
    }
    headers = {'Idempotency-Key': 'key1'}
    
    res1 = client.post('/bookings', json=payload, headers=headers)
    assert res1.status_code == 201
    
    res2 = client.post('/bookings', json=payload, headers=headers)
    assert res2.status_code == 201
    assert res2.json['id'] == res1.json['id']


def test_cancel_booking_success(client):
    client.post('/rooms', json={"name": "C", "capacity": 5})
    rid = client.get('/rooms').json[-1]['id']
    
    start = (datetime.now(timezone.utc) + timedelta(days=2)).replace(hour=10, minute=0)
    res = client.post('/bookings', json={
        "roomId": rid, "title": "C", "organizerEmail": "c@c.com",
        "startTime": start.isoformat(), "endTime": (start + timedelta(hours=1)).isoformat()
    })
    bid = res.json['id']
    
    assert client.post(f'/bookings/{bid}/cancel').status_code == 200

def test_cancel_booking_invalid(client):
    assert client.post('/bookings/abc/cancel').status_code == 404
    assert client.post('/bookings/0/cancel').status_code == 400
    assert client.post('/bookings/99999/cancel').status_code == 404



def test_room_utilization_success(client):
    client.post('/rooms', json={"name": "U", "capacity": 5})
    rid = client.get('/rooms').json[-1]['id']
    
    today = datetime.now(timezone.utc)
    d = today + timedelta(days=(7 - today.weekday()))
    client.post('/bookings', json={
        "roomId": rid, "title": "U", "organizerEmail": "u@u.com",
        "startTime": d.replace(hour=9, minute=0).isoformat(), 
        "endTime": d.replace(hour=11, minute=0).isoformat()
    })
    
    res = client.get(f'/reports/room-utilization?from={d.replace(hour=8).isoformat()}&to={d.replace(hour=12).isoformat()}')
    assert res.status_code == 200
    item = [x for x in res.json if x['roomId'] == rid][0]
    assert item['totalBookingHours'] == 2.0

def test_room_utilization_invalid(client):
    assert client.get('/reports/room-utilization').status_code == 400
    
    d = datetime.now(timezone.utc)
    res = client.get(f'/reports/room-utilization?from={d.isoformat()}&to={(d - timedelta(days=1)).isoformat()}')
    assert res.status_code == 400
