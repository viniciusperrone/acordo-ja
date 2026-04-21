from flask import jsonify, Flask
from marshmallow.exceptions import ValidationError

from common.exceptions import AppException


def register_error_handlers(app: Flask):

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify({"message": err.message}), 400

    @app.errorhandler(AppException)
    def handle_app_exception(err):
        return jsonify({"message": err.message}), err.status_code

    @app.errorhandler(Exception)
    def handle_generic_exception(err):
        print(str(err))
        return jsonify({"message": "Internal Server Error"}), 500
