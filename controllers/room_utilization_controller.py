import datetime
from flask import request, jsonify, Blueprint
from helpers.errors import make_error
from services.room_utilization_service import room_utilization_service
from helpers.schemas import UTILIZATION_SCHEMA
import jsonschema

bp = Blueprint('room_utilization_controller', __name__)

@bp.route('/reports/room-utilization', methods=['GET'])
def room_utilization():
    try:
        args = {key: value for key, value in request.args.items()}
        jsonschema.validate(instance=args, schema=UTILIZATION_SCHEMA)
    except jsonschema.ValidationError as e:
         path = ".".join([str(p) for p in e.path]) if e.path else "input"
         return make_error(f"Invalid {path}: {e.message}", 400)

    start_str = request.args.get('from')
    end_str = request.args.get('to')
    
    try:
        start_str_fixed = start_str.replace(' ', '+')
        end_str_fixed = end_str.replace(' ', '+')
        start = datetime.datetime.fromisoformat(start_str_fixed.replace('Z', '+00:00'))
        end = datetime.datetime.fromisoformat(end_str_fixed.replace('Z', '+00:00'))
        start = start.replace(tzinfo=None)
        end = end.replace(tzinfo=None)
        
        if start >= end:
            return make_error("Start date must be before end date", 400)

    except ValueError:
         return make_error("Invalid dates", 400)
    
    report = room_utilization_service(start, end)
    return jsonify(report)