import json
import os
from datetime import datetime
import uuid

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def _generate_id():
    """Generates a unique ID."""
    return str(uuid.uuid4())

def _create_truncated_desc(description, max_length=100):
    """Creates a truncated description."""
    if len(description) > max_length:
        return description[:max_length-3] + "..."
    return description

def get_timestamp():
    """Returns the current timestamp in ISO format (UTC)."""
    from datetime import timezone
    return datetime.now(timezone.utc).isoformat()

def read_data(store_name):
    """Reads data from a specified JSON file in the data directory."""
    file_path = os.path.join(DATA_DIR, f"{store_name}.json")
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # If the file doesn't exist, return an empty list for list-based stores
        # or an empty dict for dict-based stores (like priorities)
        if store_name in ['user_goals_map', 'agent_context', 'user_context', 'agent_tasks', 'timeheap', 'chatlog']:
            return []
        elif store_name == 'priorities':
            return {"daily": [], "weekly": [], "monthly": []}
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
    """
    Appends a new entry to a JSON list in a file,
    automatically adding id, entry_date, and truncated_desc.
    """
    file_path = os.path.join(DATA_DIR, f"{store_name}.json")
    try:
        data = read_data(store_name)
        if "error" in data: # Handle case where read_data returned an error
            data = [] # Assume empty list if file not found or invalid JSON for append

        if isinstance(data, list):
            # Add metadata if not already present
            if "id" not in new_entry:
                new_entry["id"] = _generate_id()
            if "entry_date" not in new_entry:
                new_entry["entry_date"] = get_timestamp()
            if "description" in new_entry and "truncated_desc" not in new_entry:
                new_entry["truncated_desc"] = _create_truncated_desc(new_entry["description"])

            data.append(new_entry)
            return write_data(store_name, data)
        else:
            return {"error": f"Data store '{store_name}' is not a list. Use write_data for dictionary-based stores."}
    except Exception as e:
        return {"error": f"Error appending to data store '{store_name}': {e}"}

def delete_data_entry(store_name, entry_id):
    """Deletes an entry from a list-based data store by its ID."""
    file_path = os.path.join(DATA_DIR, f"{store_name}.json")
    try:
        data = read_data(store_name)
        if "error" in data:
            return data # Pass through error from read_data

        if isinstance(data, list):
            initial_len = len(data)
            data = [entry for entry in data if entry.get("id") != entry_id]
            if len(data) < initial_len:
                return write_data(store_name, data)
            else:
                return {"error": f"Entry with ID '{entry_id}' not found in '{store_name}'."}
        else:
            return {"error": f"Data store '{store_name}' is not a list. Cannot delete by ID."}
    except Exception as e:
        return {"error": f"Error deleting from data store '{store_name}': {e}"}

def load_memory(store_name, entry_id=None):
    """
    Loads memory from a specified data store.
    If entry_id is provided, loads a specific entry.
    Otherwise, loads the entire store.
    """
    data = read_data(store_name)
    if "error" in data:
        return data

    if entry_id:
        if isinstance(data, list):
            for entry in data:
                if entry.get("id") == entry_id:
                    return entry
            return {"error": f"Entry with ID '{entry_id}' not found in '{store_name}'."}
        else:
            return {"error": f"Data store '{store_name}' is not a list. Cannot load specific entry by ID."}
    return data
