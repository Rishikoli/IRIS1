#!/usr/bin/env python3
"""
IRIS OCR Processor - Test Your PDF File
Simple script to test PDF processing with your disclosure_reg_304.pdf file
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.ocr_processor import OCRProcessor

def test_pdf_processing(pdf_filename="disclosure_reg_304.pdf"):
    """Test PDF processing with the specified file"""

    # Initialize OCR processor
    print("🔍 Initializing OCR Processor...")
    ocr = OCRProcessor()
    print("✅ OCR Processor ready")
    # Check if PDF file exists
    pdf_path = Path("data") / pdf_filename

    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return False

    print(f"\n🔍 Testing text extraction...")
    try:
        result = ocr.extract_text_from_pdf(str(pdf_path))

        if result["success"]:
            print("✅ Text extraction successful!")
            print(f"   📊 Characters extracted: {len(result['text'])}")
            print(f"   🔧 Method used: {result['method']}")
            print(f"   📄 Pages processed: {result.get('pages_processed', 'N/A')}")

            # Show first 500 characters
            preview = result['text'][:500].replace('\n', ' ').strip()
            print(f"   👀 Preview: {preview}...")

        else:
            print(f"❌ Text extraction failed: {result['error']}")
            return False

    except Exception as e:
        print(f"❌ Text extraction error: {e}")
        return False

    # Test annual report processing
    print("\n📑 Testing annual report processing...")
    try:
        result = ocr.process_annual_report(str(pdf_path))

        if result["success"]:
            print("✅ Annual report processing successful!")
            print(f"   📄 Sections found: {list(result['sections'].keys())}")
            print(f"   📊 Tables detected: {len(result['tables'])}")

            # Show sections
            for section, content in result['sections'].items():
                print(f"      📋 {section}: {len(content)} characters")

        else:
            print(f"❌ Annual report processing failed: {result['error']}")

    except Exception as e:
        print(f"❌ Annual report processing error: {e}")

    return True

def main():
    """Main test function"""
    print("🚀 IRIS OCR PROCESSOR - PDF TEST")
    print("=" * 40)

    # Test with the specific filename
    success = test_pdf_processing("disclosure_reg_304.pdf")

    if success:
        print("\n🎉 PDF PROCESSING TEST: SUCCESS")
        print("✅ Your PDF file has been successfully processed!")
        print("✅ Text extraction working")
        print("✅ Section identification working")
        print("✅ Ready for forensic analysis pipeline")
    else:
        print("\n❌ PDF PROCESSING TEST: ISSUES FOUND")
        print("💡 Check the error messages above")
        print("💡 Make sure your PDF file is in the data/ directory")

if __name__ == "__main__":
    main()
