from flask import request , jsonify, Blueprint
from services.list_bookings_service import list_bookings_service
from helpers.schemas import LIST_BOOKINGS_SCHEMA
from helpers.errors import make_error
import jsonschema

bp = Blueprint('list_bookings_controller', __name__)

@bp.route('/bookings', methods=['GET'])
def list_bookings():
    try:
        args = {key: value for key, value in request.args.items()}
        for field in ['roomId', 'limit', 'offset']:
            if field in args:
                try:
                    args[field] = int(args[field])
                except ValueError:
                    return make_error(f"Invalid {field}", 400)
        
        jsonschema.validate(instance=args, schema=LIST_BOOKINGS_SCHEMA)
    except jsonschema.ValidationError as e:
        path = ".".join([str(p) for p in e.path]) if e.path else "input"
        return make_error(f"Invalid {path}: {e.message}", 400)

    room_id = args.get('roomId')
    start = args.get('from')
    end = args.get('to')
    limit = args.get('limit', 10)
    offset = args.get('offset', 0)
    
    try:
        items, total = list_bookings_service(room_id, start, end, limit, offset)
        return jsonify({"items": items, "total": total, "limit": limit, "offset": offset})
    except ValueError as e:
        return make_error(str(e), 400)
