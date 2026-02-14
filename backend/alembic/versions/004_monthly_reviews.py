"""Add monthly_reviews and commitments tables

Revision ID: 004_monthly_reviews
Revises: 003_canvas_management
Create Date: 2026-02-13 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '004_monthly_reviews'
down_revision = '003_canvas_management'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create testing_type enum
    testing_type_enum = postgresql.ENUM('thesis', 'proof_point', name='testing_type')
    testing_type_enum.create(op.get_bind())
    
    # Create monthly_reviews table
    op.create_table('monthly_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('canvas_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('review_date', sa.Date(), nullable=False),
        sa.Column('what_moved', sa.Text(), nullable=True),
        sa.Column('what_learned', sa.Text(), nullable=True),
        sa.Column('what_threatens', sa.Text(), nullable=True),
        sa.Column('currently_testing_type', testing_type_enum, nullable=True),
        sa.Column('currently_testing_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['canvas_id'], ['canvases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('canvas_id', 'review_date', name='uq_monthly_reviews_canvas_date'),
        sa.CheckConstraint("currently_testing_type IN ('thesis', 'proof_point') OR currently_testing_type IS NULL")
    )
    
    # Create commitments table
    op.create_table('commitments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('monthly_review_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['monthly_review_id'], ['monthly_reviews.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('monthly_review_id', 'order', name='uq_commitments_review_order'),
        sa.CheckConstraint('length(text) > 0 AND length(text) <= 1000', name='ck_commitments_text_length'),
        sa.CheckConstraint('order >= 1 AND order <= 3', name='ck_commitments_order_range')
    )
    
    # Create indexes
    op.create_index('ix_monthly_reviews_canvas_id', 'monthly_reviews', ['canvas_id'])
    op.create_index('ix_monthly_reviews_review_date', 'monthly_reviews', ['review_date'])
    op.create_index('ix_monthly_reviews_created_by', 'monthly_reviews', ['created_by'])
    op.create_index('ix_commitments_review_id', 'commitments', ['monthly_review_id'])

def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_commitments_review_id', table_name='commitments')
    op.drop_index('ix_monthly_reviews_created_by', table_name='monthly_reviews')
    op.drop_index('ix_monthly_reviews_review_date', table_name='monthly_reviews')
    op.drop_index('ix_monthly_reviews_canvas_id', table_name='monthly_reviews')
    
    # Drop tables
    op.drop_table('commitments')
    op.drop_table('monthly_reviews')
    
    # Drop enum
    testing_type_enum = postgresql.ENUM('thesis', 'proof_point', name='testing_type')
    testing_type_enum.drop(op.get_bind())