import requests
import cv2
from ultralytics import YOLO

CAMERA_URL = "http://172.30.80.245/capture"

model = YOLO("yolo11n.pt")

TARGETS = {
    0: "PERSON",
    14: "BIRD",
    15: "CAT",
    16: "DOG",
    17: "HORSE",
    18: "SHEEP",
    19: "COW",
    20: "ELEPHANT",
    21: "BEAR",
    22: "ZEBRA",
    23: "GIRAFFE"
}

print("===================================")
print("      RAILGUARD AI DETECTION")
print("===================================")
print("Camera: ESP32-CAM")
print("AI Model: YOLO11n")
print("Status: Ready")
print()

try:
    response = requests.get(CAMERA_URL, timeout=10)

    if response.status_code != 200:
        print("❌ Camera capture failed")
        exit()

    with open("railguard_ai_input.jpg", "wb") as file:
        file.write(response.content)

    print("✅ Image captured from ESP32-CAM")

    results = model("railguard_ai_input.jpg", verbose=False)

    found = False

    for box in results[0].boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        if class_id in TARGETS and confidence >= 0.40:
            found = True

            name = TARGETS[class_id]

            print()
            print("🚨 RAILGUARD ALERT")
            print("Object:", name)
            print("Confidence:", f"{confidence * 100:.1f}%")

    if not found:
        print()
        print("✅ No person/animal detected")
        print("Track status: SAFE")

    results[0].save(filename="railguard_ai_result.jpg")

    print()
    print("✅ AI result saved as railguard_ai_result.jpg")

except requests.RequestException as error:
    print("❌ Camera connection error:", error)

except Exception as error:
    print("❌ Error:", error)