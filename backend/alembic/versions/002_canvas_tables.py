"""Add canvas management tables

Revision ID: 002_canvas_tables
Revises: 001_auth_tables
Create Date: 2026-02-13 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002_canvas_tables'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create lifecycle lane enum
    lifecycle_lane_enum = postgresql.ENUM('build', 'sell', 'milk', 'reframe', name='lifecyclelane')
    lifecycle_lane_enum.create(op.get_bind())
    
    # Create proof point status enum
    proof_point_status_enum = postgresql.ENUM('not_started', 'in_progress', 'observed', 'stalled', name='proofpointstatus')
    proof_point_status_enum.create(op.get_bind())
    
    # Create currently testing type enum
    currently_testing_type_enum = postgresql.ENUM('thesis', 'proof_point', name='currentlytestingtype')
    currently_testing_type_enum.create(op.get_bind())
    
    # Create vbus table
    op.create_table('vbus',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('gm_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['gm_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("LENGTH(TRIM(name)) > 0", name="ck_vbu_name_not_empty")
    )
    
    # Create canvases table
    op.create_table('canvases',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('vbu_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=True),
        sa.Column('lifecycle_lane', lifecycle_lane_enum, nullable=False, server_default='build'),
        sa.Column('success_description', sa.Text(), nullable=True),
        sa.Column('future_state_intent', sa.Text(), nullable=True),
        sa.Column('primary_focus', sa.String(length=255), nullable=True),
        sa.Column('resist_doing', sa.Text(), nullable=True),
        sa.Column('good_discipline', sa.Text(), nullable=True),
        sa.Column('primary_constraint', sa.Text(), nullable=True),
        sa.Column('currently_testing_type', currently_testing_type_enum, nullable=True),
        sa.Column('currently_testing_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('portfolio_notes', sa.Text(), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['vbu_id'], ['vbus.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vbu_id', name='uq_canvases_vbu_id'),
        sa.CheckConstraint("product_name IS NULL OR LENGTH(TRIM(product_name)) > 0", name="ck_canvas_product_name_not_empty"),
        sa.CheckConstraint("(currently_testing_type IS NULL) = (currently_testing_id IS NULL)", name="ck_canvas_currently_testing_consistency")
    )
    
    # Create theses table
    op.create_table('theses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('canvas_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['canvas_id'], ['canvases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('canvas_id', 'order', name='uq_theses_canvas_order'),
        sa.CheckConstraint("order BETWEEN 1 AND 5", name="ck_thesis_order_range"),
        sa.CheckConstraint("LENGTH(TRIM(text)) > 0", name="ck_thesis_text_not_empty")
    )
    
    # Create proof_points table
    op.create_table('proof_points',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('thesis_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', proof_point_status_enum, nullable=False, server_default='not_started'),
        sa.Column('evidence_note', sa.Text(), nullable=True),
        sa.Column('target_review_month', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['thesis_id'], ['theses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("LENGTH(TRIM(description)) > 0", name="ck_proof_point_description_not_empty")
    )
    
    # Create attachments table
    op.create_table('attachments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('proof_point_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('monthly_review_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('storage_path', sa.String(length=1024), nullable=False),
        sa.Column('content_type', sa.String(length=128), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=255), nullable=True),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['proof_point_id'], ['proof_points.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['monthly_review_id'], ['monthly_reviews.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('storage_path', name='uq_attachments_storage_path'),
        sa.CheckConstraint("LENGTH(TRIM(filename)) > 0", name="ck_attachment_filename_not_empty"),
        sa.CheckConstraint("LENGTH(TRIM(storage_path)) > 0", name="ck_attachment_storage_path_not_empty"),
        sa.CheckConstraint("size_bytes BETWEEN 1 AND 10485760", name="ck_attachment_size_range"),
        sa.CheckConstraint("label IS NULL OR LENGTH(TRIM(label)) > 0", name="ck_attachment_label_not_empty"),
        sa.CheckConstraint("content_type IN ('image/jpeg','image/png','image/gif','application/pdf','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/vnd.openxmlformats-officedocument.presentationml.presentation')", name="ck_attachment_content_type"),
        sa.CheckConstraint("(proof_point_id IS NULL) != (monthly_review_id IS NULL)", name="ck_attachment_exactly_one_parent")
    )
    
    # Create indexes
    op.create_index('ix_vbus_gm_id', 'vbus', ['gm_id'])
    op.create_index('ix_canvases_vbu_id', 'canvases', ['vbu_id'])
    op.create_index('ix_theses_canvas_id', 'theses', ['canvas_id'])
    op.create_index('ix_proof_points_thesis_id', 'proof_points', ['thesis_id'])
    op.create_index('ix_proof_points_status', 'proof_points', ['status'])
    op.create_index('ix_attachments_proof_point_id', 'attachments', ['proof_point_id'])
    op.create_index('ix_attachments_monthly_review_id', 'attachments', ['monthly_review_id'])
    op.create_index('ix_attachments_uploaded_by', 'attachments', ['uploaded_by'])
    op.create_index('ix_attachments_content_type', 'attachments', ['content_type'])

def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_attachments_content_type', table_name='attachments')
    op.drop_index('ix_attachments_uploaded_by', table_name='attachments')
    op.drop_index('ix_attachments_monthly_review_id', table_name='attachments')
    op.drop_index('ix_attachments_proof_point_id', table_name='attachments')
    op.drop_index('ix_proof_points_status', table_name='proof_points')
    op.drop_index('ix_proof_points_thesis_id', table_name='proof_points')
    op.drop_index('ix_theses_canvas_id', table_name='theses')
    op.drop_index('ix_canvases_vbu_id', table_name='canvases')
    op.drop_index('ix_vbus_gm_id', table_name='vbus')
    
    # Drop tables
    op.drop_table('attachments')
    op.drop_table('proof_points')
    op.drop_table('theses')
    op.drop_table('canvases')
    op.drop_table('vbus')
    
    # Drop enums
    currently_testing_type_enum = postgresql.ENUM('thesis', 'proof_point', name='currentlytestingtype')
    currently_testing_type_enum.drop(op.get_bind())
    
    proof_point_status_enum = postgresql.ENUM('not_started', 'in_progress', 'observed', 'stalled', name='proofpointstatus')
    proof_point_status_enum.drop(op.get_bind())
    
    lifecycle_lane_enum = postgresql.ENUM('build', 'sell', 'milk', 'reframe', name='lifecyclelane')
    lifecycle_lane_enum.drop(op.get_bind())