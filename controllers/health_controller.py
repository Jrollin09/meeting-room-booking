from flask import Blueprint

bp = Blueprint('health_controller', __name__)

@bp.route('/health')
def health():
    return {'status': 'ok'}