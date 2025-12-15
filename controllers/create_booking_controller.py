from flask import request, jsonify, Blueprint
from services.idempotency_check_service import idempotency_check_service
from helpers.schemas import BOOKING_SCHEMA
from helpers.errors import make_error
import jsonschema
import datetime
from datetime import timedelta

bp = Blueprint('create_booking_controller', __name__)
@bp.route('/bookings', methods=['POST'])
def create_booking():
    data = request.get_json()
    idem_key = request.headers.get('Idempotency-Key')
    organizer = data.get('organizerEmail')
    
    try:
        jsonschema.validate(instance=data, schema=BOOKING_SCHEMA)
    except jsonschema.ValidationError as e:
        path = ".".join([str(p) for p in e.path]) if e.path else "root"
        return make_error(f"Invalid input for field '{path}': {e.message}", 400)

    try:
        start = datetime.datetime.fromisoformat(data['startTime'].replace('Z', '+00:00'))
        end = datetime.datetime.fromisoformat(data['endTime'].replace('Z', '+00:00'))
        start = start.replace(tzinfo=None)
        end = end.replace(tzinfo=None)
        
        if start < datetime.datetime.now():
            return make_error("Booking cannot be in the past", 400)

        if start.date() != end.date():
             return make_error("Booking must start and end on the same day", 400)

        if start >= end:
             return make_error("startTime must be before endTime", 400)
        
        duration = end - start
        if duration < timedelta(minutes=15) or duration > timedelta(hours=4):
             return make_error("Booking duration must be between 15 minutes and 4 hours", 400)
        
        if start.weekday() >= 5:
             return make_error("Bookings only allowed Mon-Fri", 400)
        
        if start.time() < datetime.datetime.strptime("08:00", "%H:%M").time() or \
           end.time() > datetime.datetime.strptime("20:00", "%H:%M").time():
               return make_error("Bookings only allowed 08:00-20:00", 400)

    except ValueError as e:
         return make_error("Invalid date format. Use ISO-8601", 400)

    response_data, status_code = idempotency_check_service(data, idem_key, organizer)
    return jsonify(response_data), status_code