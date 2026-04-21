from sqlalchemy import exists

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta

from agreement import Agreement
from users.models import User
from debts import Debt
from debts.history_service import DebtHistoryService
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

        # Aplica multa uma vez se a dívida estiver vencida
        if debt.due_date and debt.due_date < date.today():
            fine_rate = Decimal(debt.creditor.fine_rate).quantize(Decimal("0.0001"))
            total_to_pay = (debt_value * (Decimal("1") + fine_rate / Decimal("100"))
                            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Validação e aplicação do desconto
        discount = Decimal(data.get("discount_applied", "0.00")).quantize(Decimal("0.01"))
        discount_limit = Decimal(debt.creditor.discount_limit).quantize(Decimal("0.0001"))
        max_discount = (total_to_pay * discount_limit / Decimal("100")
                        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if discount > max_discount:
            raise ValueError(f"Discount cannot exceed {discount_limit}% of total (max: {max_discount})")
        if discount > total_to_pay:
            raise ValueError("Discount cannot exceed total debt")

        total_to_pay = (total_to_pay - discount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Validação e aplicação da entrada
        entry = Decimal(data.get("entry_value", "0.00")).quantize(Decimal("0.01"))
        if entry > total_to_pay:
            raise ValueError("Entry cannot exceed total after discount")

        remaining_value = (total_to_pay - entry).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Validação de parcelas
        installments_quantity = data["installments_quantity"]
        if installments_quantity <= 0:
            raise ValueError("Installments quantity must be greater than zero")

        # Cálculo Price (juros compostos)
        interest_rate = Decimal(debt.creditor.interest_rate).quantize(Decimal("0.0001"))
        monthly_rate = interest_rate / Decimal("100")

        if monthly_rate > 0 and remaining_value > 0:
            rate_factor = (Decimal("1") + monthly_rate) ** installments_quantity
            installment_value = (
                remaining_value * (monthly_rate * rate_factor) / (rate_factor - Decimal("1"))
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            installment_value = (
                remaining_value / installments_quantity
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        total_price = (installment_value * installments_quantity).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        last_installment_value = (
                total_price - (installment_value * (installments_quantity - 1))
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        total_with_interest = (
                (installment_value * (installments_quantity - 1)) + last_installment_value
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        agreement = Agreement(
            debt_id=debt_id,
            total_traded=entry + total_with_interest,
            installment_value=installment_value,
            installments_quantity=installments_quantity,
            entry_value=entry,
            discount_applied=discount,
            first_due_date=data["first_due_date"],
        )

        debt.renegotiation_count += 1
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
                else installment_value
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
    def open_agreement(agreement: Agreement, user: User, session):
        if not agreement.status == AgreementStatus.DRAFT:
            raise AgreementStatusError("Agreement cannot opened")

        debt = agreement.debt

        has_active = session.query(
            exists().where(
                Agreement.debt_id == debt.id,
                Agreement.status == AgreementStatus.ACTIVE
            )
        ).scalar()

        if has_active:
            raise AgreementStatusError("Debt already has an active agreement")

        old_status = debt.status

        debt.status = DebtStatus.IN_AGREEMENT
        debt.updated_value = agreement.total_traded
        debt.last_agreement_date = agreement.created_at
        agreement.status = AgreementStatus.ACTIVE

        DebtHistoryService.record_agreement_activated(
            debt=debt,
            agreement_id=str(agreement.id),
            old_status=old_status,
            total_traded=agreement.total_traded,
            installments_quantity=agreement.installments_quantity,
            user=user,
            session=session
        )

        session.commit()

        return agreement

    @staticmethod
    def cancel_agreement(agreement: Agreement, session):
        if agreement.status == AgreementStatus.COMPLETED:
            raise AgreementStatusError("Cannot cancel a completed agreement")
        if agreement.status == AgreementStatus.CANCELLED:
            raise AgreementStatusError("Agreement already cancelled")

        agreement_old_status = agreement.status
        agreement.status = AgreementStatus.CANCELLED

        Installments.query.filter_by(
            agreement_id=agreement.id
        ).update({"status": InstallmentStatus.CANCELLED})

        debt_old_status = agreement.debt.status
        agreement.debt.updated_value = None
        agreement.debt.status = DebtStatus.OPEN

        DebtHistoryService.record_agreement_cancelled(
            debt=agreement.debt,
            agreement_id=str(agreement.id),
            debt_old_status=debt_old_status,
            agreement_old_status=agreement_old_status,
            agreement_new_status=agreement.status,
            session=session
        )

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
