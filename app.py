import re
import uuid
import json
import os
from difflib import SequenceMatcher
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

DATA_FILE = "profiles.json"

# ── Data Management ──────────────────────────────────────────────────────────

def load_profiles():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_profiles(profiles):
    with open(DATA_FILE, "w") as f:
        json.dump(profiles, f, indent=4)

# ── Algorithmic Engine ───────────────────────────────────────────────────────

def mask_log(text):
    text = re.sub(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]', '<TIMESTAMP>', text)
    text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '<IP>', text)
    text = re.sub(r'\b\d+\b', '<NUM>', text)
    return text

def calculate_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/profiles", methods=["GET"])
def get_profiles():
    return jsonify(load_profiles())

@app.route("/api/profiles", methods=["POST"])
def add_profile():
    data = request.get_json(silent=True) or {}
    profiles = load_profiles()
    
    new_profile = {
        "id": str(uuid.uuid4()),
        "name": data.get("name", "Unnamed Profile"),
        "description": data.get("description", ""),
        "patterns": data.get("patterns", []),
        "instructions": data.get("instructions", ""),
        "task": data.get("task", {"enabled": False, "url": "", "method": "GET", "payload": ""})
    }
    
    profiles.insert(0, new_profile)
    save_profiles(profiles)
    return jsonify({"message": "Profile added successfully", "profile": new_profile})

@app.route("/api/profiles/<profile_id>", methods=["PUT"])
def update_profile(profile_id):
    """Update an existing profile by ID."""
    data = request.get_json(silent=True) or {}
    profiles = load_profiles()
    
    for i, p in enumerate(profiles):
        if p["id"] == profile_id:
            profiles[i].update({
                "name": data.get("name", p["name"]),
                "description": data.get("description", p.get("description", "")),
                "patterns": data.get("patterns", p.get("patterns", [])),
                "instructions": data.get("instructions", p.get("instructions", "")),
                "task": data.get("task", p.get("task", {"enabled": False, "url": "", "method": "GET", "payload": ""}))
            })
            save_profiles(profiles)
            return jsonify({"message": "Profile updated successfully", "profile": profiles[i]})
            
    return jsonify({"error": "Profile not found"}), 404

@app.route("/api/profiles/<profile_id>", methods=["DELETE"])
def delete_profile(profile_id):
    """Delete a profile by ID."""
    profiles = load_profiles()
    filtered_profiles = [p for p in profiles if p["id"] != profile_id]
    
    if len(filtered_profiles) < len(profiles):
        save_profiles(filtered_profiles)
        return jsonify({"message": "Profile deleted successfully"})
        
    return jsonify({"error": "Profile not found"}), 404

@app.route("/api/analyze", methods=["POST"])
def analyze_log():
    data = request.get_json(silent=True) or {}
    raw_log = data.get("log", "")
    
    if not raw_log:
        return jsonify({"error": "No log provided"}), 400

    red_flags = ['ERROR', 'FATAL', 'EXCEPTION', 'FAIL']
    error_lines = [line for line in raw_log.split('\n') if any(flag in line.upper() for flag in red_flags)]
    
    if not error_lines:
        return jsonify({"match": False, "message": "No obvious error keywords found."})

    target_line = error_lines[0]
    masked_line = mask_log(target_line)

    profiles = load_profiles()
    best_match = None
    highest_score = 0.0

    for profile in profiles:
        for pattern in profile.get("patterns", []):
            score = calculate_similarity(masked_line, pattern)
            if score > highest_score:
                highest_score = score
                best_match = profile

    confidence = round(highest_score * 100)

    if confidence > 65:
        return jsonify({
            "match": True,
            "confidence": confidence,
            "profile": best_match,
            "matched_segment": target_line
        })
    else:
        return jsonify({
            "match": False, 
            "confidence": confidence,
            "message": "Found an error, but it did not match any profiles closely enough."
        })

if __name__ == "__main__":
    app.run(debug=True, port=5000)