"""Add canvas update trigger for monthly reviews

Revision ID: 005_canvas_trigger
Revises: 004_monthly_reviews
Create Date: 2026-02-13 14:01:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '005_canvas_trigger'
down_revision = '004_monthly_reviews'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_canvas_currently_testing()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.currently_testing_type IS NOT NULL AND NEW.currently_testing_id IS NOT NULL THEN
                UPDATE canvases 
                SET currently_testing_type = NEW.currently_testing_type,
                    currently_testing_id = NEW.currently_testing_id,
                    updated_at = NOW()
                WHERE id = NEW.canvas_id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger
    op.execute("""
        CREATE TRIGGER trigger_update_canvas_currently_testing
            AFTER INSERT ON monthly_reviews
            FOR EACH ROW
            EXECUTE FUNCTION update_canvas_currently_testing();
    """)

def downgrade() -> None:
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS trigger_update_canvas_currently_testing ON monthly_reviews;")
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_canvas_currently_testing();")