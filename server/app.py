from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

# Path to the data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "ok", "message": "Server is running"})

@app.route('/timeheap', methods=['GET'])
def get_timeheap():
    try:
        with open(os.path.join(DATA_DIR, 'timeheap.json'), 'r') as f:
            timeheap_data = json.load(f)
        return jsonify(timeheap_data)
    except FileNotFoundError:
        return jsonify({"error": "Timeheap file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON in timeheap file"}), 500

if __name__ == '__main__':
    app.run(debug=True)