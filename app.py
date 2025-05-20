from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import re

app = Flask(__name__)

def detect_shape(img):
    output = img.copy()
    gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    shapes = []
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
        x, y, w, h = cv2.boundingRect(cnt)

        if len(approx) == 3:
            shape = "Triangle"
        elif len(approx) == 4:
            aspect_ratio = float(w) / h
            shape = "Square" if 0.95 <= aspect_ratio <= 1.05 else "Rectangle"
        elif len(approx) > 6:
            shape = "Circle"
        else:
            shape = "Unknown"

        shapes.append(shape)
    if shapes:
        return ", ".join(shapes)
    return "No shapes detected"

def parse_base64_image(data_url):
    # Remove header 'data:image/png;base64,'
    img_str = re.search(r'base64,(.*)', data_url).group(1)
    img_bytes = base64.b64decode(img_str)
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/detect", methods=["POST"])
def detect():
    data = request.json
    img_data = data.get("image")
    img = parse_base64_image(img_data)
    result = detect_shape(img)
    return jsonify({"shape": result})

if __name__ == "__main__":
    app.run(debug=True)
