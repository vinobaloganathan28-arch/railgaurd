import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "yolov8n.pt")
DATABASE_PATH = os.path.join(BASE_DIR, "database", "history.db")
SECRET_KEY = "railguard-demo-secret-change-me"

USERS = {
    "loco": {"password": "loco123", "role": "Loco Pilot", "name": "Arun Kumar", "unit": "Rail Operations"},
    "forest": {"password": "forest123", "role": "Forest Officer", "name": "Priya Sharma", "unit": "Forest & Wildlife"},
}

TRACK = {
    "camera_id": "RG-CAM-01",
    "track_id": "TRK-CGL-07",
    "zone": "Chengalpattu Safety Zone",
    "location": "RailGuard Safety Corridor",
    "lat": 12.6819,
    "lng": 79.9888,
    "radius_m": 2000,
}

TRAIN = {
    "train_no": "12606",
    "service": "Chennai Egmore – Karaikkudi",
    "speed": "62 km/h",
    "next_station": "Chengalpattu",
    "signal": "CLEAR",
}

FOREST = {
    "reserve": "Chengalpattu Wildlife Corridor",
    "patrol_unit": "FW-12",
    "crossing": "Wildlife Crossing A",
    "patrol_status": "ON DUTY",
}
