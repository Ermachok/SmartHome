import os
import time
import uuid

from flask import Flask, jsonify, send_from_directory
from picamera2 import Picamera2

app = Flask(__name__)

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())


@app.route("/take_photo", methods=["GET"])
def take_photo():
    try:
        unique_filename = str(uuid.uuid4()) + ".jpg"
        photo_path = os.path.join(os.getcwd(), unique_filename)

        picam2.start()
        picam2.capture_file(photo_path)
        picam2.stop()

        return send_from_directory(os.getcwd(), unique_filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
