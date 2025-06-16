from flask import Flask, request, jsonify, send_from_directory
from improv import ImprovGenerator
import os
import uuid

app = Flask(__name__)
generator = ImprovGenerator()
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    seed = data.get("seed")
    num_steps = data.get("num_steps", 500)
    max_len = data.get("max_sequence_length", 20)
    temperature = data.get("temperature", 0.3)

    notes = generator.generate_improv(seed, num_steps, max_len, temperature)

    base_name = str(uuid.uuid4())
    midi_path = os.path.join(OUTPUT_DIR, base_name + ".mid")
    stream = generator.save_improv(notes, file_name=midi_path)

    png_path = os.path.join(OUTPUT_DIR, base_name + ".png")
    stream.write("musicxml.png", fp=png_path)

    return jsonify({
        "notes": notes,
        "midi_file": f"/files/{base_name}.mid",
        "image_file": f"/files/{base_name}.png"
    })

@app.route("/files/<filename>")
def serve_file(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
