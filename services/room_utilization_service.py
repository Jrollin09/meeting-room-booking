import datetime

from datetime import timedelta
from collections import defaultdict

from helpers.db import get_db_connection

def room_utilization_service(start_date, end_date):
    
    db_connections = get_db_connection()
    try:
        with db_connections.cursor() as cur:
            cur.execute("SELECT * FROM rooms")
            rooms = cur.fetchall()
            
            cur.execute("""
                SELECT * FROM bookings 
                WHERE status = 'confirmed'
                AND end_time > %s
                AND start_time < %s
            """, (start_date, end_date))
            bookings = cur.fetchall()
    finally:
        db_connections.close()
    
    report = []
    
    total_seconds = 0
    curr_date = start_date.date()
    end_day = end_date.date()
    
    while curr_date <= end_day:
        if curr_date.weekday() < 5: 
            w_start = datetime.datetime.combine(curr_date, datetime.datetime.strptime("08:00", "%H:%M").time())
            w_end = datetime.datetime.combine(curr_date, datetime.datetime.strptime("20:00", "%H:%M").time())
            i_start = max(w_start, start_date)
            i_end = min(w_end, end_date)
            if i_start < i_end:
                total_seconds += (i_end - i_start).total_seconds()
        curr_date += timedelta(days=1)
    
    total_biz_hours = total_seconds / 3600.0
    factor = 1.0 / total_biz_hours if total_biz_hours > 0 else 0

    by_room = defaultdict(list)
    for booking in bookings:
        by_room[booking['room_id']].append(booking)

    for room in rooms:
        room_bookings = by_room.get(room['id'], [])
        
        booked_hours = 0.0
        for booking in room_bookings:
            b_start = max(booking['start_time'], start_date)
            b_end = min(booking['end_time'], end_date)
            if b_start < b_end:
                booked_hours += (b_end - b_start).total_seconds() / 3600.0
        
        utilization = booked_hours * factor if total_biz_hours > 0 else 0.0
        report.append({
            "roomId": room['id'],
            "roomName": room['name'],
            "totalBookingHours": round(booked_hours, 2),
            "utilizationPercent": round(utilization, 2)
        })
    return report
