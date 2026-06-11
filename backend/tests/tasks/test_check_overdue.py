import pytest
from unittest.mock import patch

from datetime import date, timedelta

from tasks.check_overdue import check_overdue_installments
from utils.enum import InstallmentStatus


@pytest.mark.tasks
@pytest.mark.db
class TestCheckOverdueTask:
    """
    Tests for overdue installments scheduler task.
    """

    @patch("tasks.check_overdue.NotificationEvents.on_installment_overdue")
    def test_marks_pending_overdue_installments(self, mock_notification, installment, session):
        """
        Should mark overdue pending installments as OVERDUE.
        """

        installment.status = InstallmentStatus.PENDING
        installment.due_date = date.today() - timedelta(days=5)

        session.flush()

        check_overdue_installments()

        session.refresh(installment)

        assert installment.status == InstallmentStatus.OVERDUE

        mock_notification.assert_called_once()

    @patch("tasks.check_overdue.NotificationEvents.on_installment_overdue")
    def test_does_not_mark_future_installments(self, mock_notification, installment, session):
        """
        Should keep future installments as PENDING.
        """

        installment.status = InstallmentStatus.PENDING
        installment.due_date = date.today() + timedelta(days=5)

        session.flush()

        check_overdue_installments()

        session.refresh(installment)

        assert installment.status == InstallmentStatus.PENDING

        mock_notification.assert_not_called()

    @patch("tasks.check_overdue.NotificationEvents.on_installment_overdue")
    def test_does_not_update_paid_installments(self, mock_notification, installment, session):
        """
        Should not update installments already paid
        """
        installment.status = InstallmentStatus.PAID
        installment.due_date = date.today() - timedelta(days=10)

        session.flush()

        check_overdue_installments()

        assert installment.status == InstallmentStatus.PAID

        mock_notification.assert_not_called()

    @patch("tasks.check_overdue.db.session.commit")
    def test_commits_after_processing(self, mock_commit, installment, session):
        """
        Should commit transaction after processing installments
        """
        installment.status = InstallmentStatus.PENDING
        installment.due_date = date.today() - timedelta(days=5)

        session.flush()

        check_overdue_installments()

        mock_commit.assert_called_once()

    @patch("tasks.check_overdue.db.session.rollback")
    @patch("tasks.check_overdue.NotificationEvents.on_installment_overdue")
    def test_rollbacks_when_exception_occurs(
            self,
            mock_notification,
            mock_rollback,
            installment,
            session,
    ):
        installment.status = InstallmentStatus.PENDING
        installment.due_date = date.today() - timedelta(days=5)

        session.flush()

        mock_notification.side_effect = Exception("unexpected error")

        check_overdue_installments()

        session.refresh(installment)

        assert installment.status == InstallmentStatus.PENDING
        mock_rollback.assert_called_once()