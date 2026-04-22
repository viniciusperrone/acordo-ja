from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from common.decorators import transactional
from config.rate_limit import limiter

from installments.models import Installments
from installments.filters import InstallmentFilter
from installments.schemas import InstallmentSchema
from installments.services import InstallmentService

from payment.schemas import PaymentSchema
from payment.services import PaymentService


installment_bp = Blueprint("installments", __name__, url_prefix="/installments")

@installment_bp.route("/list", methods=["GET"])
@limiter.limit("30 per minute")
@jwt_required()
def list_installments():
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

@installment_bp.route("/<int:installment_id>/pay", methods=["POST"])
@jwt_required()
@limiter.limit("3 per minute")
@transactional
def pay_installment(installment_id, db):
    payment_schema = PaymentSchema()

    installment = InstallmentService.get(installment_id, db.session)
    data = payment_schema.load(request.json)

    payment = PaymentService.process_installment_payment(
        installment=installment,
        amount=data['amount'],
        method=data['method'],
        session=db.session
    )

    result = payment_schema.dump(payment)

    return jsonify(result), 201
