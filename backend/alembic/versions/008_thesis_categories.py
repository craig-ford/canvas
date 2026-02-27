"""Add thesis_categories table and category_id FK on theses

Revision ID: 008_thesis_categories
Revises: 007_add_not_observed_status
Create Date: 2026-02-20 06:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

revision = '008_thesis_categories'
down_revision = '007_add_not_observed_status'
branch_labels = None
depends_on = None

# Seed data
CATEGORIES = [
    ("Market", 'The market will reward X. Example: "Enterprise buyers will consolidate from 5 vendors to 2 within 18 months."'),
    ("Differentiation", 'We will win because of X. Example: "Our real-time analytics pipeline will become the reason customers choose us over competitors."'),
    ("Distribution", 'Channel will scale. Example: "Partner-led distribution will account for 40% of new logos by end of year."'),
    ("Buyer / Adoption", 'The buyer will pay for X. Example: "Mid-market CFOs will pay a premium for automated compliance reporting."'),
    ("Capability", 'We can become good at X. Example: "The team will build production-grade ML ops capability within two quarters."'),
    ("Category", 'This category will shift toward Y. Example: "The industry will move from on-prem to cloud-native delivery as the default."'),
]


def upgrade() -> None:
    op.create_table(
        'thesis_categories',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.Text(), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Seed the 6 thesis types
    thesis_categories = sa.table(
        'thesis_categories',
        sa.column('id', UUID(as_uuid=True)),
        sa.column('name', sa.Text),
        sa.column('description', sa.Text),
    )
    op.bulk_insert(thesis_categories, [
        {"id": uuid.uuid4(), "name": name, "description": desc}
        for name, desc in CATEGORIES
    ])

    op.add_column('theses', sa.Column('category_id', UUID(as_uuid=True), nullable=True))
    op.create_index('ix_theses_category_id', 'theses', ['category_id'])
    op.create_foreign_key('fk_theses_category_id', 'theses', 'thesis_categories', ['category_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.drop_constraint('fk_theses_category_id', 'theses', type_='foreignkey')
    op.drop_index('ix_theses_category_id', table_name='theses')
    op.drop_column('theses', 'category_id')
    op.drop_table('thesis_categories')
