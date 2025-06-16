import streamlit as st
import cv2
import numpy as np
from utils import classify_damage
from pdf_report import create_pdf_report

def get_precautions(severity):
    if severity == "Healthy":
        return "No significant issues detected. Maintain regular monitoring and good agricultural practices."
    elif severity == "Low":
        return "Minor signs of disease. Use organic pesticides and avoid excess watering."
    elif severity == "Moderate":
        return "Moderate infection detected. Apply recommended fungicides and remove affected leaves."
    elif severity == "Severe":
        return "Severe disease detected. Immediate action required: isolate plants, use chemical treatments, and consult an agronomist."
    else:
        return "No data available."

def process_image(image):
    img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower = np.array([10, 100, 100])
    upper = np.array([40, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img, contours, -1, (0, 0, 255), 2)

    area = sum(cv2.contourArea(c) for c in contours)
    total = img.shape[0] * img.shape[1]
    severity_percent = (area / total) * 100 if total > 0 else 0
    severity = classify_damage(severity_percent)

    cv2.putText(img, f"Severity: {severity}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    return img, severity, severity_percent

st.set_page_config(page_title="Crop Health Detector", page_icon="🌿", layout="centered")

st.title("🌿 Crop Health Detector")
st.write("Upload one or more leaf images to check disease severity percentage and classification.")

uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

results = {}

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.write(f"### Processing: {uploaded_file.name}")
        processed_img, severity, severity_percent = process_image(uploaded_file)
        precautions = get_precautions(severity)

        results[uploaded_file.name] = (severity, severity_percent, precautions)

        st.image(processed_img[:, :, ::-1], caption=f"Processed Image - {uploaded_file.name}", use_column_width=True)
        st.markdown(f"""
            <h4 style='color:green;'>Severity Classification: <b>{severity}</b></h4>
            <h5 style='color:orange;'>Severity Percentage: <b>{severity_percent:.2f}%</b></h5>
            <p><b>Precautions:</b> {precautions}</p>
        """, unsafe_allow_html=True)
        st.progress(min(int(severity_percent), 100))
        st.markdown("---")

    if st.button("Generate & Download PDF Report"):
        pdf_path = create_pdf_report(results)
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Download Report PDF",
                data=f,
                file_name="crop_health_report.pdf",
                mime="application/pdf"
            )
else:
    st.info("Please upload one or more leaf image files to get started.")
