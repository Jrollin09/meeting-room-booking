from flask import jsonify,Blueprint
from services.cancel_booking_service import cancel_booking_service
from helpers.errors import make_error

bp= Blueprint('cancel_booking_controller', __name__)

@bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    if booking_id < 1:
        return make_error("Invalid booking ID", 400)
    
    try:
        booking = cancel_booking_service(booking_id)
        return jsonify(booking)
    except KeyError as e:
        return make_error(str(e), 404)
    except ValueError as e:
        return make_error(str(e), 400)