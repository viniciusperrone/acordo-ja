from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config.db import db
from installments import Installments
from installments.schemas import InstallmentSchema

installment_bp = Blueprint("installments", __name__, url_prefix="/installments")

@installment_bp.route("/add", methods=["POST"])
def create_installment():
    installment_schema = InstallmentSchema()

    try:
        data = installment_schema.load(request.json)

        installment = Installments(**data)

        db.session.add(installment)
        db.session.commit()

        return jsonify({'message': 'Successfully registered installment'})

    except ValidationError as err:
        return jsonify({'message': err.messages})
    except Exception as err:
        return jsonify({'message': 'Internal Server Error'})