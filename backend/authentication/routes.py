from flask import Blueprint

from config.transactional import transactional

authentication_bp = Blueprint("authentication", __name__, url_prefix="/authentication")

@authentication_bp.route("/login", methods=["POST"])
@transactional
def login(db):
    ...