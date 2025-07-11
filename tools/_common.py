import json
import ast

def parse_input(action_input):
    """
    Parses the action_input, which can be a dict or a JSON string.
    Returns a dictionary.
    """
    if isinstance(action_input, dict):
        return action_input
    
    if isinstance(action_input, str):
        try:
            return json.loads(action_input)
        except json.JSONDecodeError:
            # Fallback for slight syntax errors like single quotes
            try:
                return ast.literal_eval(action_input)
            except Exception as e:
                raise ValueError(f"Input is not a valid JSON object or Python literal: {e}")
    
    raise TypeError(f"Invalid input type: {type(action_input)}. Expected dict or JSON string.")

# We keep this path logic as it's useful for handling file paths consistently.
def resolve_path(path_str: str) -> str:
    """Corrects for absolute paths that should be relative to the project."""
    if not isinstance(path_str, str):
        return ""
    # If a path like "/results/file.txt" is given and "./results/file.txt" exists,
    # assume the user meant the local path.
    if path_str.startswith('/') and os.path.exists(f".{path_str}"):
        return f".{path_str}"
    return path_str
