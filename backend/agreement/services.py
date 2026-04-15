from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta

from agreement import Agreement
from debts import Debt
from installments import Installments
from notifications.events import NotificationEvents
from utils.enum import AgreementStatus, InstallmentStatus, DebtStatus

from .exceptions import (
    DebtNotFountError,
    AgreementStatusError,
    PendingInstallmentsError,
    AgreementNotFoundError,
)


class AgreementService:

    @staticmethod
    def get_agreement_or_fail(agreement_id):
        agreement = Agreement.query.get(agreement_id)
        if not agreement:
            raise AgreementNotFoundError("Agreement not found")
        return agreement

    @staticmethod
    def create_agreement(data, session):
        debt_id = data["debt_id"]

        debt = session.get(Debt, debt_id)

        if not debt:
            raise DebtNotFountError("Debt not found")

        debt_value = Decimal(debt.original_value).quantize(Decimal("0.01"))
        total_to_pay = debt_value

        if debt.due_date and debt.due_date < date.today():
            applied_rate = Decimal(debt.creditor.interest_rate).quantize(
                Decimal("0.01")
            )
            total_to_pay = ((debt_value * (Decimal("1.00") + applied_rate))
                            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

        discount = Decimal(data["discount_applied"]).quantize(Decimal("0.01"))
        entry = Decimal(data["entry_value"]).quantize(Decimal("0.01"))
        installments_quantity = data["installments_quantity"]

        if installments_quantity <= 0:
            raise ValueError("Installments quantity must be greater than zero")

        if discount > total_to_pay:
            raise ValueError("Discount cannot exceed total debt")

        total_to_pay = (total_to_pay - discount).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        if entry > total_to_pay:
            raise ValueError("Entry cannot exceed total after discount")

        remaining_value = (total_to_pay - entry).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        base_installment_value = (
                remaining_value / installments_quantity
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        last_installment_value = (
                remaining_value
                - (base_installment_value * (installments_quantity - 1))
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        agreement = Agreement(
            debt_id=debt_id,
            total_traded=total_to_pay,
            installment_value=base_installment_value,
            installments_quantity=installments_quantity,
            entry_value=entry,
            discount_applied=discount,
            first_due_date=data["first_due_date"],
        )

        session.add(agreement)
        session.flush()

        installments = []
        installment_number = 1
        current_due_date = data["first_due_date"]

        if entry > Decimal("0.00"):
            installments.append(
                Installments(
                    installment_number=installment_number,
                    due_date=current_due_date,
                    value=entry,
                    status=InstallmentStatus.PENDING,
                    agreement_id=agreement.id,
                )
            )

            installment_number += 1
            current_due_date += relativedelta(months=1)

        for i in range(installments_quantity):
            value = (
                last_installment_value
                if i == installments_quantity - 1
                else base_installment_value
            )
            installments.append(
                Installments(
                    installment_number=installment_number,
                    due_date=current_due_date,
                    value=value,
                    status=InstallmentStatus.PENDING,
                    agreement_id=agreement.id,
                )
            )

            installment_number += 1
            current_due_date += relativedelta(months=1)

        session.add_all(installments)
        session.flush()

        NotificationEvents.on_agreement_created(agreement, session)

        return agreement

    @staticmethod
    def open_agreement(agreement: Agreement, session):
        if not agreement.status == AgreementStatus.DRAFT:
            raise AgreementStatusError("Agreement cannot opened")

        debt = agreement.debt

        debt.status = DebtStatus.IN_AGREEMENT
        agreement.status = AgreementStatus.ACTIVE

        session.commit()

        return agreement

    @staticmethod
    def cancel_agreement(agreement: Agreement, session):
        if agreement.status == AgreementStatus.COMPLETED:
            raise AgreementStatusError("Cannot cancel a completed agreement")
        if agreement.status == AgreementStatus.CANCELLED:
            raise AgreementStatusError("Agreement already cancelled")

        agreement.status = AgreementStatus.CANCELLED

        Installments.query.filter_by(
            agreement_id=agreement.agreement_id
        ).update({"status": InstallmentStatus.CANCELLED})

        session.commit()

    @staticmethod
    def complete_agreement(agreement: Agreement, session):
        if agreement.status == AgreementStatus.COMPLETED:
            raise AgreementStatusError("Agreement already completed")
        elif agreement.status == AgreementStatus.CANCELLED:
            raise AgreementStatusError("Agreement is canceled")
        elif agreement.status == AgreementStatus.DRAFT:
            raise AgreementStatusError("Draft agreement cannot be completed")

        pending_installment = Installments.query.filter(
            Installments.agreement_id == agreement.id,
            Installments.status != InstallmentStatus.PAID,
        ).first()

        if pending_installment:
            raise PendingInstallmentsError("There are outstanding installments")

        agreement.status = AgreementStatus.COMPLETED
        session.flush()

        NotificationEvents.on_agreement_completed(agreement, session)
