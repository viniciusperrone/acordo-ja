from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config.db import db
from installments import Installments
from installments.filters import InstallmentFilter
from installments.schemas import InstallmentSchema

installment_bp = Blueprint("installments", __name__, url_prefix="/installments")


@installment_bp.route("/list", methods=["GET"])
def list_installments():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        query = Installments.query

        query = InstallmentFilter(query, request.args).apply()

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        installments_schema = InstallmentSchema(many=True)

        result = installments_schema.dump(pagination.items)

        return jsonify({
            "items": result,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page
        }), 200

    except Exception as err:
        print(str(err))
        return jsonify({'message': "Internal Server Error"}), 500


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