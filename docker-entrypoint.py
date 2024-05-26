from flask import Flask, jsonify
import threading

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    t = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    t.start()

    import main

