"""
PDF Processor for Annual Reports

Extracts text from company annual reports and investor presentations (PDFs)
and processes them for sentiment analysis training data.
"""

import PyPDF2
import pdfplumber
import pandas as pd
from pathlib import Path
from typing import List, Dict
import logging
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process financial PDFs to extract relevant text"""
    
    def __init__(self, input_dir: str = "data/raw/pdfs", output_dir: str = "data/raw/reports"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text_pypdf2(self, pdf_path: Path) -> str:
        """Extract text using PyPDF2"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = []
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
                
                return '\n'.join(text)
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed for {pdf_path}: {e}")
            return ""
    
    def extract_text_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber (more accurate)"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = []
                
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
                
                return '\n'.join(text)
        except Exception as e:
            logger.error(f"pdfplumber extraction failed for {pdf_path}: {e}")
            return ""
    
    def extract_text(self, pdf_path: Path) -> str:
        """Extract text with fallback mechanism"""
        # Try pdfplumber first (more accurate)
        text = self.extract_text_pdfplumber(pdf_path)
        
        # Fallback to PyPDF2 if pdfplumber fails
        if not text or len(text) < 100:
            logger.info(f"Falling back to PyPDF2 for {pdf_path.name}")
            text = self.extract_text_pypdf2(pdf_path)
        
        return text
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract key sections from annual report
        
        Returns:
            Dictionary with section names and content
        """
        sections = {}
        
        # Define section patterns
        section_patterns = {
            'management_discussion': r'(?:management.*?discussion|md\&a)',
            'risk_factors': r'risk\s+factors?',
            'financial_performance': r'financial\s+performance',
            'outlook': r'(?:future\s+outlook|prospects)',
            'directors_report': r'directors?\s+report',
            'governance': r'corporate\s+governance'
        }
        
        text_lower = text.lower()
        
        for section_name, pattern in section_patterns.items():
            try:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    start_idx = match.start()
                    
                    # Find next section or take next 3000 chars
                    end_idx = start_idx + 3000
                    
                    section_text = text[start_idx:end_idx]
                    sections[section_name] = section_text
                    
            except Exception as e:
                logger.warning(f"Failed to extract {section_name}: {e}")
                continue
        
        return sections
    
    def split_into_sentences(self, text: str, min_length: int = 20, max_length: int = 500) -> List[str]:
        """
        Split text into sentences suitable for sentiment analysis
        
        Args:
            text: Input text
            min_length: Minimum sentence length
            max_length: Maximum sentence length
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting
        sentences = re.split(r'[.!?]\s+', text)
        
        # Filter by length
        filtered = [
            s.strip() for s in sentences 
            if min_length <= len(s.strip()) <= max_length
        ]
        
        return filtered
    
    def process_pdf(self, pdf_path: Path, company_name: str = None) -> pd.DataFrame:
        """
        Process a single PDF and extract training data
        
        Args:
            pdf_path: Path to PDF file
            company_name: Name of the company (optional)
            
        Returns:
            DataFrame with extracted sentences
        """
        logger.info(f"Processing {pdf_path.name}...")
        
        # Extract company name from filename if not provided
        if not company_name:
            company_name = pdf_path.stem.split('_')[0]
        
        # Extract text
        full_text = self.extract_text(pdf_path)
        
        if not full_text:
            logger.warning(f"No text extracted from {pdf_path.name}")
            return pd.DataFrame()
        
        # Extract sections
        sections = self.extract_sections(full_text)
        
        # Process each section
        data = []
        
        for section_name, section_text in sections.items():
            sentences = self.split_into_sentences(section_text)
            
            for sentence in sentences:
                data.append({
                    'text': sentence,
                    'title': f"{company_name} - {section_name}",
                    'company': company_name,
                    'section': section_name,
                    'source': 'Annual Report',
                    'file': pdf_path.name,
                    'label': 'neutral'  # Needs manual labeling
                })
        
        # If no sections found, process full text
        if not sections:
            logger.info(f"No sections found, processing full text for {pdf_path.name}")
            sentences = self.split_into_sentences(full_text[:10000])  # First 10k chars
            
            for sentence in sentences:
                data.append({
                    'text': sentence,
                    'title': f"{company_name} - Annual Report",
                    'company': company_name,
                    'section': 'general',
                    'source': 'Annual Report',
                    'file': pdf_path.name,
                    'label': 'neutral'
                })
        
        df = pd.DataFrame(data)
        logger.info(f"Extracted {len(df)} sentences from {pdf_path.name}")
        
        return df
    
    def process_directory(self, pattern: str = "*.pdf") -> pd.DataFrame:
        """
        Process all PDFs in the input directory
        
        Args:
            pattern: File pattern to match
            
        Returns:
            Combined DataFrame from all PDFs
        """
        logger.info(f"Processing PDFs from {self.input_dir}...")
        
        pdf_files = list(self.input_dir.glob(pattern))
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        all_data = []
        
        for pdf_path in pdf_files:
            try:
                df = self.process_pdf(pdf_path)
                if not df.empty:
                    all_data.append(df)
            except Exception as e:
                logger.error(f"Failed to process {pdf_path.name}: {e}")
                continue
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Remove duplicates
            combined_df = combined_df.drop_duplicates(subset=['text'])
            
            # Save
            output_file = self.output_dir / f"reports_extracted_{datetime.now().strftime('%Y%m%d')}.csv"
            combined_df.to_csv(output_file, index=False)
            logger.info(f"Saved {len(combined_df)} sentences to {output_file}")
            
            return combined_df
        else:
            logger.warning("No data extracted from any PDF")
            return pd.DataFrame()
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers
        text = re.sub(r'\b(?:page|pg\.?)\s*\d+\b', '', text, flags=re.IGNORECASE)
        
        # Remove common PDF artifacts
        text = re.sub(r'(?:annual\s+report|financial\s+statements)\s+\d{4}', '', text, flags=re.IGNORECASE)
        
        return text.strip()


if __name__ == "__main__":
    # Example usage
    processor = PDFProcessor()
    
    # Process all PDFs in the directory
    df = processor.process_directory()
    
    if not df.empty:
        print(f"\nProcessed {len(df)} sentences from PDFs")
        print(f"\nSource files:\n{df['file'].value_counts()}")
        print("\nSample data:")
        print(df[['company', 'section', 'text']].head())
    else:
        print("\nNo PDFs found. Place PDF files in data/raw/pdfs/")
