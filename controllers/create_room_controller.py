from flask import request, jsonify,Blueprint
from helpers.errors import make_error
from services.create_room_service import create_room_service
from helpers.schemas import ROOM_SCHEMA
import jsonschema

bp = Blueprint('create_room_controller', __name__)
@bp.route('/rooms', methods=['POST'])
def create_room():
    data = request.get_json()
    try:
        jsonschema.validate(instance=data, schema=ROOM_SCHEMA)
    except jsonschema.ValidationError as e:
        path = ".".join([str(p) for p in e.path]) if e.path else "root"
        return make_error(f"Invalid input for field '{path}': {e.message}", 400)

    try:
        room = create_room_service(data)
        return jsonify({
            'id': room['id'],
            'name': room['name'],
            'capacity': room['capacity'],
            'floor': room['floor'],
            'amenities': room['amenities']
        }), 201
    except ValueError as e:
        return make_error(str(e), 400)