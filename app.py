import streamlit as st
import cv2
import numpy as np
import plotly.graph_objects as go  # type: ignore
from utils import detect_symptoms_and_severity
from pdf_report import create_pdf_report

# --- Helper Functions ---
def get_precautions(severity):
    tips = {
        "Healthy": "✅ No significant issues. Maintain proper watering, light, and nutrient balance.",
        "Low": "🌱 Minor symptoms. Use neem-based organic sprays and avoid overwatering.",
        "Moderate": "⚠️ Disease spreading. Isolate infected leaves and apply mild fungicide.",
        "Severe": "🚨 Major infection! Remove infected plants, use chemical treatment, consult an agronomist."
    }
    return tips.get(severity, "No precautions available.")

def get_symptom_tips(symptoms):
    tips = {
        "Yellowing": "🟡 Yellowing indicates nutrient deficiency or fungal stress. Improve soil nitrogen or use bio-fungicides.",
        "Holes": "🕳️ Holes are signs of pests. Use neem oil or insecticidal soap.",
        "Fungal Spots": "🔵 Circular spots signal fungal attack. Apply copper-based fungicide.",
        "Dried Edges": "🌾 Dried leaf edges may be due to heat stress or potassium deficiency. Improve watering and soil health."
    }
    return "\n".join([f"{s}: {tips.get(s, 'No advice available.')}" for s in symptoms])

def process_image(image):
    img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([10, 100, 100]), np.array([40, 255, 255]))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    area = sum(cv2.contourArea(c) for c in contours)
    total = img.shape[0] * img.shape[1]
    severity_percent = (area / total) * 100 if total > 0 else 0

    result = detect_symptoms_and_severity(img, severity_percent)
    severity = result["severity"]
    symptoms = result["symptoms"]
    cv2.drawContours(img, contours, -1, (0, 0, 255), 2)
    cv2.putText(img, f"Severity: {severity}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    return img, severity, severity_percent, symptoms, mask

def create_3d_surface_from_mask(mask):
    z = mask.astype(np.float32)
    z = (z - z.min()) / (z.max() - z.min() + 1e-6) * 50
    x = np.arange(z.shape[1])
    y = np.arange(z.shape[0])
    fig = go.Figure(data=[go.Surface(z=z, x=x, y=y, colorscale='Reds')])
    fig.update_layout(title="3D Disease Area Visualization",
                      scene=dict(zaxis_title='Severity Depth'))
    return fig

# --- Streamlit Config ---
st.set_page_config(
    page_title="Crop Health Detector",
    page_icon="🌿",
    layout="wide"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Lexend', sans-serif;
    }

    body {
        background-image: url("https://img.freepik.com/free-vector/green-agriculture-background-flat-design_23-2149423044.jpg");
        background-size: cover;
        background-attachment: fixed;
    }

    .title-gradient {
        background: linear-gradient(90deg, #00b09b, #96c93d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 52px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #444;
        margin-bottom: 30px;
    }

    .stButton>button {
        background: linear-gradient(to right, #56ab2f, #a8e063);
        border: none;
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
    }

    .stButton>button:hover {
        background: linear-gradient(to right, #a8e063, #56ab2f);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-gradient">🌿 Crop Health Detector</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered leaf disease detection and advisory system</div>', unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2909/2909642.png", width=110)

menu = st.sidebar.radio("Navigate", ["📁 Image Upload", "📄 PDF Report", "🌐 3D Visualization"])
st.sidebar.markdown("## 🌾 About")
st.sidebar.info("""
- Detects Yellowing, Holes, Fungal Spots, Dried Edges  
- Classifies Severity  
- Generates Reports  
- 3D Disease Visualization
""")

st.sidebar.markdown("## 👩‍💻 Developer")
st.sidebar.markdown("**Bhumika**\n📧 bhumikasindhakhed12@gmail.com")

# --- App Logic ---
results = {}
uploaded_file_refs = {}

if menu == "📁 Image Upload":
    uploaded_files = st.file_uploader("Upload leaf images (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.markdown(f"#### 🖼️ Processing: {uploaded_file.name}")
            img, severity, percent, symptoms, mask = process_image(uploaded_file)
            precautions = get_precautions(severity)
            tips = get_symptom_tips(symptoms)

            results[uploaded_file.name] = {
                "severity": severity,
                "severity_percent": percent,
                "precautions": precautions,
                "symptoms": symptoms
            }
            uploaded_file_refs[uploaded_file.name] = mask

            st.image(img[:, :, ::-1], caption=f"Analyzed: {uploaded_file.name}", use_container_width=True)
            st.markdown(f"""
                <h4 style='color:#2E7D32;'>🩺 <b>Severity: {severity}</b></h4>
                <h5 style='color:#F57C00;'>📊 Percentage: {percent:.2f}%</h5>
                <h5 style='color:#6A1B9A;'>🔬 Symptoms: {', '.join(symptoms) or "None"}</h5>
                <p><b>🛡️ General Advice:</b> {precautions}</p>
                <p><b>📘 Symptom-specific Tips:</b><br>{tips}</p>
            """, unsafe_allow_html=True)

            st.progress(min(int(percent), 100))
            st.markdown("---")
    else:
        st.warning("Please upload at least one image to begin analysis.")

elif menu == "📄 PDF Report":
    st.subheader("📄 Generate PDF Health Report")
    if results:
        if st.button("Generate PDF Report", key="pdf_button"):
            pdf_path = create_pdf_report(results)
            st.success("✅ PDF report generated successfully!")
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Download PDF", f, file_name="crop_health_report.pdf", mime="application/pdf")
    else:
        st.info("No results to report. Upload and analyze images first.")

elif menu == "🌐 3D Visualization":
    st.subheader("3D Visualization of Leaf Damage")
    if uploaded_file_refs:
        selected_img = st.selectbox("Select Image", list(uploaded_file_refs.keys()))
        fig = create_3d_surface_from_mask(uploaded_file_refs[selected_img])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Upload and analyze an image to view 3D plot.")

# --- Footer ---
st.markdown("""
---
<p style='text-align:center; color:gray; font-size:14px'>
🌿 Built with ❤️ by <b>Bhumika</b> | Powered by OpenCV + Streamlit + Plotly
</p>
""", unsafe_allow_html=True)
