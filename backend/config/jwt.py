from flask import Flask
from flask_jwt_extended import JWTManager

from authentication.models import TokenBlocklist
from common.decorators import transactional


def init_jwt(app: Flask):
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    @transactional
    def check_if_token_revoked(jwt_header, jwt_payload, db):
        jti = jwt_payload['jti']

        token = db.session.query(TokenBlocklist).filter_by(jti=jti).first()

        return token is not None

    @jwt.expired_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {"message": "Token has been revoked"}, 401

    return jwt
