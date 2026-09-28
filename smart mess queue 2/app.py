from flask import Flask, render_template, jsonify, request
from collections import deque
import time

app = Flask(__name__)

class SmartMessQueueManager:
    def __init__(self, avg_prep_mins=2):
        self.queue = deque()
        self.token_counter = 101
        self.served_history = []
        self.avg_prep_mins = avg_prep_mins

    def add_student(self, name, meal):
        token_id = f"TKN-{self.token_counter}"
        student = {
            "token": token_id,
            "name": name,
            "meal": meal,
            "time_joined": time.strftime("%H:%M:%S")
        }
        self.queue.append(student)
        self.token_counter += 1
        return student

    def serve_next(self):
        if not self.queue:
            return None
        student = self.queue.popleft()
        student["time_served"] = time.strftime("%H:%M:%S")
        self.served_history.append(student)
        return student

    def get_status(self):
        return {
            "queue": list(self.queue),
            "waiting_count": len(self.queue),
            "est_wait_time": max(0, (len(self.queue) - 1) * self.avg_prep_mins),
            "history": self.served_history[::-1]  # Latest served first
        }

manager = SmartMessQueueManager()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify(manager.get_status())

@app.route("/api/token", methods=["POST"])
def generate_token():
    data = request.json
    name = data.get("name", "").strip()
    meal = data.get("meal", "Regular Thali")
    
    if not name:
        return jsonify({"success": False, "error": "Name is required"}), 400

    student = manager.add_student(name, meal)
    return jsonify({"success": True, "student": student})

@app.route("/api/serve", methods=["POST"])
def serve_student():
    served = manager.serve_next()
    if served:
        return jsonify({"success": True, "served": served})
    return jsonify({"success": False, "message": "Queue is empty!"}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)