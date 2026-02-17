from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config.db import db

from creditor.schemas import CreditorSchema
from creditor.models import Creditor


creditor_bp = Blueprint('creditor', __name__, url_prefix='/creditors')

@creditor_bp.route('/add', methods=['POST'])
def create_creditor():
    creditor_schema = CreditorSchema()

    try:
        data = creditor_schema.load(request.json)

        bank_code = data['bank_code']

        existing_creditor = Creditor.query.filter_by(bank_code=bank_code).first()

        if existing_creditor:
            return jsonify({'message': 'Creditor already exists'}), 400

        creditor = Creditor(**data)

        db.session.add(creditor)
        db.session.commit()

        return jsonify({'message': 'Successfully registered creditor'})

    except ValidationError as err:
        return jsonify({'message': err.messages}), 400

    except Exception as err:

        return jsonify({'message': "Internal Server Error"}), 500
