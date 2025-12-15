from flask import Flask
from helpers.errors import register_error_handlers
from helpers.db import init_db, Config

app = Flask(__name__)

register_error_handlers(app)

from controllers.list_bookings_controller import bp as list_bookings_controller
from controllers.create_room_controller import bp as create_room_controller
from controllers.list_rooms_controller import bp as list_rooms_controller
from controllers.create_booking_controller import bp as create_booking_controller
from controllers.cancel_booking_controller import bp as cancel_booking_controller           
from controllers.room_utilization_controller import bp as room_utilization_controller
from controllers.health_controller import bp as health_controller

app.register_blueprint(list_bookings_controller)
app.register_blueprint(create_room_controller)
app.register_blueprint(list_rooms_controller)       
app.register_blueprint(create_booking_controller)
app.register_blueprint(cancel_booking_controller)
app.register_blueprint(room_utilization_controller)
app.register_blueprint(health_controller)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
