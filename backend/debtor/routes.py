from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config.db import db
from debtor.models import Debtor
from debtor.schemas import DebtorSchema


debtor_bp = Blueprint('debtor', __name__, url_prefix='/debtor')

@debtor_bp.route('/add', methods=['POST'])
def create_debtor():
    debtor_schema = DebtorSchema()

    try:
        data = debtor_schema.load(request.json)

        debt = Debtor(**data)

        db.session.add(debt)
        db.session.commit()

        return jsonify({"message": "Successfully registered debtor"}), 201

    except ValidationError as err:
        return jsonify({"message": err.messages}), 400

    except Exception as err:
        return jsonify({"message": "Internal Server Error"}), 500

