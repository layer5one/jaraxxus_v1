import os
import shutil
from core.app_config import settings
from ._common import parse_input, resolve_path

DESCRIPTION = "Moves or renames a file. Creates destination directories if they do not exist."
ARGS_SCHEMA = '{"source_path": "<string: The path of the file to move>", "destination_path": "<string: The new path for the file>"}'

def run(action_input):
    if not settings.get("ALLOW_FILE_CREATE", False):
        return "Error: File move/creation is disabled by permissions."

    try:
        args = parse_input(action_input)
        source_path = resolve_path(args.get("source_path", ""))
        destination_path = resolve_path(args.get("destination_path", ""))

        if not source_path or not destination_path:
            return "Error: 'source_path' and 'destination_path' arguments are required."
            
        if not os.path.exists(source_path):
            return f"Error: Source file not found: {source_path}"
            
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        shutil.move(source_path, destination_path)
        
        return f"File moved successfully: {source_path} -> {destination_path}"
    except Exception as e:
        return f"Error moving file: {e}"
