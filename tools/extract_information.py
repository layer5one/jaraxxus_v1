from ._common import parse_input, resolve_path
from . import extract_text_from_pdf, to_excel # Import the tool modules

DESCRIPTION = "High-level tool to extract text from a PDF and immediately save it as a spreadsheet."
ARGS_SCHEMA = '{"pdf_path": "<string: path to the source PDF>", "output_excel_path": "<string: path for the new .xlsx file>"}'

def run(action_input):
    try:
        args = parse_input(action_input)
        pdf_path = resolve_path(args.get("pdf_path", ""))
        output_path = resolve_path(args.get("output_excel_path", ""))
        
        if not pdf_path or not output_path:
            return "Error: 'pdf_path' and 'output_excel_path' are required arguments."

        # --- Step 1: Call the PDF extraction tool ---
        pdf_text_input = {"pdf_path": pdf_path}
        extracted_text = extract_text_from_pdf.run(pdf_text_input)

        if isinstance(extracted_text, str) and extracted_text.startswith("Error:"):
            return f"Error during PDF extraction step: {extracted_text}"

        # --- Step 2: Call the Excel writing tool ---
        # We'll use the simple "text" mode of the to_excel tool
        excel_writer_input = {
            "output_path": output_path,
            "text": extracted_text
        }
        result = to_excel.run(excel_writer_input)
        
        return result # Forward the result from the final step

    except Exception as e:
        return f"An error occurred in the extraction workflow: {e}"
