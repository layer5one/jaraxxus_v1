import os
from core.app_config import settings
from ._common import parse_input, resolve_path

DESCRIPTION = "Deletes a specified file from the filesystem."
ARGS_SCHEMA = '{"file_path": "<string: The full path of the file to delete>"}'

def run(action_input):
    if not settings.get("ALLOW_FILE_DELETE", False):
        return "Error: File deletion is disabled by permissions."

    try:
        args = parse_input(action_input)
        file_path = resolve_path(args.get("file_path", ""))

        if not file_path:
            return "Error: 'file_path' argument is required."
        
        if not os.path.exists(file_path):
            return f"Error: File not found at path: {file_path}"

        os.remove(file_path)
        return f"File deleted successfully: {file_path}"
    except Exception as e:
        return f"Error deleting file: {e}"
