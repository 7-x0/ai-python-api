from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "API شغال 🔥"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "")

    return jsonify({
        "result": f"حللت: {text}"
    })

app.run(host="0.0.0.0", port=3000)
