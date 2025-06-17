import os
from fpdf import FPDF

def create_pdf_report(results):
    """
    Generate a PDF report summarizing crop health analysis results.

    Parameters:
        results (dict): 
            Keys are image filenames (str), values are dicts with keys like:
            - 'severity' (str)
            - 'severity_percent' (float)
            - 'precautions' (str)

    Returns:
        output_path (str): Path to the generated PDF file.
    """
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, "crop_health_report.pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Crop Health Disease Report", ln=True, align='C')
    pdf.ln(10)

    # For each image's results, add details
    pdf.set_font("Arial", size=12)

    for filename, data in results.items():
        severity = data.get("severity", "N/A")
        percent = data.get("severity_percent", 0.0)
        precautions = data.get("precautions", "No data available.")

        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Image: {filename}", ln=True)

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, f"Severity Classification: {severity}", ln=True)
        pdf.cell(0, 8, f"Severity Percentage: {percent:.2f}%", ln=True)
        pdf.multi_cell(0, 8, f"Precautions/Measures:\n{precautions}")
        pdf.ln(5)

    # Save PDF file
    pdf.output(output_path)

    return output_path
