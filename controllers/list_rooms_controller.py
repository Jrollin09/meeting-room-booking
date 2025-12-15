from flask import request, jsonify, Blueprint
from services.list_rooms_service import list_rooms_service
from helpers.schemas import LIST_ROOMS_SCHEMA
from helpers.errors import make_error
import jsonschema


bp = Blueprint('list_rooms_controller', __name__)
@bp.route('/rooms', methods=['GET'])
def list_rooms():
    try:
        args = {}
        min_capacity_raw = request.args.get('minCapacity')
        if min_capacity_raw is not None:
             try:
                 args['minCapacity'] = int(min_capacity_raw)
             except ValueError:
                 return make_error("Invalid minCapacity", 400)

        amenities = request.args.getlist('amenities')
        amenities.extend(request.args.getlist('amenity'))
            
        if amenities:
            args['amenities'] = amenities

        jsonschema.validate(instance=args, schema=LIST_ROOMS_SCHEMA)
    except jsonschema.ValidationError as e:
         path = ".".join([str(p) for p in e.path]) if e.path else "input"
         return make_error(f"Invalid {path}: {e.message}", 400)

    min_cap = args.get('minCapacity')
    amenities = args.get('amenities')
    rooms = list_rooms_service(min_cap, amenities)
    return jsonify([{
        'id': r['id'],
        'name': r['name'],
        'capacity': r['capacity'],
        'floor': r['floor'],
        'amenities': r['amenities']
    } for r in rooms])