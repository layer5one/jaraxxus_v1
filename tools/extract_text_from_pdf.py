import os
from core.app_config import settings
from ._common import parse_input, resolve_path
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PyPDF2 import PdfReader

    # Set tesseract path from config
    if settings.get("tesseract_cmd_path"):
        pytesseract.pytesseract.tesseract_cmd = settings.get("tesseract_cmd_path")
except ImportError:
    pytesseract = None

DESCRIPTION = "Extracts all text from a PDF file. It first tries direct extraction, then falls back to OCR if needed."
ARGS_SCHEMA = '{"pdf_path": "<string: path to the PDF file>", "page_limit": "<integer: optional, number of pages to process>"}'

def run(action_input):
    if pytesseract is None:
        return "Error: PDF processing libraries (PyPDF2, pdf2image, pytesseract) are not installed."

    try:
        args = parse_input(action_input)
        pdf_path = resolve_path(args.get("pdf_path", ""))
        page_limit = args.get("page_limit") # Can be None

        if not pdf_path:
            return "Error: 'pdf_path' argument is required."
        if not os.path.exists(pdf_path):
            return f"Error: PDF file not found at: {pdf_path}"

        text_content = ""
        # 1. Direct text extraction
        try:
            reader = PdfReader(pdf_path)
            for i, page in enumerate(reader.pages):
                if page_limit and i >= page_limit:
                    break
                text_content += page.extract_text() + "\f" # Use form feed as page separator
        except Exception:
            text_content = "" # Reset on failure

        # 2. OCR Fallback
        if not text_content.strip():
            images = convert_from_path(pdf_path, dpi=300)
            if page_limit:
                images = images[:page_limit]
            
            for img in images:
                text_content += pytesseract.image_to_string(img, lang="eng") + "\f"

        return text_content.strip() if text_content.strip() else "Error: No text could be extracted from the PDF."

    except Exception as e:
        return f"Error processing PDF: {e}"
