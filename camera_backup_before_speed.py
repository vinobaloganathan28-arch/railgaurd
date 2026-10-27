import cv2
import requests
import numpy as np
from detector import Detector


class Camera:
    def __init__(self):
        self.detector = Detector()
        self.last_found = []
        self.running = True

        # ESP32-CAM capture URL
        self.url = "http://172.30.80.245/capture"

    def open(self):
        return True

    def stop(self):
        self.running = False

    def status(self):
        return {
            "camera": True,
            "ai": self.detector.ready,
            "error": self.detector.error,
            "model": self.detector.model_source,
            "detections": self.last_found,
            "source": "ESP32-CAM"
        }

    def stream(self):
        self.running = True

        while self.running:

            try:
                response = requests.get(self.url, timeout=5)

                if response.status_code != 200:
                    continue

                image_array = np.frombuffer(response.content, dtype=np.uint8)
                frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                if frame is None:
                    continue

                # YOLO AI detection
                frame, found = self.detector.process(frame)
                self.last_found = found

                # Convert image to JPEG
                ok, data = cv2.imencode(
                    ".jpg",
                    frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), 88]
                )

                if ok:
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n"
                        b"Cache-Control: no-cache\r\n\r\n"
                        + data.tobytes()
                        + b"\r\n"
                    )

            except requests.RequestException as error:
                self.detector.error = str(error)
                continue

            except Exception as error:
                self.detector.error = str(error)
                continue


camera = Camera()