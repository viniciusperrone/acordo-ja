"""recreate debt history enum

Revision ID: ee979f6f4b54
Revises: c1cc5c92d357
Create Date: 2026-04-20 15:28:35.564569

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision = 'ee979f6f4b54'
down_revision = 'c1cc5c92d357'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP TABLE IF EXISTS debt_history;")
    op.execute("DROP TYPE IF EXISTS debt_history_type_enum;")

    op.create_table(
        'debt_history',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('debt_id', sa.UUID(), nullable=False),

        sa.Column(
            'event_type',
            sa.Enum(
                'DEBT_CREATED',
                'DEBT_PAID',
                'DEBT_CANCELLED',
                'DEBT_DEFAULTED',
                'AGREEMENT_ACTIVATED',
                'AGREEMENT_CANCELLED',
                'INTEREST_APPLIED',
                'DISCOUNT_APPLIED',
                name='debt_history_type_enum',
                create_type=True
            ),
            nullable=False
        ),

        sa.Column('old_status', ENUM(name='debt_status_enum', create_type=False), nullable=True),
        sa.Column('new_status', ENUM(name='debt_status_enum', create_type=False), nullable=True),
        sa.Column('old_value', sa.Numeric(12, 2), nullable=True),
        sa.Column('new_value', sa.Numeric(12, 2), nullable=True),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.Column('reason', sa.String(), nullable=True),
        sa.Column('extra', sa.JSON(), nullable=True),

        sa.ForeignKeyConstraint(['debt_id'], ['debts.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        'ix_debt_history_debt_id_changed_at',
        'debt_history',
        ['debt_id', 'changed_at']
    )

def downgrade():
    op.drop_index('ix_debt_history_debt_id_changed_at', table_name='debt_history')
    op.drop_table('debt_history')
    op.execute("DROP TYPE debt_history_type_enum")
