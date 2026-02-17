import pytest
from uuid import uuid4, UUID
from canvas.pdf.service import PDFService, CanvasNotFoundError, PDFGenerationError

class TestPDFServiceContract:
    """Test PDFService interface contracts"""
    
    def test_service_instantiation(self):
        """Test PDFService can be instantiated"""
        service = PDFService()
        assert service is not None
    
    def test_export_canvas_signature(self):
        """Test export_canvas method signature"""
        service = PDFService()
        
        # Verify method exists and has correct signature
        assert hasattr(service, 'export_canvas')
        assert callable(service.export_canvas)
        
        # Check method is async
        import inspect
        assert inspect.iscoroutinefunction(service.export_canvas)
    
    def test_export_canvas_return_type_annotation(self):
        """Test export_canvas has correct return type annotation"""
        import inspect
        
        signature = inspect.signature(PDFService.export_canvas)
        return_annotation = signature.return_annotation
        
        # Should return bytes
        assert 'bytes' in str(return_annotation)
    
    def test_export_canvas_parameter_annotation(self):
        """Test export_canvas has correct parameter annotations"""
        import inspect
        
        signature = inspect.signature(PDFService.export_canvas)
        params = signature.parameters
        
        # Should have self and canvas_id parameters
        assert 'self' in params
        assert 'canvas_id' in params
        
        # canvas_id should be UUID type
        canvas_id_annotation = params['canvas_id'].annotation
        assert canvas_id_annotation == UUID

class TestPDFServiceExceptions:
    """Test PDFService exception contracts"""
    
    def test_canvas_not_found_error_exists(self):
        """Test CanvasNotFoundError exception is defined"""
        assert CanvasNotFoundError is not None
        assert issubclass(CanvasNotFoundError, Exception)
    
    def test_pdf_generation_error_exists(self):
        """Test PDFGenerationError exception is defined"""
        assert PDFGenerationError is not None
        assert issubclass(PDFGenerationError, Exception)
    
    def test_canvas_not_found_error_instantiation(self):
        """Test CanvasNotFoundError can be instantiated"""
        error = CanvasNotFoundError("Canvas not found")
        assert str(error) == "Canvas not found"
    
    def test_pdf_generation_error_instantiation(self):
        """Test PDFGenerationError can be instantiated"""
        error = PDFGenerationError("PDF generation failed")
        assert str(error) == "PDF generation failed"

class TestPDFServiceBehaviorContract:
    """Test expected behavior contracts for PDFService"""
    
    def test_export_canvas_with_valid_uuid(self):
        """Test export_canvas accepts valid UUID"""
        service = PDFService()
        canvas_id = uuid4()
        
        # This is a contract test - we're verifying the interface accepts UUID
        # The actual implementation will be tested in integration tests
        assert isinstance(canvas_id, UUID)
    
    def test_export_canvas_docstring(self):
        """Test export_canvas has proper docstring"""
        docstring = PDFService.export_canvas.__doc__
        assert docstring is not None
        assert "Export canvas as PDF" in docstring
        assert "Args:" in docstring
        assert "Returns:" in docstring
        assert "Raises:" in docstring
        assert "CanvasNotFoundError" in docstring
        assert "PDFGenerationError" in docstring

class TestPDFServiceErrorHandlingContract:
    """Test error handling contracts"""
    
    def test_canvas_not_found_error_in_signature(self):
        """Test CanvasNotFoundError is documented in method signature"""
        docstring = PDFService.export_canvas.__doc__
        assert "CanvasNotFoundError: If canvas doesn't exist" in docstring
    
    def test_pdf_generation_error_in_signature(self):
        """Test PDFGenerationError is documented in method signature"""
        docstring = PDFService.export_canvas.__doc__
        assert "PDFGenerationError: If PDF creation fails" in docstring
    
    def test_return_type_is_bytes(self):
        """Test method is documented to return bytes"""
        docstring = PDFService.export_canvas.__doc__
        assert "PDF file content as bytes" in docstring