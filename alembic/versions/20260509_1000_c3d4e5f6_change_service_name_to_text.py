"""change_service_name_to_text

Revision ID: c3d4e5f6
Revises: b1c2d3e4
Create Date: 2026-05-09 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c3d4e5f6'
down_revision: Union[str, None] = 'b1c2d3e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('transactions', 'service_name',
                    existing_type=sa.String(length=255),
                    type_=sa.Text(),
                    existing_nullable=False)


def downgrade() -> None:
    op.alter_column('transactions', 'service_name',
                    existing_type=sa.Text(),
                    type_=sa.String(length=255),
                    existing_nullable=False)
