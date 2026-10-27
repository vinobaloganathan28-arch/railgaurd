
import requests
import time
from detector import Detector


class Camera:
    def __init__(self):
        self.detector = Detector()
        self.last_found = []
        self.running = True

        # Current working ESP32-CAM URL
        self.url = "http://192.168.137.157"

    def open(self):
        try:
            with requests.get(
                self.url,
                stream=True,
                timeout=(5, 10)
            ) as response:
                response.raise_for_status()

            self.detector.error = None
            print("CAMERA CONNECTED:", self.url)
            return True

        except requests.RequestException as error:
            self.detector.error = str(error)
            print("CAMERA CONNECTION ERROR:", repr(error))
            return False

    def stop(self):
        self.running = False

    def status(self):
        return {
            "camera": self.detector.error is None,
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
                with requests.get(
                    self.url,
                    stream=True,
                    timeout=(5, 30)
                ) as response:
                    response.raise_for_status()

                    buffer = b""

                    for chunk in response.iter_content(
                        chunk_size=1024
                    ):
                        if not self.running:
                            break

                        if not chunk:
                            continue

                        buffer += chunk

                        while True:
                            start = buffer.find(b"\xff\xd8")

                            if start < 0:
                                buffer = buffer[-1:]
                                break

                            end = buffer.find(
                                b"\xff\xd9",
                                start + 2
                            )

                            if end < 0:
                                buffer = buffer[start:]
                                break

                            jpg = buffer[start:end + 2]
                            buffer = buffer[end + 2:]

                            yield (
                                b"--frame\r\n"
                                b"Content-Type: image/jpeg\r\n"
                                b"Cache-Control: no-cache\r\n\r\n"
                                + jpg
                                + b"\r\n"
                            )

            except Exception as error:
                self.detector.error = str(error)
                print("CAMERA STREAM ERROR:", repr(error))
                time.sleep(1)


camera = Camera()
