"""fix missing timestamp defaults

Revision ID: 18f9158b7778
Revises: b48b47cb7991
Create Date: 2026-05-07 22:26:47.755602

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18f9158b7778'
down_revision = 'b48b47cb7991'
branch_labels = None
depends_on = None


def upgrade():
    columns = [
        ("agreements", "created_at"),
        ("agreements", "updated_at"),
        ("creditors", "created_at"),
        ("debtors", "created_at"),
        ("debtors", "updated_at"),
        ("debts", "created_at"),
        ("debts", "updated_at"),
        ("installments", "created_at"),
        ("installments", "updated_at"),
        ("leads", "created_at"),
        ("notifications", "created_at"),
        ("password_reset_tokens", "created_at"),
        ("token_blocklist", "created_at"),
    ]

    for table, column in columns:
        op.alter_column(
            table,
            column,
            server_default=sa.text("now()"),
        )


def downgrade():
    columns = [
        ("agreements", "created_at"),
        ("agreements", "updated_at"),
        ("creditors", "created_at"),
        ("debtors", "created_at"),
        ("debtors", "updated_at"),
        ("debts", "created_at"),
        ("debts", "updated_at"),
        ("installments", "created_at"),
        ("installments", "updated_at"),
        ("leads", "created_at"),
        ("notifications", "created_at"),
        ("password_reset_tokens", "created_at"),
        ("token_blocklist", "created_at"),
    ]

    for table, column in columns:
        op.alter_column(
            table,
            column,
            server_default=None
        )
