"""add must_reset_password column

Revision ID: 011_add_must_reset_password
Revises: 010_add_group_leader_role
"""
from alembic import op
import sqlalchemy as sa

revision = "011_add_must_reset_password"
down_revision = "010_add_group_leader_role"

def upgrade():
    op.add_column("users", sa.Column("must_reset_password", sa.Boolean(), nullable=False, server_default="false"))

def downgrade():
    op.drop_column("users", "must_reset_password")
