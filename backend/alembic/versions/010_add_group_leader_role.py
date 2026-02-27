"""Add group_leader role and VBU group_leader_id

Revision ID: 010
Revises: 009
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "010_add_group_leader_role"
down_revision = "009_thesis_category_colors"

def upgrade():
    # Add group_leader to the enum
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'group_leader'")
    
    # Add group_leader_id column to vbus
    op.add_column("vbus", sa.Column("group_leader_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True))
    op.create_index("ix_vbus_group_leader_id", "vbus", ["group_leader_id"])

def downgrade():
    op.drop_index("ix_vbus_group_leader_id", "vbus")
    op.drop_column("vbus", "group_leader_id")
    # Note: PostgreSQL doesn't support removing enum values
