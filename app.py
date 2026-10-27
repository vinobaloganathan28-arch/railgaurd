from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, flash
from config import USERS, TRACK, TRAIN, FOREST, SECRET_KEY
from database import init_db, detections, alerts, stats, read_alert, clear_history
from camera import camera

app = Flask(__name__)
app.secret_key = SECRET_KEY
init_db()


def login_required(f):
    @wraps(f)
    def w(*a, **k):
        return f(*a, **k) if session.get("user") else redirect(url_for("login"))
    return w


@app.context_processor
def common():
    return {
        "current_user": session.get("user"),
        "track": TRACK,
        "train": TRAIN,
        "forest": FOREST,
    }


@app.route("/")
def login():
    return redirect(url_for("dashboard")) if session.get("user") else render_template("login.html")


@app.post("/login")
def do_login():
    role = request.form.get("role", "").strip()
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "")
    user = USERS.get(username)
    if not user or user["password"] != password or user["role"] != role:
        flash("Select the correct role and enter valid credentials.", "error")
        return redirect(url_for("login"))
    session["user"] = user
    session["username"] = username
    return redirect(url_for("dashboard"))


@app.get("/logout")
def logout():
    camera.stop(); session.clear(); return redirect(url_for("login"))


@app.get("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", stats=stats(), recent=detections(8), alerts=alerts(5))


@app.get("/camera")
@login_required
def camera_page():
    return render_template("camera.html", ready=camera.detector.ready, error=camera.detector.error)


@app.get("/video_feed")
@login_required
def video_feed():
    return Response(camera.stream(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.get("/camera/status")
@login_required
def camera_status():
    return jsonify(camera.status())


@app.post("/camera/stop")
@login_required
def camera_stop():
    camera.stop(); return jsonify(ok=True)


@app.get("/api/overview")
@login_required
def api_overview():
    return jsonify({"stats": stats(), "recent": detections(8), "alerts": alerts(5), "camera": camera.status()})


@app.get("/api/detections")
@login_required
def api_detections():
    return jsonify(detections(100, request.args.get("type"), request.args.get("risk")))


@app.get("/history")
@login_required
def history():
    return render_template("history.html", items=detections())


@app.post("/history/clear")
@login_required
def history_clear():
    clear_history(); return jsonify(ok=True)


@app.get("/alerts")
@login_required
def alert_page():
    return render_template("alerts.html", items=alerts())


@app.post("/alerts/<int:i>/read")
@login_required
def alert_read(i):
    read_alert(i); return jsonify(ok=True)


@app.get("/map")
@login_required
def map_page():
    return render_template("map.html")


@app.get("/profile")
@login_required
def profile():
    return render_template("profile.html")


@app.get("/settings")
@login_required
def settings():
    return render_template("settings.html")


@app.errorhandler(404)
def e404(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
