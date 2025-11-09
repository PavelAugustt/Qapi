from flask import Flask, jsonify, request
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging
from server.handlers import read_data, write_data, append_data, get_timestamp
from google.generativeai import types

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(filename='server.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

app = Flask(__name__)

# Path to the data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    app.logger.error("GEMINI_API_KEY not found in environment variables.")
    raise ValueError("GEMINI_API_KEY not found in environment variables.")
genai.configure(api_key=GEMINI_API_KEY)


# Define the function declarations for the handler functions
read_data_function = {
    "name": "read_data",
    "description": "Reads data from a specified JSON data store.",
    "parameters": {
        "type": "object",
        "properties": {
            "store_name": {"type": "string", "description": "The name of the data store (e.g., 'user_goals_map')."},
        },
        "required": ["store_name"],
    },
}

write_data_function = {
    "name": "write_data",
    "description": "Writes data to a specified JSON data store. The data should be a valid JSON string.",
    "parameters": {
        "type": "object",
        "properties": {
            "store_name": {"type": "string", "description": "The name of the data store."},
            "data": {"type": "string", "description": "The JSON string representing the data to write."},
        },
        "required": ["store_name", "data"],
    },
}

append_data_function = {
    "name": "append_data",
    "description": "Appends a new entry to a list in a JSON data store. The new entry should be a valid JSON string.",
    "parameters": {
        "type": "object",
        "properties": {
            "store_name": {"type": "string", "description": "The name of the data store."},
            "new_entry": {"type": "string", "description": "The JSON string representing the new entry to append."},
        },
        "required": ["store_name", "new_entry"],
    },
}

get_timestamp_function = {
    "name": "get_timestamp",
    "description": "Returns the current timestamp in ISO format.",
    "parameters": {
        "type": "object",
        "properties": {},
    },
}

# Create the tools object
tools = types.Tool(function_declarations=[
    read_data_function,
    write_data_function,
    append_data_function,
    get_timestamp_function,
])

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash', # Corrected model name
    generation_config={"temperature": 0.7},
    tools=tools
)

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "ok", "message": "Server is running"})

@app.route('/timeheap', methods=['GET'])
def get_timeheap():
    return jsonify(read_data('timeheap'))

@app.route('/instruct', methods=['POST'])
def instruct_llm():
    user_prompt = request.json.get('prompt')
    if not user_prompt:
        app.logger.warning("Instruct endpoint called with no prompt.")
        return jsonify({"error": "No prompt provided"}), 400

    try:
        response = agent_execute(user_prompt)
        return jsonify({"response": response})
    except Exception as e:
        app.logger.exception("An error occurred during agent execution.")
        return jsonify({"error": "An internal error occurred."}), 500

def agent_execute(user_prompt):
    """
    The core logic for the agent.
    Constructs a system prompt, interacts with the LLM using function calling,
    and executes the user's instruction.
    """
    system_prompt = """
    You are Qapi, a helpful AI assistant. Your goal is to help the user manage their tasks and goals.
    You have access to a set of tools (functions) to interact with the user's data stores.
    The available data stores and their schemas are documented in the ARCH_DESIGN.MD file.
    When a user gives you an instruction, you should:
    1.  Refer to the ARCH_DESIGN.MD file to understand the data structures.
    2.  Decide which tools to use to fulfill the request.
    3.  Call the tools with the correct parameters, ensuring the data you provide matches the schema.
    4.  Use the tool outputs to formulate your final response.
    5.  If you need to add a task with a reminder, add it to the 'timeheap' data store.
        A timeheap entry should be a JSON object with 'id', 'description', and 'due_date' (in ISO format).
    6.  When creating tasks, always include the consequences of not completing the task in the description.
        This is very important. The consequences should be the worst-case scenario.
    7.  When adding to a data store, you should first read the data store to see what is already there, and then append the new data.
    """

    chat = model.start_chat()
    response = chat.send_message(system_prompt + "\nUser instruction: " + user_prompt)

    while True:
        function_call = None
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    function_call = part.function_call
                    break

        if not function_call:
            break # No function call, break the loop

        function_name = function_call.name
        function_args = function_call.args

        result = None
        if function_name == "read_data":
            result = read_data(function_args["store_name"])
        elif function_name == "write_data":
            result = write_data(function_args["store_name"], json.loads(function_args["data"]))
        elif function_name == "append_data":
            result = append_data(function_args["store_name"], json.loads(function_args["new_entry"]))
        elif function_name == "get_timestamp":
            result = get_timestamp()
        else:
            result = {"error": f"Unknown function: {function_name}"}

        # Send the result back to the model
        response = chat.send_message(
            [{"function_response": {"name": function_name, "response": {"result": result}}}]
        )

    return response.text

@app.route('/search', methods=['POST'])
def search():
    """
    Instructs the LLM to search the data stores.
    """
    query = request.json.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    search_prompt = f"""
    The user wants to search the data stores.
    The query is: "{query}"
    Please search the relevant data stores and return the results.
    """
    try:
        response = agent_execute(search_prompt)
        return jsonify({"response": response})
    except Exception as e:
        app.logger.exception("An error occurred during search.")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/create_daily_timeheap', methods=['POST'])
def create_daily_timeheap():
    """
    Instructs the LLM to create the daily timeheap.
    """
    # The prompt for the agent to create the daily timeheap
    timeheap_creation_prompt = """
    It's the start of a new day. Please create the daily timeheap for today.
    Review the 'user_goals_map.json' and 'priorities.json' data stores.
    Based on the user's goals and priorities, create a list of tasks for today
    and add them to the 'timeheap.json' data store.
    For each task, provide a detailed description, a due date in ISO format,
    and the worst-case consequences for not completing the task.
    """
    try:
        response = agent_execute(timeheap_creation_prompt)
        return jsonify({"response": response})
    except Exception as e:
        app.logger.exception("An error occurred during daily timeheap creation.")
        return jsonify({"error": "An internal error occurred."}), 500

if __name__ == '__main__':
    app.run(debug=True)