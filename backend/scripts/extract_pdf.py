import PyPDF2
import sys

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += f"--- Page {page_num + 1} ---\n"
            text += page.extract_text() + "\n\n"
        return text

if __name__ == "__main__":
    path = "reserach_paper (2).pdf"
    if len(sys.argv) > 1:
        path = sys.argv[1]
    
    try:
        content = extract_text_from_pdf(path)
        print(content)
    except Exception as e:
        print(f"Error: {e}")
