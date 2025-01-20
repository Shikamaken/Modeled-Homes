import os
import sys
import json
import pdfplumber

def extract_embedded_text(pdf_path, output_json):
    """
    Extracts embedded text from a PDF file and saves it as a JSON file,
    ensuring we produce a 'bbox' and a valid 'text' string for each entry.

    :param pdf_path: Path to the input PDF file.
    :param output_json: Path to save the extracted embedded text as JSON.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    results = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            text_objects = page.extract_words()  # Extract embedded text as word objects

            for obj in text_objects:
                # Coerce text to string (avoid None)
                raw_text = obj.get("text", "")
                if raw_text is None:
                    raw_text = ""

                # Build 'bbox' from pdfplumber fields: [x0, top, x1, bottom]
                bbox = [
                    obj.get("x0", 0),
                    obj.get("top", 0),
                    obj.get("x1", 0),
                    obj.get("bottom", 0),
                ]

                # Construct the final dict, including "source"
                entry = {
                    "page_index": page_index,
                    "text": raw_text,
                    "bbox": bbox,
                    "confidence": 1.0,  # default for embedded text
                    "source": "embedded"
                }

                results.append(entry)

    # Save results to JSON
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Embedded text extracted and saved to {output_json}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_embedded_text.py <input_pdf_path> <output_json_path>")
        sys.exit(1)

    input_pdf_path = os.path.normpath(sys.argv[1])
    output_json_path = os.path.normpath(sys.argv[2])

    try:
        extract_embedded_text(input_pdf_path, output_json_path)
    except Exception as e:
        print(f"Error extracting embedded text: {e}")
        sys.exit(1)