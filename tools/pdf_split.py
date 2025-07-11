import os
from core.app_config import settings
from ._common import parse_input, resolve_path
from PyPDF2 import PdfReader, PdfWriter

DESCRIPTION = "Splits each page of a PDF into a separate, single-page PDF file."
ARGS_SCHEMA = '{"pdf_path": "<string: path to the source PDF>", "output_dir": "<string: optional, directory to save page files, defaults to \'output_pages\'>"}'

def run(action_input):
    if not settings.get("ALLOW_FILE_CREATE", True):
        return "Error: File creation is disabled by permissions."

    try:
        args = parse_input(action_input)
        pdf_path = resolve_path(args.get("pdf_path", ""))
        output_dir = resolve_path(args.get("output_dir", "output_pages"))

        if not pdf_path:
            return "Error: 'pdf_path' argument is required."
        if not os.path.exists(pdf_path):
            return f"Error: PDF file not found at: {pdf_path}"

        os.makedirs(output_dir, exist_ok=True)
        reader = PdfReader(pdf_path)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            out_name = os.path.join(output_dir, f"{base_name}_page_{i + 1}.pdf")
            with open(out_name, "wb") as f_out:
                writer.write(f_out)
        
        return f"Successfully split {len(reader.pages)} pages into the directory: {output_dir}"

    except Exception as e:
        return f"Error splitting PDF: {e}"
