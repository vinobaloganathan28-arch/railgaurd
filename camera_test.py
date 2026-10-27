import cv2

url = "http://172.30.80.245:81/stream"

cap = cv2.VideoCapture(url)

cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

print("Connecting to ESP32-CAM...")

if not cap.isOpened():
    print("❌ Camera stream open failed")
    exit()

print("✅ Camera stream connected!")

while True:
    ret, frame = cap.read()

    if not ret:
        print("❌ Frame not received")
        break

    cv2.imshow("RailGuard - ESP32 CAM", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()