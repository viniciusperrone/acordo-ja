import pytest

from decimal import Decimal
from datetime import date

from debts.services import DebtService

from utils.enum import DebtStatus


@pytest.mark.integration
@pytest.mark.db
class TestDebtFlow:
    """
    Validate debt creation and search workflows involving
    creditors, debtors, and related business rules.
    """

    def test_should_create_debt_with_valid_creditor_and_debtor(self, creditor, debtor, manager_user, session):
        data = {
            "creditor_id": creditor.id,
            "debtor_id": debtor.id,
            "original_value": Decimal("3000.00"),
            "due_date": date(2026, 12, 31),
        }

        debt = DebtService.create(
            data,
            manager_user,
            session,
        )

        session.commit()

        assert debt.id is not None
        assert debt.creditor_id == creditor.id
        assert debt.debtor_id == debtor.id
        assert debt.original_value == Decimal("3000.00")
        assert debt.status == DebtStatus.OPEN


    def test_should_return_debts_for_existing_document(self, debt, session):
        result = DebtService.search(
            debt.debtor.document,
            session,
        )

        assert result["document"] == debt.debtor.document
        assert result["has_debts"] is True
        assert result["total_debts"] == 1
        assert len(result["debts"]) == 1

        returned_debt = result["debts"][0]

        assert returned_debt["id"] == debt.id
        assert returned_debt["amount"] == debt.original_value
        assert returned_debt["status"] == debt.status.value
        assert returned_debt["creditor"] == debt.creditor.bank_name

    def test_should_return_empty_result_for_document_without_debts(self, session):
        document = "52998224725"

        result = DebtService.search(
            document,
            session,
        )

        assert result["document"] == document
        assert result["has_debts"] is False
        assert result["debts"] == []
        assert result["total_debts"] == 0
        assert result["total_amount"] == 0
        assert result["redirect_url"] is None
