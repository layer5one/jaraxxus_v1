# tools/__init__.py
import importlib
import pkgutil

# The master dictionary that will hold all discovered tool functions
AVAILABLE_TOOLS = {}

print("Initializing tool discovery...")

# Iterate over all modules in the 'tools' package
for finder, name, ispkg in pkgutil.iter_modules(__path__, __name__ + "."):
    if not ispkg:  # Ensure we are not importing a sub-package
        try:
            # Import the module (e.g., tools.run_command)
            module = importlib.import_module(name)

            # We expect each tool module to have a 'run' function
            if hasattr(module, 'run') and callable(getattr(module, 'run')):
                # The tool's key is its module name (e.g., "run_command")
                tool_name = name.split('.')[-1]
                AVAILABLE_TOOLS[tool_name] = module
                print(f"  > Discovered tool: '{tool_name}'")

        except Exception as e:
            print(f"  > Failed to load tool from {name}: {e}")

print(f"Tool discovery complete. Loaded: {list(AVAILABLE_TOOLS.keys())}")
