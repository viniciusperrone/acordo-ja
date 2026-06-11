from flask import request, jsonify, Flask
from werkzeug.exceptions import HTTPException
from marshmallow.exceptions import ValidationError

from common.exceptions import AppException
from observability.structured_logger import get_logger


logger = get_logger("api.error_handlers")


def register_error_handlers(app: Flask):

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify({"message": err.messages if err.messages else str(err)}), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        status_code = err.code if err.code else 500
        message = getattr(err, 'description', str(err))

        return jsonify({"message": message}), status_code

    @app.errorhandler(AppException)
    def handle_app_exception(err):
        return jsonify({"message": err.message}), err.status_code

    @app.errorhandler(Exception)
    def handle_generic_exception(err):
        logger.exception(
            "api.unhandled_exception",
            extra={
                "extra_fields": {
                    "event": "api.unhandled_exception",
                    "error": str(err),
                    "method": request.method,
                    "path": request.path,
                    "endpoint": request.endpoint
                }
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500
