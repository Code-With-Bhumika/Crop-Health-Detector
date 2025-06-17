import streamlit as st
import cv2
import numpy as np
import plotly.graph_objects as go # type: ignore
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
        font-size: 18px !important;
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
        font-size: 60px;
        font-weight: 800;
        text-align: center;
    }
    .subtitle {
        text-align: center;
        font-size: 22px;
        color: #2c2c2c;
        margin-bottom: 30px;
    }
    .stButton>button {
        background: linear-gradient(to right, #56ab2f, #a8e063);
        border: none;
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 18px;
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

st.sidebar.markdown("## 🌿 About the Project")
st.sidebar.markdown("""
<b>Crop Health Detector</b> is an AI-powered application designed to detect and classify diseases in crop leaves.

**Key Features:**
- 🔍 Detects symptoms like Yellowing, Holes, Fungal Spots, and Dried Edges.
- 📈 Classifies severity as Healthy, Low, Moderate, or Severe.
- 📄 Generates downloadable health reports in PDF format.
- 🌐 Offers interactive 3D visualization of disease-affected areas.

**Technologies Used:** OpenCV, Streamlit, Plotly, Machine Learning
""", unsafe_allow_html=True)

st.sidebar.markdown("## 👩‍💻 Developer")
st.sidebar.markdown("**Bhumika**  \n📧 bhumikasindhakhed12@gmail.com")

# --- App Logic ---
if "results" not in st.session_state:
    st.session_state.results = {}
if "uploaded_file_refs" not in st.session_state:
    st.session_state.uploaded_file_refs = {}

results = st.session_state.results
uploaded_file_refs = st.session_state.uploaded_file_refs

if menu == "📁 Image Upload":
    st.markdown("### 📁 Upload & Analyze Leaf Images")
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
            <div style='padding:10px; background-color:#f0f9ff; border-left:5px solid #2E7D32'>
            <b>🩺 Severity:</b> <span style='color:#2E7D32; font-size:20px;'>{severity}</span><br>
            <b>📊 Disease Coverage:</b> <span style='color:#F57C00;'>{percent:.2f}%</span><br>
            <b>🔬 Symptoms:</b> <span style='color:#6A1B9A;'>{', '.join(symptoms) or "None"}</span><br><br>
            <b>🛡️ General Advice:</b><br>{precautions}<br><br>
            <b>📘 Symptom-specific Tips:</b><br>{tips}
            </div>
            """, unsafe_allow_html=True)

            st.progress(min(int(percent), 100))
            st.markdown("---")
    else:
        st.warning("Please upload at least one image to begin analysis.")

elif menu == "📄 PDF Report":
    st.markdown("### 📄 Generate PDF Health Report")
    if results:
        if st.button("Generate PDF Report", key="pdf_button"):
            pdf_path = create_pdf_report(results)
            st.success("✅ PDF report generated successfully!")
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Download PDF", f, file_name="crop_health_report.pdf", mime="application/pdf")
    else:
        st.info("No results to report. Upload and analyze images first.")

elif menu == "🌐 3D Visualization":
    st.markdown("### 🌐 Interactive 3D Disease Visualization")
    if uploaded_file_refs:
        selected_img = st.selectbox("Select Image", list(uploaded_file_refs.keys()))
        fig = create_3d_surface_from_mask(uploaded_file_refs[selected_img])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Upload and analyze an image to view 3D plot.")

# --- Footer ---
st.markdown("""
---
<p style='text-align:center; font-size:16px; color:#666'>
🌱 <b>Project by Bhumika</b><br>
📧 bhumikasindhakhed12@gmail.com | 🚀 Streamlit • OpenCV • Plotly
</p>
""", unsafe_allow_html=True)
