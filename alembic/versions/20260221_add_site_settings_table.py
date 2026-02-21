"""Add site_settings table

Revision ID: a1b2c3d4e5f6
Revises: 052c36e7ecc4
Create Date: 2026-02-21 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '052c36e7ecc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Default settings to seed
DEFAULT_SETTINGS = {
    "site_name": "嫚霏 SPA",
    "address": "嘉義市西區北港路 8 號",
    "phone": "05-2273758",
    "business_hours": "週一至週日 09:00 - 17:00",
    "line_url": "",
    "facebook_url": "",
    "instagram_url": "",
    "meta_title": "嫚霏 SPA | 專業德系護膚",
    "meta_description": "嫚霏 SPA 位於嘉義，提供專業德系護膚服務，以科學為基底，為您找回肌膚原本的光采。",
    "og_image": "",
}


def upgrade() -> None:
    # Create site_settings table
    site_settings = op.create_table(
        'site_settings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('key', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('value', sa.Text(), nullable=False, server_default=''),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Seed default settings
    op.bulk_insert(
        site_settings,
        [{"key": k, "value": v} for k, v in DEFAULT_SETTINGS.items()]
    )


def downgrade() -> None:
    op.drop_table('site_settings')
