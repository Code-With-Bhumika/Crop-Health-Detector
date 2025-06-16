def classify_damage(percentage):
    if percentage < 10:
        return "Healthy"
    elif percentage < 30:
        return "Low"
    elif percentage < 60:
        return "Moderate"
    else:
        return "Severe"




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
