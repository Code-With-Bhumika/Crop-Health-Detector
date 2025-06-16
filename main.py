from pdf_report import create_pdf_report
import cv2
import numpy as np
import os
from utils import classify_damage

sample_folder = "samples"
output_folder = "output"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

results = {}  # Dictionary to store severity results for PDF report

for file in os.listdir(sample_folder):
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join(sample_folder, file)
        print(f"\n🔍 Processing: {image_path}")

        img = cv2.imread(image_path)
        if img is None:
            print("❌ Error: Image not found or unreadable.")
            continue
        else:
            print("✅ Image loaded successfully.")

        # Convert image to HSV color space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Define HSV range for yellow/brown (diseased areas)
        lower = np.array([10, 100, 100])
        upper = np.array([40, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)

        # Morphological operation to clean the mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Find contours of diseased spots
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw contours on original image
        cv2.drawContours(img, contours, -1, (0, 0, 255), 2)

        # Calculate area of diseased regions
        area = sum(cv2.contourArea(c) for c in contours)

        # Total image area (pixels)
        total = img.shape[0] * img.shape[1]
        if total == 0:
            severity_percent = 0
        else:
            severity_percent = (area / total) * 100

        # Classify severity based on percentage
        severity = classify_damage(severity_percent)

        print(f"🟡 Severity percentage: {severity_percent:.2f}%")
        print(f"🔎 Severity classification: {severity}")

        # Save results in dictionary
        results[file] = severity

        # Annotate image with severity text
        cv2.putText(img, f"Severity: {severity}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Save the annotated image to output folder
        output_path = os.path.join(output_folder, f"result_{file}")
        cv2.imwrite(output_path, img)

        # Optionally display the image (comment if running on headless server)
        # cv2.imshow("Detected", img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

# Generate PDF report after processing all images
create_pdf_report(results)
