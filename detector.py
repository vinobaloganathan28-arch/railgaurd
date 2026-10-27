import os, time
from config import MODEL_PATH
from database import add_detection, add_alert

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

ANIMALS = {
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear",
    "zebra", "giraffe"
}


class Detector:
    def __init__(self):
        self.model = None
        self.error = None
        self.last_saved = {}
        self.last_events = []
        self.model_source = ""
        self._load_model()

    def _load_model(self):
        if YOLO is None:
            self.error = "Ultralytics is not installed. Run: pip install -r requirements.txt"
            return
        try:
            if os.path.exists(MODEL_PATH):
                self.model = YOLO(MODEL_PATH)
                self.model_source = MODEL_PATH
            else:
                # Ultralytics downloads the official small model on first use when internet is available.
                self.model = YOLO("yolov8n.pt")
                self.model_source = "Ultralytics model cache / auto-download"
        except Exception as e:
            self.error = "YOLO model unavailable: " + str(e)

    @property
    def ready(self):
        return self.model is not None

    def process(self, frame):
        if not self.model:
            return frame, []
        try:
            result = self.model.predict(frame, conf=0.35, imgsz=640, verbose=False)[0]
        except Exception as e:
            self.error = str(e)
            return frame, []

        found = []
        if result.boxes is None:
            return result.plot(), found

        for b in result.boxes:
            label = result.names[int(b.cls[0])].lower()
            conf = float(b.conf[0])
            kind = "Human" if label == "person" else ("Animal" if label in ANIMALS else None)
            if not kind:
                continue
            risk = "High" if conf >= 0.70 else ("Medium" if conf >= 0.50 else "Low")
            item = {
                "type": kind,
                "label": label.title(),
                "confidence": round(conf * 100, 1),
                "risk": risk,
                "timestamp": time.time(),
            }
            found.append(item)

            # Save each category at most once every 2 seconds to avoid flooding the DB.
            now = time.time()
            key = f"{kind}:{label}"
            if now - self.last_saved.get(key, 0) >= 2.0:
                self.last_saved[key] = now
                add_detection(kind, label.title(), round(conf, 4), risk)
                if risk in ("High", "Medium"):
                    title = f"{kind} detected — {label.title()}"
                    message = f"AI detected {label.title()} with {conf * 100:.1f}% confidence in the monitored safety zone."
                    add_alert(title, message, risk, kind)

        self.last_events = found
        return result.plot(), found
