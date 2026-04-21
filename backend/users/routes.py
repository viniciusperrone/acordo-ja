from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from marshmallow.exceptions import ValidationError

from common.decorators import transactional, current_user
from common.exceptions import UnauthorizedError
from config.rate_limit import limiter

from users.services import UserService
from users.schemas import UserSchema
from users.exceptions import EmailAlreadyExists


user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/add', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
@transactional
@current_user
def create_user(db):
    staff = g.current_user

    user_schema = UserSchema()

    try:
        data = user_schema.load(request.json)

        user = UserService.create_user(data=data, staff=staff, session=db.session)

        return jsonify(user_schema.dump(user)), 201
    except ValidationError as err:
        return jsonify({"message": err.messages}), 400
    except UnauthorizedError as err:
        return jsonify({"message": str(err)}), 401
    except EmailAlreadyExists as err:
        return jsonify({"message": str(err)}), 400
    except Exception as err:
        print(str(err))
        return jsonify({"message": "Internal Server Error"}), 500
