# core/app_config.py
import json
import os

def load_settings():
    # Example: Load settings from a JSON file
    # In a real application, this would be more robust.
    default_settings = {
        "ALLOW_RUN_SCRIPTS": True,
        "ALLOW_SUDO": False,
        "tesseract_cmd_path": None
    }
    # You can add logic here to load from a file, environment variables, etc.
    return default_settings

settings = load_settings()
