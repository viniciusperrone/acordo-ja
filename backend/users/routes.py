from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from common.decorators import transactional
from config.rate_limit import limiter

from users.services import UserService
from users.schemas import UserSchema


user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/add', methods=['POST'])
@limiter.limit("10 per minute")
@transactional
def create_user(db):
    user_schema = UserSchema()

    try:
        data = user_schema.load(request.json)

        user = UserService.create_user(data=data, session=db.session)

        return jsonify(user_schema.dump(user)), 201
    except ValidationError as err:
        return jsonify({"message": err.messages}), 400
    except Exception as err:
        print(str(err))
        return jsonify({"message": "Internal Server Error"}), 500
