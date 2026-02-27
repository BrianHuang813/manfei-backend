"""UUID for users, soft delete everywhere, MemberTier enum, transactions table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # STEP 1: Ensure pgcrypto extension for gen_random_uuid()
    # ------------------------------------------------------------------
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # ------------------------------------------------------------------
    # STEP 2: Create MemberTier PostgreSQL ENUM type
    # ------------------------------------------------------------------
    membertier_enum = sa.Enum('regular', 'vip', name='membertier', create_type=False)
    op.execute("CREATE TYPE membertier AS ENUM ('regular', 'vip')")

    # ------------------------------------------------------------------
    # STEP 3: Add deleted_at column to ALL existing tables (soft delete)
    # ------------------------------------------------------------------
    for table in ['news', 'services', 'products', 'testimonials', 'portfolio',
                  'users', 'work_logs', 'site_settings']:
        op.add_column(table, sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))

    # ------------------------------------------------------------------
    # STEP 4: Add tier column to users table
    # ------------------------------------------------------------------
    op.add_column('users', sa.Column(
        'tier', membertier_enum, nullable=False, server_default='regular'
    ))
    op.create_index('ix_users_tier', 'users', ['tier'])

    # ------------------------------------------------------------------
    # STEP 5: Convert users.id from Integer to UUID
    #   - Add a temporary UUID column
    #   - Populate it with gen_random_uuid() for existing rows
    #   - Drop the FK from work_logs.user_id
    #   - Drop the old PK constraint
    #   - Drop the old integer id and rename new_id to id
    #   - Recreate PK and index
    #   - Convert work_logs.user_id to UUID with mapping
    # ------------------------------------------------------------------

    # 5a. Add temp UUID column to users
    op.add_column('users', sa.Column('new_id', UUID(as_uuid=True), nullable=True))
    op.execute("UPDATE users SET new_id = gen_random_uuid()")
    op.alter_column('users', 'new_id', nullable=False)

    # 5b. Add temp UUID column to work_logs for new user_id
    op.add_column('work_logs', sa.Column('new_user_id', UUID(as_uuid=True), nullable=True))

    # 5c. Map existing integer user_ids to UUID via JOIN
    op.execute("""
        UPDATE work_logs
        SET new_user_id = u.new_id
        FROM users u
        WHERE work_logs.user_id = u.id
    """)

    # 5d. Drop the FK constraint on work_logs.user_id before altering columns
    op.drop_constraint('work_logs_user_id_fkey', 'work_logs', type_='foreignkey')
    op.drop_index('ix_work_logs_user_id', table_name='work_logs')

    # 5e. Drop old integer user_id from work_logs, rename new_user_id
    op.drop_column('work_logs', 'user_id')
    op.alter_column('work_logs', 'new_user_id', new_column_name='user_id', nullable=False)
    op.create_index('ix_work_logs_user_id', 'work_logs', ['user_id'])

    # 5f. Drop old PK and index on users.id
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_index('ix_users_id', table_name='users')

    # 5g. Drop old integer id, rename new_id to id
    op.drop_column('users', 'id')
    op.alter_column('users', 'new_id', new_column_name='id')

    # 5h. Recreate PK and index on users.id (UUID)
    op.create_primary_key('users_pkey', 'users', ['id'])
    op.create_index('ix_users_id', 'users', ['id'])

    # 5i. Recreate FK from work_logs.user_id → users.id (UUID)
    op.create_foreign_key(
        'work_logs_user_id_fkey', 'work_logs', 'users',
        ['user_id'], ['id'], ondelete='CASCADE'
    )

    # ------------------------------------------------------------------
    # STEP 6: Create transactions table
    # ------------------------------------------------------------------
    op.create_table(
        'transactions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('service_name', sa.String(255), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_transactions_id', 'transactions', ['id'])


def downgrade() -> None:
    """
    WARNING: Downgrading from UUID back to Integer for users.id will NOT
    preserve original integer IDs. This is a destructive migration.
    All work_logs.user_id FK references will be rebuilt with new integer IDs.
    """
    # ------------------------------------------------------------------
    # Reverse STEP 6: Drop transactions table
    # ------------------------------------------------------------------
    op.drop_index('ix_transactions_id', table_name='transactions')
    op.drop_table('transactions')

    # ------------------------------------------------------------------
    # Reverse STEP 5: Convert users.id from UUID back to Integer (serial)
    # ------------------------------------------------------------------

    # Drop FK from work_logs
    op.drop_constraint('work_logs_user_id_fkey', 'work_logs', type_='foreignkey')
    op.drop_index('ix_work_logs_user_id', table_name='work_logs')

    # Add temp integer columns
    op.add_column('users', sa.Column('new_id', sa.Integer(), autoincrement=True, nullable=True))
    op.execute("CREATE SEQUENCE IF NOT EXISTS users_id_seq")
    op.execute("SELECT setval('users_id_seq', 1)")
    op.execute("UPDATE users SET new_id = nextval('users_id_seq')")
    op.alter_column('users', 'new_id', nullable=False)

    # Map work_logs user_id UUID → new integer
    op.add_column('work_logs', sa.Column('new_user_id', sa.Integer(), nullable=True))
    op.execute("""
        UPDATE work_logs
        SET new_user_id = u.new_id
        FROM users u
        WHERE work_logs.user_id = u.id
    """)

    # Swap columns on work_logs
    op.drop_column('work_logs', 'user_id')
    op.alter_column('work_logs', 'new_user_id', new_column_name='user_id', nullable=False)
    op.create_index('ix_work_logs_user_id', 'work_logs', ['user_id'])

    # Swap columns on users
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_column('users', 'id')
    op.alter_column('users', 'new_id', new_column_name='id')
    op.create_primary_key('users_pkey', 'users', ['id'])
    op.create_index('ix_users_id', 'users', ['id'])

    # Restore FK
    op.create_foreign_key(
        'work_logs_user_id_fkey', 'work_logs', 'users',
        ['user_id'], ['id'], ondelete='CASCADE'
    )

    # ------------------------------------------------------------------
    # Reverse STEP 4: Remove tier column and enum
    # ------------------------------------------------------------------
    op.drop_index('ix_users_tier', table_name='users')
    op.drop_column('users', 'tier')
    op.execute("DROP TYPE IF EXISTS membertier")

    # ------------------------------------------------------------------
    # Reverse STEP 3: Remove deleted_at from all tables
    # ------------------------------------------------------------------
    for table in ['news', 'services', 'products', 'testimonials', 'portfolio',
                  'users', 'work_logs', 'site_settings']:
        op.drop_column(table, 'deleted_at')

    # ------------------------------------------------------------------
    # Reverse STEP 1: Drop pgcrypto (optional, may be used elsewhere)
    # ------------------------------------------------------------------
    # op.execute('DROP EXTENSION IF EXISTS "pgcrypto"')
