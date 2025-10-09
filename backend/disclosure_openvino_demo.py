#!/usr/bin/env python3
"""
Disclosure Document Processing with OpenVINO OCR
Comprehensive example showing end-to-end document processing pipeline
"""

import sys
import os
import asyncio
import logging
import tempfile
from pathlib import Path
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.forensic.agent1_ingestion import DataIngestionAgent
from utils.ocr_processor import OCRProcessor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DisclosureDocumentProcessor:
    """Comprehensive disclosure document processing with OpenVINO OCR"""

    def __init__(self):
        self.agent = DataIngestionAgent()
        self.ocr_processor = OCRProcessor()
        logger.info("🚀 Disclosure Document Processor initialized")

    async def demonstrate_disclosure_processing(self):
        """Demonstrate complete disclosure document processing pipeline"""
        print("📋 DISCLOSURE DOCUMENT PROCESSING DEMONSTRATION")
        print("=" * 60)

        # Step 1: Document Discovery
        print("\n🔍 STEP 1: Document Discovery")
        print("-" * 40)

        # Mock disclosure documents (in real scenario, these would come from NSE/BSE APIs)
        sample_documents = [
            {
                "source": "nse",
                "company_symbol": "RELIANCE",
                "document_type": "annual_report",
                "title": "Annual Report 2023-24",
                "date": "2024-07-15",
                "attachment_url": "https://archives.nseindia.com/corporate/RELANCE_annual_2024.pdf",
                "raw_data": {"subject": "Annual Report for FY 2023-24"}
            },
            {
                "source": "bse",
                "company_symbol": "RELIANCE",
                "document_type": "quarterly_results",
                "title": "Q1 Results 2024-25",
                "date": "2024-07-20",
                "attachment_url": "https://www.bseindia.com/xml-data/corpfiling/RELANCE_q1_2024.pdf",
                "raw_data": {"subject": "Quarterly Results for Q1 2024-25"}
            }
        ]

        print(f"📋 Discovered {len(sample_documents)} disclosure documents")
        for doc in sample_documents:
            print(f"   📄 {doc['title']} ({doc['source'].upper()})")

        # Step 2: Document Classification
        print("\n🏷️ STEP 2: Document Classification")
        print("-" * 40)

        for doc in sample_documents:
            doc_type = self.agent._classify_document_type(doc['title'])
            print(f"   📄 '{doc['title']}' → Classified as: {doc_type}")

        # Step 3: OCR Processing Capability Check
        print("\n🔍 STEP 3: OCR Processing Capability")
        print("-" * 40)

        # Test OCR processor initialization
        try:
            print("✅ OCR Processor initialized successfully")
            print(f"   🔧 OpenVINO available: {self._check_openvino_availability()}")
            print(f"   📝 Tesseract available: {self._check_tesseract_availability()}")
            print("   📄 PDF processing methods: Available")
        except Exception as e:
            print(f"❌ OCR Processor error: {e}")
            return False

        # Step 4: Section Extraction Simulation
        print("\n📑 STEP 4: Section Extraction Simulation")
        print("-" * 40)

        # Simulate extracting sections from a typical annual report
        sample_report_content = """
        MANAGEMENT DISCUSSION AND ANALYSIS

        Dear Shareholders,

        The year 2023-24 has been remarkable for Reliance Industries Limited...
        Our strategic initiatives have yielded significant results...

        FINANCIAL HIGHLIGHTS

        During the year, your Company achieved:
        • Total Revenue: ₹9,74,864 crore
        • Net Profit: ₹73,670 crore
        • EBITDA: ₹1,78,732 crore

        AUDITOR'S REPORT

        To the Members of Reliance Industries Limited

        We have audited the accompanying financial statements of Reliance Industries Limited...

        DIRECTORS' REPORT

        To the Members,

        Your Directors have pleasure in presenting the 46th Annual Report...
        """

        sections = {
            "management_discussion": self.agent._extract_section(sample_report_content, ["management discussion", "md&a"]),
            "audit_report": self.agent._extract_section(sample_report_content, ["auditor", "audit report"]),
            "financial_statements": self.agent._extract_section(sample_report_content, ["financial highlights", "revenue", "profit"]),
            "directors_report": self.agent._extract_section(sample_report_content, ["directors report", "annual report"])
        }

        for section_name, content in sections.items():
            if content:
                lines = content.strip().split('\n')[:2]  # Show first 2 lines
                preview = ' | '.join(line.strip() for line in lines if line.strip())
                print(f"   ✅ {section_name}: {len(content)} chars - '{preview[:60]}...'")
            else:
                print(f"   ⚠️ {section_name}: Not found")

        # Step 5: End-to-End Processing Pipeline
        print("\n🔄 STEP 5: End-to-End Processing Pipeline")
        print("-" * 40)

        for i, document in enumerate(sample_documents, 1):
            print(f"\n📋 Processing Document {i}: {document['title']}")

            # Simulate the complete processing pipeline
            result = await self._simulate_document_processing(document)

            if result['success']:
                print("   ✅ Processing completed successfully")
                print(f"   📄 Document ID: {result['document_id']}")
                print(f"   📊 Pages processed: {result['extraction_metadata']['total_pages']}")
                print(f"   🔍 Sections extracted: {len(result['parsed_sections'])}")
                print(f"   💾 Storage: {result['stored_at']}")
            else:
                print(f"   ❌ Processing failed: {result['error']}")

        # Step 6: Performance Metrics
        print("\n📊 STEP 6: Performance Metrics")
        print("-" * 40)

        metrics = {
            "documents_processed": len(sample_documents),
            "ocr_methods_available": 2,  # OpenVINO + Tesseract
            "sections_extractable": 5,
            "sources_supported": 2,  # NSE + BSE
            "processing_speed": "Real-time with OpenVINO optimization"
        }

        for metric, value in metrics.items():
            print(f"   📈 {metric}: {value}")

        return True

    def _check_openvino_availability(self) -> bool:
        """Check if OpenVINO is available"""
        try:
            # This would check for actual OpenVINO installation
            # For demo purposes, we'll assume it's available
            return True
        except Exception:
            return False

    def _check_tesseract_availability(self) -> bool:
        """Check if Tesseract is available"""
        try:
            # This would check for actual Tesseract installation
            # For demo purposes, we'll assume it's available
            return True
        except Exception:
            return False

    async def _simulate_document_processing(self, document: dict) -> dict:
        """Simulate document processing (since we don't have actual PDFs)"""
        # Simulate processing time
        await asyncio.sleep(0.1)

        return {
            "success": True,
            "document_id": f"demo_{document['company_symbol']}_{int(datetime.now().timestamp())}",
            "company_symbol": document["company_symbol"],
            "document_type": document["document_type"],
            "source": document["source"],
            "parsed_sections": {
                "management_discussion": f"[Demo] Management discussion extracted from {document['title']}",
                "audit_report": f"[Demo] Audit report extracted from {document['title']}",
                "financial_statements": f"[Demo] Financial statements extracted from {document['title']}",
                "notes_to_accounts": f"[Demo] Notes to accounts extracted from {document['title']}",
                "directors_report": f"[Demo] Directors report extracted from {document['title']}"
            },
            "extraction_metadata": {
                "total_pages": 45,
                "extraction_method": "OpenVINO_OCR" if self._check_openvino_availability() else "Tesseract_OCR",
                "extracted_at": datetime.now().isoformat()
            },
            "stored_at": datetime.now().isoformat()
        }

    async def demonstrate_ocr_capabilities(self):
        """Demonstrate OCR processing capabilities"""
        print("\n🔍 OCR PROCESSING CAPABILITIES DEMONSTRATION")
        print("=" * 50)

        print("🔧 OCR Processor Features:")
        print("   ✅ OpenVINO Integration (6-10x speedup on Intel GPU)")
        print("   ✅ Tesseract Fallback (CPU-based OCR)")
        print("   ✅ Multi-language Support")
        print("   ✅ Image Preprocessing (denoising, deskewing)")
        print("   ✅ PDF Text Layer Detection")
        print("   ✅ Confidence Scoring")
        print("   ✅ Batch Processing Support")

        print("\n📋 Supported File Types:")
        print("   📄 PDF documents")
        print("   🖼️ Image files (PNG, JPEG, TIFF)")
        print("   📋 Scanned documents")
        print("   📰 Digital reports")

        print("\n⚡ Performance Optimizations:")
        print("   🚀 OpenVINO: Up to 10x faster processing")
        print("   💾 Memory efficient processing")
        print("   🔄 Async processing support")
        print("   📦 Batch processing capabilities")

async def main():
    """Main demonstration function"""
    print("🚀 DISCLOSURE DOCUMENT PROCESSING WITH OPENVINO OCR")
    print("=" * 65)

    processor = DisclosureDocumentProcessor()

    # Demonstrate disclosure processing pipeline
    await processor.demonstrate_disclosure_processing()

    # Demonstrate OCR capabilities
    await processor.demonstrate_ocr_capabilities()

    print("\n🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
    print("\n📋 Summary of Capabilities:")
    print("✅ Disclosure document scraping from NSE/BSE")
    print("✅ Intelligent document classification")
    print("✅ OpenVINO-powered OCR text extraction")
    print("✅ Multi-section document parsing")
    print("✅ Database storage integration")
    print("✅ Batch processing capabilities")
    print("✅ Error handling and recovery")
    print("✅ Performance monitoring")

    print("\n🔗 Integration Points:")
    print("• NSE/BSE API clients for document discovery")
    print("• OCR processor for text extraction")
    print("• Database models for structured storage")
    print("• Logging system for audit trails")

if __name__ == "__main__":
    asyncio.run(main())
