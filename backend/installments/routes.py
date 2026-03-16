from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from config.transactional import transactional

from installments import Installments
from installments.filters import InstallmentFilter
from installments.schemas import InstallmentSchema
from installments.services import InstallmentService
from installments.exceptions import InstallmentNotFoundError, InstallmentWithoutAgreementError
from payment.exception import PaymentError
from payment.schemas import PaymentSchema
from payment.services import PaymentService

installment_bp = Blueprint("installments", __name__, url_prefix="/installments")


@installment_bp.route("/list", methods=["GET"])
@jwt_required()
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


@installment_bp.route("/<int:installment_id>/pay", methods=["POST"])
@jwt_required()
@transactional
def pay_installment(installment_id, db):
    payment_schema = PaymentSchema()

    try:
        installment = InstallmentService.get_installment_or_fail(installment_id)

        data = payment_schema.load(request.json)

        PaymentService.register_payment(
            installment=installment,
            amount=data['amount'],
            method=data['method'],
            session=db.session
        )

        return jsonify({"message": "Installment paid successfully"}), 200

    except ValidationError as err:
        return jsonify({'message': err.messages}), 400

    except InstallmentNotFoundError as err:
        return jsonify({"message": str(err)}), 404

    except (InstallmentWithoutAgreementError, PaymentError) as err:
        return jsonify({"message": str(err)}), 400

    except Exception as err:
        db.session.rollback()
        print(str(err))
        return jsonify({'message': "Internal Server Error"}), 500
