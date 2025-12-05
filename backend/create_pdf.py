from reportlab.pdfgen import canvas

def create_sample_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "Financial Report 2024")
    c.drawString(100, 730, "Company: Test Corp")
    c.drawString(100, 710, "Revenue: $1,000,000")
    c.drawString(100, 690, "Profit: $200,000")
    c.save()

if __name__ == "__main__":
    create_sample_pdf("sample_report.pdf")
