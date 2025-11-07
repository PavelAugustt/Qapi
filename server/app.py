from flask import Flask, jsonify, request
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Path to the data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro') # Using gemini-pro for text generation

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

@app.route('/instruct', methods=['POST'])
def instruct_llm():
    user_prompt = request.json.get('prompt')
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Simplified system prompt for now. This will be expanded later.
    # The README.MD suggests outlining handler functions and data structures here.
    system_prompt = """
You are Qapi, a helpful AI assistant designed to manage tasks and reminders.
Your goal is to assist the user in organizing their life and ensuring tasks are completed.
When a task is not completed, it is crucial to emphasize the worst-case scenario and consequences.
You have access to several data stores (e.g., user_goals_map, agent_context, timeheap)
and can use handler functions to interact with them.
For this interaction, assume you are receiving an instruction from the user.
Respond concisely and directly to the user's instruction.
    """

    try:
        # For now, just generate a response based on the user's prompt
        # In the future, this will involve more complex tool use and data store interaction
        response = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": system_prompt + "\nUser instruction: " + user_prompt}]}]
        )
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)