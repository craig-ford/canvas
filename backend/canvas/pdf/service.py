from uuid import UUID
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from canvas.models.canvas import Canvas
from canvas.models.thesis import Thesis


class CanvasNotFoundError(Exception):
    """Raised when canvas doesn't exist"""
    pass


class PDFGenerationError(Exception):
    """Raised when PDF creation fails"""
    pass


class PDFService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.jinja_env = Environment(
            loader=FileSystemLoader('canvas/pdf/templates')
        )

    async def export_canvas(self, canvas_id: UUID) -> bytes:
        """Export canvas as PDF with proper styling.

        Args:
            canvas_id: UUID of canvas to export

        Returns:
            PDF file content as bytes

        Raises:
            CanvasNotFoundError: If canvas doesn't exist
            PDFGenerationError: If PDF creation fails
        """
        try:
            canvas = await self._get_canvas_with_relations(self.db, canvas_id)

            template = self.jinja_env.get_template("canvas.html")
            html_content = template.render(
                vbu_name=canvas.vbu.name,
                lifecycle_lane=canvas.lifecycle_lane.value,
                success_description=canvas.success_description or "",
                future_state_intent=canvas.future_state_intent or "",
                theses=canvas.theses,
                primary_constraint=canvas.primary_constraint or ""
            )

            pdf_bytes = HTML(string=html_content).write_pdf()
            return pdf_bytes

        except CanvasNotFoundError:
            raise
        except (OSError, IOError) as e:
            raise PDFGenerationError(f"Failed to generate PDF: {str(e)}")

    async def _get_canvas_with_relations(self, db: AsyncSession, canvas_id: UUID) -> Canvas:
        """Get canvas with VBU and theses relations."""
        stmt = select(Canvas).options(
            selectinload(Canvas.vbu),
            selectinload(Canvas.theses).selectinload(Thesis.proof_points)
        ).where(Canvas.id == canvas_id)

        result = await db.execute(stmt)
        canvas = result.scalar_one_or_none()

        if not canvas:
            raise CanvasNotFoundError(f"Canvas {canvas_id} not found")

        return canvas
