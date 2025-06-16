from fpdf import FPDF

def create_pdf_report(results):
    """
    results: dict of
        filename -> (severity_classification, severity_percentage, precaution_text)
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Crop Health Disease Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)

    for filename, (severity, percent, precautions) in results.items():
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Image: {filename}", ln=True)

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, f"Severity Classification: {severity}", ln=True)
        pdf.cell(0, 8, f"Severity Percentage: {percent:.2f}%", ln=True)
        pdf.multi_cell(0, 8, f"Precautions/Measures:\n{precautions}")
        pdf.ln(5)

    output_path = "output/crop_health_report.pdf"
    pdf.output(output_path)
    return output_path
