import subprocess
import shlex
from core.app_config import settings
from ._common import parse_input

DESCRIPTION = "Executes a shell command and returns its output. Essential for file system navigation (e.g., 'ls -R') and other system interactions."
ARGS_SCHEMA = '{"command": "<string: The full shell command to execute, e.g., \'ls -l /path/to/dir\'>"}'

def run(action_input):
    """
    Executes a shell command and returns its output.
    This tool safely executes commands and returns a string containing
    the standard output and standard error.
    """
    # --- Permission Gates ---
    if not settings.get("ALLOW_RUN_SCRIPTS", False):
        return "Error: Command execution is disabled by permissions."

    try:
        args = parse_input(action_input)
        command = args.get("command", "")

        if not command:
            return "Error: 'command' argument is required."

        # Split command into a list to avoid shell injection vulnerabilities
        cmd_list = shlex.split(command)

        # Explicitly check for sudo
        if cmd_list and cmd_list[0] == 'sudo' and not settings.get("ALLOW_SUDO", False):
            return "Error: Sudo (superuser) execution is disabled by permissions."

        # --- Execute ---
        result = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            check=False,  # Don't automatically raise error, we'll format it
            encoding='utf-8'
        )
        
        output = result.stdout.strip() if result.stdout else ""
        error = result.stderr.strip() if result.stderr else ""

        if result.returncode != 0:
            return f"Error: Command failed with exit code {result.returncode}.\nSTDOUT:\n{output}\nSTDERR:\n{error}".strip()
        
        # On success, return stdout, and stderr if it exists
        return (output + "\n" + error).strip() if error else output

    except FileNotFoundError:
        return f"Error: Command not found: '{cmd_list[0]}'. Please ensure it is installed and on your system's PATH."
    except Exception as e:
        return f"Error: An unexpected exception occurred: {e}"
