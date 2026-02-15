from decimal import Decimal, ROUND_HALF_UP

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from agreement import Agreement
from agreement.schema import AgreementSchema
from installments import Installments
from debts import Debt

from dateutil.relativedelta import relativedelta

from config.db import db
from utils.enum import AgreementStatus, InstallmentStatus

agreement_bp = Blueprint('agreement', __name__, url_prefix='/agreement')

@agreement_bp.route('/add', methods=['POST'])
def create_agreement():
    agreement_schema = AgreementSchema()

    try:
        data = agreement_schema.load(request.json)

        debt_id = data['debt_id']

        debt = Debt.query.get(debt_id)
        if not debt:
            return jsonify({"message": "Debt not found"}), 404

        debt_value = Decimal(debt.original_value).quantize(Decimal('0.01'))

        discount = data['discount_applied']
        entry = data['entry_value']
        installments_quantity = data['installments_quantity']

        total_to_pay = (debt_value - discount).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        remaining_value = (total_to_pay - entry).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        installment_value = (remaining_value / installments_quantity).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        agreement = Agreement(
            debt_id=data["debt_id"],
            total_traded=debt_value,
            installment_value=installment_value,
            installments_quantity=installments_quantity,
            entry_value=entry,
            discount_applied=discount,
            first_due_date=data["first_due_date"],
        )

        db.session.add(agreement)
        db.session.flush()

        installments = []

        installment_number = 1
        current_due_date = data["first_due_date"]

        if entry > Decimal("0.00"):
            entry_installment = Installments(
                installment_number=installment_number,
                due_date=current_due_date,
                value=entry,
                status="PENDING",
                agreement_id=agreement.id,
            )
            installments.append(entry_installment)

            installment_number += 1
            current_due_date += relativedelta(months=1)

        for _ in range(installments_quantity):
            installment = Installments(
                installment_number=installment_number,
                due_date=current_due_date,
                value=installment_value,
                status="PENDING",
                agreement_id=agreement.id,
            )

            installments.append(installment)

            installment_number += 1
            current_due_date = current_due_date + relativedelta(months=1)

        db.session.add_all(installments)
        db.session.commit()

        return jsonify({"message": "Successfully registered agreement"}), 201

    except ValidationError as err:
        db.session.rollback()
        return jsonify({"message": err.messages}), 400

    except Exception as err:
        print(str(err))

        db.session.rollback()
        return jsonify({"message": "Internal Server Error"}), 500


@agreement_bp.route('/<uuid:agreement_id>', methods=['POST'])
def cancel_agreement(agreement_id):
    try:
        agreement = Agreement.query.get(agreement_id)

        if not agreement:
            return jsonify({"message": "Agreement not found"}), 404

        if agreement.status == AgreementStatus.COMPLETED:
            return jsonify({"message": "Cannot cancel a completed agreement"}), 400

        if agreement.status == AgreementStatus.CANCELLED:
            return jsonify({"message": "Agreement already cancelled"}), 400

        agreement.status = AgreementStatus.CANCELLED

        Installments.query.filter_by(
            agreement_id=agreement.id,
            status=InstallmentStatus.PENDING
        ).update({"status": InstallmentStatus.CANCELLED})

        db.session.commit()

        return jsonify({"message": "Agreement successfully cancelled"}), 201

    except Exception as err:
        db.session.rollback()

        return jsonify({"message": "Internal Server Error"}), 500

@agreement_bp.route('/<uuid:agreement_id>/complete', methods=['POST'])
def complete_agreement(agreement_id):
    try:
        agreement = Agreement.query.get(agreement_id)

        if not agreement:
            return jsonify({"message": "Agreement not found"}), 404

        if agreement.status == AgreementStatus.COMPLETED:
            return jsonify({"message": "Agreement already completed"}), 400

        if agreement.status == AgreementStatus.CANCELLED:
            return jsonify({"message": "Agreement is canceled"}), 400

        if agreement.status == AgreementStatus.DRAFT:
            return jsonify({
                "message": "Draft agreement cannot be completed"
            }), 400

        pending_installment = Installments.query.filter(
            Installments.agreement_id == agreement.id,
            Installments.status != "PAID"
        ).first()

        if pending_installment:
            return jsonify({"message": "There are outstanding installments"}), 400

        agreement.status = AgreementStatus.COMPLETED

        db.session.commit()

        return jsonify({
            "message": "Agreement successfully completed"
        }), 200

    except Exception as err:
        db.session.rollback()

        return jsonify({"message": "Internal Server Error"}), 500
