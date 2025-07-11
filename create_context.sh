#!/bin/bash

# The output file
CONTEXT_FILE="jaraxxus_context.md"

# Start with a clean file
> "$CONTEXT_FILE"

# 1. Add the project structure tree
echo "## Project Structure" >> "$CONTEXT_FILE"
echo "\`\`\`" >> "$CONTEXT_FILE"
tree . -I '.venv|__pycache__|*.pyc|jaraxxus_chroma_db' >> "$CONTEXT_FILE"
echo "\`\`\`" >> "$CONTEXT_FILE"
echo -e "\n---\n" >> "$CONTEXT_FILE"

# 2. Add the contents of all Python files
echo "## File Contents" >> "$CONTEXT_FILE"
for file in $(find . -type f -name "*.py"); do
    echo "### \`$file\`" >> "$CONTEXT_FILE"
    echo "\`\`\`python" >> "$CONTEXT_FILE"
    cat "$file" >> "$CONTEXT_FILE"
    echo -e "\n\`\`\`" >> "$CONTEXT_FILE"
    echo -e "\n---\n" >> "$CONTEXT_FILE"
done

echo "Context file '$CONTEXT_FILE' created successfully."
