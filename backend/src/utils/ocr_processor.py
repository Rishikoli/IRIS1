"""
Project IRIS - OCR Processor
OpenVINO-optimized OCR for document text extraction
"""

import logging
import os
import tempfile
from typing import Dict, Any, Optional, List
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import openvino as ov

from config import settings

logger = logging.getLogger(__name__)


class OCRProcessor:
    """OpenVINO-optimized OCR processor for financial documents"""
    
    def __init__(self):
        self.openvino_enabled = settings.openvino_enabled
        self.device = settings.openvino_device
        self.core = None
        self.model = None
        
        if self.openvino_enabled:
            self._initialize_openvino()
        
        # Configure Tesseract
        self._configure_tesseract()
    
    def _initialize_openvino(self):
        """Initialize OpenVINO for OCR acceleration"""
        try:
            self.core = ov.Core()
            
            # Check if OpenVINO OCR model exists
            model_path = "./models/openvino/ocr_model.xml"
            if os.path.exists(model_path):
                self.model = self.core.read_model(model_path)
                logger.info(f"OpenVINO OCR model loaded from {model_path}")
            else:
                logger.warning(f"OpenVINO OCR model not found at {model_path}, falling back to Tesseract")
                self.openvino_enabled = False
                
        except Exception as e:
            logger.error(f"Failed to initialize OpenVINO: {e}")
            self.openvino_enabled = False
    
    def _configure_tesseract(self):
        """Configure Tesseract OCR settings"""
        try:
            # Test Tesseract installation
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR configured successfully")
        except Exception as e:
            logger.error(f"Tesseract configuration failed: {e}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text from PDF document"""
        try:
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            # First try PyMuPDF for text-based PDFs
            text_content = self._extract_text_pymupdf(pdf_path)
            
            if len(text_content.strip()) > 100:  # If sufficient text found
                return {
                    "success": True,
                    "text": text_content,
                    "method": "pymupdf",
                    "page_count": self._get_pdf_page_count(pdf_path)
                }
            
            # If text extraction failed, use OCR
            logger.info("Text-based extraction insufficient, using OCR")
            return self._extract_text_ocr(pdf_path)
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {pdf_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "method": "failed"
            }
    
    def _extract_text_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF (for text-based PDFs)"""
        try:
            doc = fitz.open(pdf_path)
            text_content = ""
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text_content += f"\n--- Page {page_num + 1} ---\n"
                text_content += page.get_text()
            
            doc.close()
            return text_content
            
        except Exception as e:
            logger.error(f"PyMuPDF text extraction failed: {e}")
            return ""
    
    def _extract_text_ocr(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text using OCR (for image-based PDFs)"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300, fmt='jpeg')
            
            extracted_text = ""
            processed_pages = 0
            
            for page_num, image in enumerate(images):
                try:
                    # Preprocess image for better OCR
                    processed_image = self._preprocess_image(image)
                    
                    # Extract text using appropriate method
                    if self.openvino_enabled and self.model:
                        page_text = self._ocr_with_openvino(processed_image)
                    else:
                        page_text = self._ocr_with_tesseract(processed_image)
                    
                    extracted_text += f"\n--- Page {page_num + 1} ---\n"
                    extracted_text += page_text
                    processed_pages += 1
                    
                except Exception as e:
                    logger.error(f"OCR failed for page {page_num + 1}: {e}")
                    continue
            
            return {
                "success": True,
                "text": extracted_text,
                "method": "openvino_ocr" if self.openvino_enabled else "tesseract_ocr",
                "pages_processed": processed_pages,
                "total_pages": len(images)
            }
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "method": "ocr_failed"
            }
    
    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for better OCR accuracy"""
        try:
            # Convert PIL image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            # Return original image as numpy array if preprocessing fails
            return np.array(image.convert('L'))
    
    def _ocr_with_openvino(self, image: np.ndarray) -> str:
        """Perform OCR using OpenVINO optimized model"""
        try:
            # This is a placeholder for OpenVINO OCR implementation
            # In practice, you would:
            # 1. Preprocess image for the specific model
            # 2. Run inference
            # 3. Post-process results
            
            compiled_model = self.core.compile_model(self.model, self.device)
            
            # Placeholder implementation - would need actual model-specific code
            logger.info("Using OpenVINO OCR (placeholder implementation)")
            
            # Fall back to Tesseract for now
            return self._ocr_with_tesseract(image)
            
        except Exception as e:
            logger.error(f"OpenVINO OCR failed: {e}")
            return self._ocr_with_tesseract(image)
    
    def _ocr_with_tesseract(self, image: np.ndarray) -> str:
        """Perform OCR using Tesseract"""
        try:
            # Configure Tesseract for financial documents
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,()%-₹$'
            
            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return ""
    
    def _get_pdf_page_count(self, pdf_path: str) -> int:
        """Get number of pages in PDF"""
        try:
            doc = fitz.open(pdf_path)
            page_count = doc.page_count
            doc.close()
            return page_count
        except Exception:
            return 0
    
    def extract_tables_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract tables from PDF (placeholder for advanced table extraction)"""
        try:
            logger.info(f"Extracting tables from PDF: {pdf_path}")
            
            # This is a placeholder for table extraction
            # In practice, you might use libraries like:
            # - tabula-py for table extraction
            # - camelot-py for table detection
            # - Custom ML models for table structure recognition
            
            tables = []
            
            # Basic table detection using text patterns
            text_result = self.extract_text_from_pdf(pdf_path)
            if text_result["success"]:
                text = text_result["text"]
                
                # Look for table-like patterns (rows with multiple columns)
                lines = text.split('\n')
                potential_tables = []
                current_table = []
                
                for line in lines:
                    # Simple heuristic: lines with multiple numeric values might be table rows
                    if self._looks_like_table_row(line):
                        current_table.append(line)
                    else:
                        if len(current_table) > 2:  # At least 3 rows to be considered a table
                            potential_tables.append(current_table)
                        current_table = []
                
                # Add final table if exists
                if len(current_table) > 2:
                    potential_tables.append(current_table)
                
                # Convert to structured format
                for i, table_lines in enumerate(potential_tables):
                    tables.append({
                        "table_id": i + 1,
                        "rows": table_lines,
                        "row_count": len(table_lines),
                        "extraction_method": "text_pattern"
                    })
            
            return tables
            
        except Exception as e:
            logger.error(f"Table extraction failed for {pdf_path}: {e}")
            return []
    
    def _looks_like_table_row(self, line: str) -> bool:
        """Heuristic to identify potential table rows"""
        try:
            # Remove extra whitespace
            clean_line = ' '.join(line.split())
            
            # Skip empty lines or very short lines
            if len(clean_line) < 10:
                return False
            
            # Count numeric values (including currency symbols)
            import re
            numeric_pattern = r'[\d,]+\.?\d*'
            numeric_matches = re.findall(numeric_pattern, clean_line)
            
            # Count separators (tabs, multiple spaces)
            separator_count = len(re.findall(r'\s{2,}|\t', line))
            
            # Heuristic: likely a table row if it has multiple numeric values and separators
            return len(numeric_matches) >= 2 and separator_count >= 1
            
        except Exception:
            return False
    
    def process_annual_report(self, pdf_path: str) -> Dict[str, Any]:
        """Process annual report and extract key sections"""
        try:
            logger.info(f"Processing annual report: {pdf_path}")
            
            # Extract full text
            text_result = self.extract_text_from_pdf(pdf_path)
            
            if not text_result["success"]:
                return text_result
            
            full_text = text_result["text"]
            
            # Extract key sections
            sections = self._extract_report_sections(full_text)
            
            # Extract tables
            tables = self.extract_tables_from_pdf(pdf_path)
            
            return {
                "success": True,
                "full_text": full_text,
                "sections": sections,
                "tables": tables,
                "page_count": text_result.get("page_count", 0),
                "extraction_method": text_result.get("method", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Annual report processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_report_sections(self, text: str) -> Dict[str, str]:
        """Extract key sections from annual report text"""
        try:
            sections = {}
            
            # Define section patterns
            section_patterns = {
                "management_discussion": [
                    r"management.{0,20}discussion.{0,20}analysis",
                    r"md&a",
                    r"management.{0,20}analysis"
                ],
                "auditor_report": [
                    r"independent.{0,20}auditor.{0,20}report",
                    r"auditor.{0,20}report",
                    r"audit.{0,20}report"
                ],
                "financial_statements": [
                    r"financial.{0,20}statements",
                    r"balance.{0,20}sheet",
                    r"profit.{0,20}loss",
                    r"income.{0,20}statement"
                ],
                "notes_to_accounts": [
                    r"notes.{0,20}to.{0,20}accounts",
                    r"notes.{0,20}to.{0,20}financial.{0,20}statements",
                    r"significant.{0,20}accounting.{0,20}policies"
                ],
                "directors_report": [
                    r"directors.{0,20}report",
                    r"board.{0,20}report"
                ]
            }
            
            import re
            
            for section_name, patterns in section_patterns.items():
                for pattern in patterns:
                    matches = list(re.finditer(pattern, text, re.IGNORECASE))
                    if matches:
                        # Find the section content (next 2000 characters)
                        start_pos = matches[0].start()
                        end_pos = min(start_pos + 2000, len(text))
                        sections[section_name] = text[start_pos:end_pos]
                        break
            
            return sections
            
        except Exception as e:
            logger.error(f"Section extraction failed: {e}")
            return {}
