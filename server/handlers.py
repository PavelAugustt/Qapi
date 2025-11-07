import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def get_timestamp():
    """Returns the current timestamp in ISO format."""
    return datetime.now().isoformat()

def read_data(store_name):
    """Reads data from a specified JSON file in the data directory."""
    file_path = os.path.join(DATA_DIR, f"{store_name}.json")
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": f"Data store '{store_name}' not found."}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON in data store '{store_name}'."}

def write_data(store_name, data):
    """Writes data to a specified JSON file in the data directory."""
    file_path = os.path.join(DATA_DIR, f"{store_name}.json")
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return {"success": f"Data store '{store_name}' updated."}
    except Exception as e:
        return {"error": f"Error writing to data store '{store_name}': {e}"}

def append_data(store_name, new_entry):
    """Appends a new entry to a JSON list in a file."""
    file_path = os.path.join(DATA_DIR, f"{store_name}.json")
    try:
        with open(file_path, 'r+') as f:
            data = json.load(f)
            if isinstance(data, list):
                data.append(new_entry)
                f.seek(0)
                json.dump(data, f, indent=4)
                return {"success": f"New entry added to '{store_name}'."}
            else:
                return {"error": f"Data store '{store_name}' is not a list."}
    except FileNotFoundError:
        return {"error": f"Data store '{store_name}' not found."}
    except Exception as e:
        return {"error": f"Error appending to data store '{store_name}': {e}"}
