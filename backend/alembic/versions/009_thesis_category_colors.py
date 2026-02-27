"""Add color column to thesis_categories

Revision ID: 009_thesis_category_colors
Revises: 008_thesis_categories
Create Date: 2026-02-20 06:53:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '009_thesis_category_colors'
down_revision = '008_thesis_categories'
branch_labels = None
depends_on = None

COLORS = {
    "Market": "#dbeafe,#1e40af",
    "Differentiation": "#f3e8ff,#6b21a8",
    "Distribution": "#fef3c7,#92400e",
    "Buyer / Adoption": "#d1fae5,#065f46",
    "Capability": "#ffe4e6,#9f1239",
    "Category": "#cffafe,#155e75",
}


def upgrade() -> None:
    op.add_column('thesis_categories', sa.Column('color', sa.Text(), nullable=True))
    for name, color in COLORS.items():
        op.execute(
            sa.text("UPDATE thesis_categories SET color = :color WHERE name = :name").bindparams(color=color, name=name)
        )


def downgrade() -> None:
    op.drop_column('thesis_categories', 'color')
