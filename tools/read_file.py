import os
import mimetypes
from core.app_config import settings
from ._common import parse_input, resolve_path

DESCRIPTION = "Reads and returns the entire text content of a specified file."
ARGS_SCHEMA = '{"file_path": "<string: The full path of the file to read>"}'

def run(action_input):
    try:
        args = parse_input(action_input)
        file_path = resolve_path(args.get("file_path", ""))

        if not file_path:
            return "Error: 'file_path' argument is required."
            
        if not os.path.exists(file_path):
            return f"Error: File not found at path: {file_path}"

        # Detect and reject binary files
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and not mime_type.startswith("text"):
            return f"Error: Cannot read binary file. Mime type detected: {mime_type}"

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"
