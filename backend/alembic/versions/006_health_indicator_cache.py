"""Add health indicator cache to canvases

Revision ID: 006_health_indicator_cache
Revises: 005_canvas_trigger
Create Date: 2026-02-13 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006_health_indicator_cache'
down_revision = '005_canvas_trigger'
branch_labels = None
depends_on = None

def upgrade():
    # Add health indicator cache columns
    op.add_column('canvases', sa.Column('health_indicator_cache', sa.String(20), nullable=True))
    op.add_column('canvases', sa.Column('health_computed_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create trigger function for health indicator updates
    op.execute("""
        CREATE OR REPLACE FUNCTION update_canvas_health_indicator()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE canvases 
            SET health_indicator_cache = (
                CASE 
                    WHEN EXISTS(SELECT 1 FROM proof_points pp JOIN theses t ON pp.thesis_id = t.id 
                               WHERE t.canvas_id = c.id AND pp.status = 'stalled') THEN 'At Risk'
                    WHEN NOT EXISTS(SELECT 1 FROM proof_points pp JOIN theses t ON pp.thesis_id = t.id 
                                   WHERE t.canvas_id = c.id AND pp.status != 'not_started') THEN 'Not Started'
                    WHEN EXISTS(SELECT 1 FROM proof_points pp JOIN theses t ON pp.thesis_id = t.id 
                               WHERE t.canvas_id = c.id AND pp.status = 'observed') 
                         AND NOT EXISTS(SELECT 1 FROM proof_points pp JOIN theses t ON pp.thesis_id = t.id 
                                       WHERE t.canvas_id = c.id AND pp.status = 'stalled') THEN 'On Track'
                    ELSE 'In Progress'
                END
            ),
            health_computed_at = NOW()
            FROM canvases c
            JOIN theses t ON t.canvas_id = c.id
            WHERE t.id = COALESCE(NEW.thesis_id, OLD.thesis_id);
            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger
    op.execute("""
        CREATE TRIGGER proof_point_health_update
            AFTER INSERT OR UPDATE OR DELETE ON proof_points
            FOR EACH ROW EXECUTE FUNCTION update_canvas_health_indicator();
    """)

def downgrade():
    op.execute("DROP TRIGGER IF EXISTS proof_point_health_update ON proof_points;")
    op.execute("DROP FUNCTION IF EXISTS update_canvas_health_indicator();")
    op.drop_column('canvases', 'health_computed_at')
    op.drop_column('canvases', 'health_indicator_cache')