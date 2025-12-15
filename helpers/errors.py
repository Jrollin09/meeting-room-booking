from flask import jsonify

class ConflictError(Exception):
    pass

def make_error(msg, code=400, error_type="ValidationError"):
    return jsonify({"error": error_type, "message": msg}), code

def register_error_handlers(app):
    @app.errorhandler(ValueError)
    def handle_value_error(e):
        return make_error(str(e), 400, "ValidationError")

    @app.errorhandler(KeyError)
    def handle_key_error(e):
        return make_error(str(e), 404, "NotFoundError")

    @app.errorhandler(ConflictError)
    def handle_conflict_error(e):
        return make_error(str(e), 409, "ConflictError")

