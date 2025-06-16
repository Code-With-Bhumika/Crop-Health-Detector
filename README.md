# 🌿 Crop Health Detector using OpenCV

This project identifies unhealthy regions on crop leaves using image processing in OpenCV. It works by detecting yellow/brown patches and calculating affected area percentage.

## 🔧 Technologies Used
- Python 3
- OpenCV
- NumPy

## 🧪 Features
- Load leaf image
- Convert to HSV
- Mask unhealthy (yellow/brown) regions
- Contour detection to highlight affected areas
- Severity classification

## 📂 How to Run
```bash
pip install -r requirements.txt
python main.py
```

## 📍 Applications
- Smart farming
- Crop disease monitoring
- Agricultural robotics

## 🧠 Future Work
- Use deep learning (e.g., CNN) for better classification
- Deploy to Raspberry Pi or Jetson Nano
