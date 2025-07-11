import os
from core.app_config import settings
from ._common import parse_input, resolve_path

DESCRIPTION = "Creates a new file and writes specified content to it. Overwrites existing files."
ARGS_SCHEMA = '{"file_path": "<string: The full path of the file to create>", "content": "<string: The text content to write into the file>"}'

def run(action_input):
    if not settings.get("ALLOW_FILE_CREATE", False):
        return "Error: File creation is disabled by permissions."

    try:
        args = parse_input(action_input)
        file_path = resolve_path(args.get("file_path", ""))
        content = args.get("content", "")

        if not file_path:
            return "Error: 'file_path' argument is required."

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"File created successfully: {file_path}"
    except Exception as e:
        return f"Error creating file: {e}"
