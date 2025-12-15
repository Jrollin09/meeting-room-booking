def map_booking(row):
    return {
        'id': row['id'],
        'roomId': row['room_id'],
        'title': row['title'],
        'organizerEmail': row['organizer_email'],
        'startTime': row['start_time'].isoformat(),
        'endTime': row['end_time'].isoformat(),
        'status': row['status']
    }
