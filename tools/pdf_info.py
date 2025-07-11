import os
from core.app_config import settings
from ._common import parse_input, resolve_path
from PyPDF2 import PdfReader

DESCRIPTION = "Returns metadata about a PDF file, such as the number of pages and title."
ARGS_SCHEMA = '{"pdf_path": "<string: The path to the PDF file>"}'

def run(action_input):
    try:
        args = parse_input(action_input)
        pdf_path = resolve_path(args.get("pdf_path", ""))

        if not pdf_path:
            return "Error: 'pdf_path' argument is required."
        if not os.path.exists(pdf_path):
            return f"Error: PDF file not found at: {pdf_path}"
        
        reader = PdfReader(pdf_path)
        metadata = reader.metadata
        
        info = {
            "page_count": len(reader.pages),
            "title": getattr(metadata, 'title', 'N/A'),
            "author": getattr(metadata, 'author', 'N/A'),
        }
        return f"PDF Info: {info}"
        
    except Exception as e:
        return f"Error getting PDF info: {e}"
