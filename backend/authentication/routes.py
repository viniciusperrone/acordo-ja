from flask import Blueprint, request, jsonify

from authentication.schemas import AuthenticationSchema
from authentication.services import AuthenticationService
from config.rate_limit import limiter
from common.decorators.transactional import transactional


authentication_bp = Blueprint("authentication", __name__, url_prefix="/authentication")

@authentication_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
@transactional
def login(db):
    authentication_schema = AuthenticationSchema()

    data = authentication_schema.load(request.get_json())

    tokens = AuthenticationService.login(email=data["email"], password=data["password"], session=db.session)

    return jsonify(tokens), 200
