from uuid import UUID

class CanvasNotFoundError(Exception):
    """Raised when canvas doesn't exist"""
    pass

class PDFGenerationError(Exception):
    """Raised when PDF creation fails"""
    pass

class PDFService:
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
        pass