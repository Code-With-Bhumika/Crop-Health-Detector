import cv2
import numpy as np

def detect_yellowing(hsv_img):
    yellow_lower = np.array([20, 100, 100])
    yellow_upper = np.array([35, 255, 255])
    mask = cv2.inRange(hsv_img, yellow_lower, yellow_upper)
    ratio = np.sum(mask > 0) / (hsv_img.shape[0] * hsv_img.shape[1])
    return ratio, mask

def detect_holes(gray_img):
    _, black_mask = cv2.threshold(gray_img, 20, 255, cv2.THRESH_BINARY_INV)
    ratio = np.sum(black_mask > 0) / (gray_img.shape[0] * gray_img.shape[1])
    return ratio, black_mask

def detect_fungal_spots(gray_img):
    blurred = cv2.medianBlur(gray_img, 5)
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, 1, 20,
        param1=50, param2=30, minRadius=5, maxRadius=30
    )
    count = 0
    circle_coords = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        count = len(circles[0])
        circle_coords = [(x, y, r) for x, y, r in circles[0]]
    return count, circle_coords

def detect_dried_edges(hsv_img):
    edges = hsv_img[:, :10, :]  # left border slice
    brown_lower = np.array([10, 100, 20])
    brown_upper = np.array([20, 255, 200])
    mask = cv2.inRange(edges, brown_lower, brown_upper)
    ratio = np.sum(mask > 0) / (edges.shape[0] * edges.shape[1])
    return ratio, mask

def detect_symptoms_and_severity(image, percentage):
    symptoms = []
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    yellow_ratio, yellow_mask = detect_yellowing(hsv)
    if yellow_ratio > 0.02:
        symptoms.append("Yellowing")

    holes_ratio, holes_mask = detect_holes(gray)
    if holes_ratio > 0.01:
        symptoms.append("Holes")

    fungal_count, fungal_circles = detect_fungal_spots(gray)
    if fungal_count >= 2:
        symptoms.append("Fungal Spots")

    dried_ratio, dried_mask = detect_dried_edges(hsv)
    if dried_ratio > 0.02:
        symptoms.append("Dried Edges")

    # Severity based on disease area percentage (can be adjusted or combined with symptoms count)
    if percentage < 10:
        severity = "Healthy"
    elif percentage < 30:
        severity = "Low"
    elif percentage < 60:
        severity = "Moderate"
    else:
        severity = "Severe"

    # Optional: Return masks and detected features for visualization or 3D plotting
    return {
        "severity": severity,
        "symptoms": symptoms,
        "yellow_mask": yellow_mask,
        "holes_mask": holes_mask,
        "fungal_spots": fungal_circles,
        "dried_edges_mask": dried_mask,
        "severity_percent": percentage,
        "yellow_ratio": yellow_ratio,
        "holes_ratio": holes_ratio,
        "dried_ratio": dried_ratio
    }
