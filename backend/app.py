from flask import Flask, request, jsonify
from uuid import uuid4

app = Flask(__name__)

notes = []

@app.route("/api/notes", methods=["GET"])
def list_notes():
    return jsonify(notes)

@app.route("/api/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    note = {
        "id": uuid4().hex,
        "title": data.get("title", ""),
        "content": data.get("content", ""),
    }
    notes.append(note)
    return jsonify(note), 201

@app.route("/api/notes/<note_id>", methods=["GET"])
def get_note(note_id):
    note = next((n for n in notes if n["id"] == note_id), None)
    if note is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(note)

@app.route("/api/notes/<note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.get_json()
    for note in notes:
        if note["id"] == note_id:
            note["title"] = data.get("title", note["title"])
            note["content"] = data.get("content", note["content"])
            return jsonify(note)
    return jsonify({"error": "not found"}), 404

@app.route("/api/notes/<note_id>", methods=["DELETE"])
def delete_note(note_id):
    global notes
    notes = [n for n in notes if n["id"] != note_id]
    return "", 204

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
