"""rename agreementstatus to agreement_status_enum

Revision ID: 52fa4c5f90f4
Revises: 184610a405a1
Create Date: 2026-04-19 20:40:40.277292

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52fa4c5f90f4'
down_revision = '184610a405a1'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE agreementstatus RENAME TO agreement_status_enum;")


def downgrade():
    op.execute("ALTER TYPE agreement_status_enum RENAME TO agreementstatus;")
