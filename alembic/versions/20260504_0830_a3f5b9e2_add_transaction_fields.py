"""add_transaction_date_sort_order_and_updated_at

Revision ID: a3f5b9e2
Revises: 4d3cd28835d6
Create Date: 2026-05-04 08:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = 'a3f5b9e2'
down_revision: Union[str, None] = '4d3cd28835d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to transactions table
    op.add_column('transactions', sa.Column('transaction_date', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False))
    op.add_column('transactions', sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False))
    op.add_column('transactions', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    
    # Create indices for new columns
    op.create_index(op.f('ix_transactions_transaction_date'), 'transactions', ['transaction_date'], unique=False)
    op.create_index(op.f('ix_transactions_sort_order'), 'transactions', ['sort_order'], unique=False)
    
    # Backfill data
    # 1. Fill transaction_date from created_at (extract date part)
    op.execute(text("""
        UPDATE transactions
        SET transaction_date = DATE(created_at)
        WHERE deleted_at IS NULL
    """))
    
    # 2. Fill sort_order: for each user, assign continuous sort_order based on created_at ascending
    # This query ranks transactions by created_at within each user group
    op.execute(text("""
        WITH ranked_transactions AS (
            SELECT 
                id,
                ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at ASC, id ASC) - 1 as new_sort_order
            FROM transactions
            WHERE deleted_at IS NULL
        )
        UPDATE transactions
        SET sort_order = ranked_transactions.new_sort_order
        FROM ranked_transactions
        WHERE transactions.id = ranked_transactions.id
    """))


def downgrade() -> None:
    # Drop indices
    op.drop_index(op.f('ix_transactions_sort_order'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_transaction_date'), table_name='transactions')
    
    # Drop columns
    op.drop_column('transactions', 'updated_at')
    op.drop_column('transactions', 'sort_order')
    op.drop_column('transactions', 'transaction_date')
