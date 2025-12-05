import PyPDF2
from typing import List, Dict, Any
import os
from .base import BaseConnector

class PDFConnector(BaseConnector):
    """Connector for ingesting PDF files"""

    def ingest(self, source: str) -> List[Dict[str, Any]]:
        """
        Extract text from a PDF file.
        
        Args:
            source: Path to the PDF file
            
        Returns:
            List of documents, one per page
        """
        if not os.path.exists(source):
            raise FileNotFoundError(f"PDF file not found: {source}")
            
        documents = []
        
        try:
            with open(source, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        documents.append({
                            'text': text,
                            'metadata': {
                                'source': os.path.basename(source),
                                'page': i + 1,
                                'type': 'pdf'
                            }
                        })
                        
            return documents
        except Exception as e:
            raise Exception(f"Failed to process PDF: {str(e)}")
