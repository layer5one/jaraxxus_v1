import importlib
import pkgutil
import tools  # the package containing all tool modules

TOOLS_REGISTRY = {}

# Dynamically import all modules in the tools package
for finder, name, ispkg in pkgutil.iter_modules(tools.__path__, tools.__name__ + "."):
    # Import the module (e.g., tools.create_file, tools.move_file, etc.)
    module = importlib.import_module(name)
    # Option 1: If each module has a known function name, e.g., function matches module name
    func_name = name.split(".")[-1]         # e.g., "create_file"
    if hasattr(module, func_name):
        TOOLS_REGISTRY[func_name] = getattr(module, func_name)
    # Option 2: Alternatively, import all functions from module:
    # for attr_name, attr_value in module.__dict__.items():
    #     if callable(attr_value):
    #         TOOLS_REGISTRY[attr_name] = attr_value

print("Loaded tools:", list(TOOLS_REGISTRY.keys()))
# Now you can call tools by name:
result = TOOLS_REGISTRY["create_file"]("/tmp/hello.txt", content="Hello, World!")
print(result)
