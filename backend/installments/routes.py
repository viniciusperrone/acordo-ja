from flask import Blueprint, request, jsonify

from config.db import db
from installments import Installments
from installments.filters import InstallmentFilter
from installments.schemas import InstallmentSchema
from installments.services import InstallmentService
from installments.exceptions import InstallmentNotFoundError, InstallmentError, InstallmentWithoutAgreementError


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


@installment_bp.route("/<int:installment_id>/pay", methods=["POST"])
def pay_installment(installment_id):
    try:
        installment = InstallmentService.get_installment_or_fail(installment_id)

        InstallmentService.pay_installment(installment, db.session)

        return jsonify({"message": "Installment paid"}), 200

    except InstallmentNotFoundError as err:
        return jsonify({"message": str(err)}), 404

    except (InstallmentWithoutAgreementError, InstallmentError) as err:
        return jsonify({"message": str(err)}), 400

    except Exception as err:
        db.session.rollback()
        print(str(err))
        return jsonify({'message': "Internal Server Error"}), 500
