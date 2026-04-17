from flask import jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://redis:6379",
    default_limits=["100 per hour"]
)

def rate_limit_handler(e):
    return jsonify({
        "message": "Too many requests",
        "details": str(e.description),
    }), 429
