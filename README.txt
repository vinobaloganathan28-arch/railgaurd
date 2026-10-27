RAILGUARD v2.0 - FULL WORKING PROTOTYPE

RUN
1. Open this folder in VS Code.
2. Open Terminal in the folder.
3. Run: pip install -r requirements.txt
4. Run: python app.py
5. Open: http://127.0.0.1:5000

DEMO LOGIN
Loco Pilot   -> loco / loco123
Forest Officer -> forest / forest123

AI CAMERA
- Open Live AI Camera and allow webcam access if Windows asks.
- YOLOv8n is used for human and supported animal classes.
- If yolov8n.pt is not in the project folder, Ultralytics will try to download it automatically when internet is available.
- Keep the browser page open while testing so detections are processed and written to SQLite.

ALERT SOUND
The alert sound uses the browser Web Audio API. Click the bell button once to enable/unmute it. Browsers block unsolicited audio before user interaction.

DATA
Detection history and alerts are stored in database/history.db.

HARDWARE CAMERA
The camera source is isolated in camera.py. Later, replace VideoCapture(0) with an RTSP/IP camera URL when the ordered hardware camera arrives.
