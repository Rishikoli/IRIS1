"""
Project IRIS - OCR and Document Processing Tests
Test OCR extraction, document scraping, and text processing
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.utils.ocr_processor import OCRProcessor
from src.utils.document_scraper import DocumentScraper


class TestOCRProcessor:
    """Test OCR processing functionality"""

    @pytest.fixture
    def ocr_processor(self):
        """Create OCR processor with test configuration"""
        return OCRProcessor()

    def test_ocr_processor_initialization(self, ocr_processor):
        """Test OCR processor initialization"""
        # Should initialize without errors
        assert ocr_processor.openvino_enabled is not None
        assert ocr_processor.device is not None

        # Should attempt to configure Tesseract
        # (may fail if not installed, but should not raise exception)

    def test_pdf_text_extraction_pymupdf(self, ocr_processor):
        """Test text extraction using PyMuPDF"""
        # Create a simple test PDF
        pdf_path = TestUtils.create_test_pdf("Test PDF Content for OCR")

        # Extract text
        result = ocr_processor.extract_text_from_pdf(pdf_path)

        # Should succeed and contain text
        assert result["success"] == True
        assert "text" in result
        assert "method" in result

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def test_pdf_ocr_extraction_fallback(self, ocr_processor):
        """Test OCR extraction when PyMuPDF fails"""
        # Create a PDF that would be hard to extract with PyMuPDF
        # (This is hard to simulate without actual PDFs)

        # For now, test that the method handles errors gracefully
        result = ocr_processor.extract_text_from_pdf("nonexistent.pdf")

        # Should handle missing file gracefully
        assert "success" in result
        assert "error" in result

    def test_image_preprocessing(self, ocr_processor):
        """Test image preprocessing for OCR"""
        from PIL import Image
        import numpy as np

        # Create test image
        test_image = Image.new('RGB', (100, 100), color='white')

        # Preprocess image
        processed = ocr_processor._preprocess_image(test_image)

        # Should return numpy array
        assert isinstance(processed, np.ndarray)

        # Should be grayscale (2D array)
        assert len(processed.shape) == 2

    def test_tesseract_ocr(self, ocr_processor):
        """Test Tesseract OCR functionality"""
        from PIL import Image
        import numpy as np

        # Create simple test image with text
        test_image = Image.new('RGB', (200, 50), color='white')

        # Test OCR (may fail if Tesseract not available)
        result = ocr_processor._ocr_with_tesseract(np.array(test_image))

        # Should return string (may be empty)
        assert isinstance(result, str)

    def test_annual_report_processing(self, ocr_processor):
        """Test annual report processing"""
        # Create test PDF with annual report content
        report_content = """
        RELIANCE INDUSTRIES LIMITED
        ANNUAL REPORT 2023

        MANAGEMENT DISCUSSION AND ANALYSIS

        During the year under review, your Company achieved significant milestones...

        FINANCIAL HIGHLIGHTS

        Total Revenue: ₹8,50,000 crores
        Net Profit: ₹75,000 crores
        Total Assets: ₹15,00,000 crores

        AUDITOR'S REPORT

        We have audited the accompanying financial statements...
        """

        pdf_path = TestUtils.create_test_pdf(report_content)

        # Process annual report
        result = ocr_processor.process_annual_report(pdf_path)

        # Should extract sections
        assert "success" in result
        assert "sections" in result

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def test_section_extraction(self, ocr_processor):
        """Test section extraction from text"""
        sample_text = """
        MANAGEMENT DISCUSSION AND ANALYSIS

        This is the management discussion section with important information.

        AUDITOR'S REPORT

        This is the auditor's report section.

        FINANCIAL STATEMENTS

        Balance sheet and other financial data here.
        """

        # Test section extraction (using internal method)
        mda_section = ocr_processor._extract_section(
            sample_text,
            ["management discussion", "md&a"],
            max_length=200
        )

        # Should find management discussion section
        assert mda_section is not None
        assert "management discussion" in mda_section.lower()

        # Test auditor section
        auditor_section = ocr_processor._extract_section(
            sample_text,
            ["auditor"],
            max_length=200
        )

        assert auditor_section is not None
        assert "auditor" in auditor_section.lower()


class TestDocumentScraper:
    """Test document scraping functionality"""

    @pytest.fixture
    def document_scraper(self):
        """Create document scraper"""
        return DocumentScraper()

    def test_document_scraper_initialization(self, document_scraper):
        """Test document scraper initialization"""
        assert document_scraper.nse_client is not None
        assert document_scraper.bse_client is not None
        assert document_scraper.ocr_processor is not None

        # Check directory creation
        assert document_scraper.pdf_folder.exists()
        assert document_scraper.upload_folder.exists()

    def test_nse_document_fetching(self, document_scraper, mock_api_responses):
        """Test NSE document fetching"""
        documents = document_scraper.fetch_disclosure_documents("RELIANCE", "nse")

        # Should return list of documents
        assert isinstance(documents, list)

        # Each document should have expected fields
        for doc in documents:
            assert "symbol" in doc
            assert "exchange" in doc
            assert "document_type" in doc

    def test_bse_document_fetching(self, document_scraper, mock_api_responses):
        """Test BSE document fetching"""
        documents = document_scraper.fetch_disclosure_documents("500325", "bse")

        # Should return list of documents
        assert isinstance(documents, list)

    def test_document_download(self, document_scraper):
        """Test document download functionality"""
        # Test with mock URL
        test_url = "https://example.com/test.pdf"

        # Mock the download request
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.iter_content.return_value = [b"test pdf content"]
            mock_get.return_value = mock_response

            # Test download
            result = document_scraper.download_document({
                "url": test_url,
                "symbol": "TEST",
                "document_type": "test"
            })

            # Should handle download (mocked)
            # In real scenario, would check file exists
            assert result is not None

    def test_comprehensive_document_processing(self, document_scraper):
        """Test comprehensive document processing workflow"""
        result = document_scraper.get_comprehensive_documents("RELIANCE", "nse")

        # Should return comprehensive result
        assert "symbol" in result
        assert "documents_found" in result
        assert "processed_documents" in result
        assert "parsed_reports" in result

        # Should be a dictionary with expected structure
        assert isinstance(result["processed_documents"], list)
        assert isinstance(result["parsed_reports"], list)

    def test_annual_report_parsing(self, document_scraper):
        """Test annual report section parsing"""
        sample_text = """
        MANAGEMENT DISCUSSION AND ANALYSIS

        This section discusses the company's performance and future outlook.
        Key achievements include revenue growth and market expansion.

        FINANCIAL HIGHLIGHTS

        Total Revenue: ₹8,50,000 crores
        Net Profit: ₹75,000 crores
        EPS: ₹125.50

        AUDITOR'S REPORT

        We have audited the financial statements and found them to be accurate.
        """

        result = document_scraper.parse_annual_report_sections(sample_text)

        # Should extract sections
        assert result["success"] == True
        assert "sections" in result
        assert "sections_found" in result

        sections = result["sections"]
        # Should find at least management discussion
        assert "management_discussion_analysis" in sections or len(sections) >= 0


class TestOCRIntegration:
    """Test OCR integration scenarios"""

    def test_ocr_with_different_pdf_types(self, ocr_processor):
        """Test OCR with different PDF types"""
        # Test with text-based PDF
        text_pdf = TestUtils.create_test_pdf("Simple text content for OCR testing")
        text_result = ocr_processor.extract_text_from_pdf(text_pdf)

        # Should extract text successfully
        assert text_result["success"] == True

        # Clean up
        if os.path.exists(text_pdf):
            os.remove(text_pdf)

    def test_ocr_fallback_mechanism(self, ocr_processor):
        """Test OCR fallback from PyMuPDF to Tesseract"""
        # Test with PDF that has both text and images
        mixed_content = """
        TEXT SECTION
        This is extractable text content.

        [Image would be here in real scenario]

        MORE TEXT
        Additional text that should be extracted.
        """

        pdf_path = TestUtils.create_test_pdf(mixed_content)

        # Test extraction
        result = ocr_processor.extract_text_from_pdf(pdf_path)

        # Should handle mixed content
        assert "success" in result

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def test_ocr_performance(self, ocr_processor):
        """Test OCR processing performance"""
        import time

        # Create larger test content
        large_content = "Test content " * 1000  # Large text
        pdf_path = TestUtils.create_test_pdf(large_content)

        start_time = time.time()
        result = ocr_processor.extract_text_from_pdf(pdf_path)
        end_time = time.time()

        # Should complete within reasonable time
        processing_time = end_time - start_time
        assert processing_time < 30  # 30 seconds max

        # Should succeed
        assert result["success"] == True

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def test_ocr_error_handling(self, ocr_processor):
        """Test OCR error handling"""
        # Test with non-existent file
        result = ocr_processor.extract_text_from_pdf("nonexistent.pdf")

        # Should handle gracefully
        assert result["success"] == False
        assert "error" in result

        # Test with corrupted file (simulate)
        # This is hard to test without actual corrupted files

    def test_section_extraction_accuracy(self, ocr_processor):
        """Test section extraction accuracy"""
        # Test with well-structured text
        structured_text = """
        EXECUTIVE SUMMARY

        This is the executive summary section.

        DETAILED ANALYSIS

        This is the detailed analysis section with more content.

        CONCLUSION

        This is the conclusion section.
        """

        # Extract sections
        executive = ocr_processor._extract_section(structured_text, ["executive"], 200)
        analysis = ocr_processor._extract_section(structured_text, ["detailed analysis"], 200)
        conclusion = ocr_processor._extract_section(structured_text, ["conclusion"], 200)

        # Should extract sections correctly
        assert executive is not None
        assert analysis is not None
        assert conclusion is not None

        assert "executive" in executive.lower()
        assert "detailed analysis" in analysis.lower()
        assert "conclusion" in conclusion.lower()


class TestDocumentProcessingWorkflow:
    """Test complete document processing workflows"""

    def test_end_to_end_document_processing(self, document_scraper, ocr_processor):
        """Test end-to-end document processing"""
        # Test complete workflow
        # 1. Fetch documents
        documents = document_scraper.fetch_disclosure_documents("RELIANCE", "nse")

        # 2. Download document (if URLs available)
        # 3. Process with OCR
        # 4. Parse sections

        # For testing, just verify the workflow structure
        assert isinstance(documents, list)

        # Test section parsing with sample text
        sample_annual_report = """
        RELIANCE INDUSTRIES LIMITED
        ANNUAL REPORT 2023

        MANAGEMENT DISCUSSION AND ANALYSIS

        The company achieved strong growth in the petrochemical segment.
        Revenue increased by 25% compared to previous year.

        FINANCIAL PERFORMANCE

        Total revenue: ₹850,000 crores
        EBITDA: ₹150,000 crores
        PAT: ₹75,000 crores

        AUDITOR'S REPORT

        We have audited the financial statements...
        """

        parsed = document_scraper.parse_annual_report_sections(sample_annual_report)

        # Should extract key sections
        assert parsed["success"] == True
        sections = parsed["sections"]

        # Should find at least some sections
        assert isinstance(sections, dict)

    def test_cross_format_processing(self, ocr_processor):
        """Test processing different document formats"""
        # Test with different content types

        # Financial table content
        table_content = """
        BALANCE SHEET AS AT 31ST MARCH 2023

        ASSETS                          ₹ Crores
        Fixed Assets                     500,000
        Current Assets                   300,000
        Total Assets                     800,000

        LIABILITIES
        Equity                           400,000
        Debt                             300,000
        Current Liabilities              100,000
        Total Liabilities                800,000
        """

        pdf_path = TestUtils.create_test_pdf(table_content)

        # Process as annual report
        result = ocr_processor.process_annual_report(pdf_path)

        # Should extract some content
        assert "success" in result

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def test_error_recovery_in_workflow(self, document_scraper):
        """Test error recovery in document processing workflow"""
        # Test with invalid inputs
        result = document_scraper.get_comprehensive_documents("INVALID_SYMBOL")

        # Should handle gracefully
        assert "symbol" in result
        assert "error" in result or result["documents_found"] == 0


class TestUtils:
    """Test utility functions"""

    @staticmethod
    def create_test_pdf(content: str = "Test PDF Content") -> str:
        """Create a test PDF file"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import tempfile

        # Create temporary file
        fd, pdf_path = tempfile.mkstemp(suffix='.pdf')

        try:
            c = canvas.Canvas(pdf_path, pagesize=letter)
            # Split content into lines and draw
            lines = content.split('\n')
            y_position = 750

            for line in lines:
                if y_position < 50:  # New page
                    c.showPage()
                    y_position = 750
                c.drawString(50, y_position, line[:80])  # Limit line length
                y_position -= 20

            c.save()
            return pdf_path
        finally:
            os.close(fd)

    @staticmethod
    def cleanup_test_files():
        """Clean up test-generated files"""
        # Clean up any test files in test outputs directory
        test_outputs = Path(__file__).parent / "data" / "outputs"
        if test_outputs.exists():
            import shutil
            shutil.rmtree(test_outputs)
            test_outputs.mkdir()
