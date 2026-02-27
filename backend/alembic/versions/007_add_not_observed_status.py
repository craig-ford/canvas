"""Add not_observed to proof point status enum

Revision ID: 007_add_not_observed_status
Revises: 006_health_indicator_cache
Create Date: 2026-02-19 09:00:00.000000

"""
from alembic import op

revision = '007_add_not_observed_status'
down_revision = '006_health_indicator_cache'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("ALTER TYPE proofpointstatus ADD VALUE IF NOT EXISTS 'not_observed' AFTER 'observed'")

def downgrade():
    # PostgreSQL doesn't support removing enum values; would need full enum recreation
    pass
