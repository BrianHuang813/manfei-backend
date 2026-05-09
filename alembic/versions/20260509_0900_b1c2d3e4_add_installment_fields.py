"""add_installment_fields_to_transactions

Revision ID: b1c2d3e4
Revises: a3f5b9e2
Create Date: 2026-05-09 09:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b1c2d3e4'
down_revision: Union[str, None] = 'a3f5b9e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('transactions', sa.Column('is_installment', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('transactions', sa.Column('total_installments', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('amount_per_installment', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('paid_installments', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('transactions', sa.Column('paid_amount', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('transactions', 'paid_amount')
    op.drop_column('transactions', 'paid_installments')
    op.drop_column('transactions', 'amount_per_installment')
    op.drop_column('transactions', 'total_installments')
    op.drop_column('transactions', 'is_installment')
