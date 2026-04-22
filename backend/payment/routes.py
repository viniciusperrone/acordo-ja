from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from config.rate_limit import limiter

from payment.models import Payment
from payment.schemas import PaymentSchema
from payment.filters import PaymentFilter


payment_bp = Blueprint("payment", __name__, url_prefix="/payment")

@payment_bp.route("/list", methods=["GET"])
@limiter.limit("30 per minute")
@jwt_required()
def list_payment():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = Payment.query

    query = PaymentFilter(query, request.args).apply()

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    payments_schema = PaymentSchema(many=True)

    result = payments_schema.dump(pagination.items)

    return jsonify({
        "items": result,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page
    }), 200

