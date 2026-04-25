from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt

from authentication.schemas import AuthenticationSchema, UpdatePasswordSchema, ForgotPasswordSchema,  ResetPasswordSchema
from authentication.services import AuthenticationService
from common.decorators import current_user, transactional
from config import limiter


authentication_bp = Blueprint("authentication", __name__, url_prefix="/auth")

@authentication_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
@transactional
def login(db):
    authentication_schema = AuthenticationSchema()

    data = authentication_schema.load(request.get_json())

    tokens = AuthenticationService.login(email=data["email"], password=data["password"], session=db.session)

    return jsonify(tokens), 200

@authentication_bp.route("/me/update-password", methods=["PATCH"])
@jwt_required()
@limiter.limit("1 per minute")
@transactional
@current_user
def update_password(db):
    user = getattr(g, "current_user")
    schema = UpdatePasswordSchema()
    data = schema.load(request.json)

    AuthenticationService.update_password(
        user=user,
        data=data,
        session=db.session
    )

    return jsonify({"message": "Password changed successfully"}), 200

@authentication_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("1 per minute")
@transactional
def forgot_password(db):
    schema = ForgotPasswordSchema()
    data = schema.load(request.json)

    AuthenticationService.forgot_password(data=data, session=db.session)

    return jsonify({"message": "The link to reset your password has been sent to your email"})

@authentication_bp.route("/logout", methods=["POST"])
@jwt_required()
@limiter.limit("5 per minute")
@transactional
def logout(db):
    jti = get_jwt()["jti"]

    AuthenticationService.logout(jti=jti, session=db.session)

    return jsonify({"message": "Successfully logged out"}), 200

@authentication_bp.route("/<string:url_safe>/reset-password", methods=["PUT"])
@limiter.limit("1 per minute")
@transactional
def reset_password(url_safe, db):
    schema = ResetPasswordSchema()
    data = schema.load(request.json)

    AuthenticationService.reset_password(
        url_safe=url_safe,
        data=data,
        session=db.session
    )

    return jsonify({"message": "Password reset requested"}), 200
