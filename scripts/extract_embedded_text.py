import os
import sys
import json
import pdfplumber

def extract_embedded_text(pdf_path, output_json):
    """
    Extracts embedded text from a PDF file and saves it as a JSON file,
    mapping the bounding box to bottom-left PDF coords
    (inverting y from pdfplumber's default top-left).
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    results = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            page_height = page.height  # pdfplumber page’s top-left-based page height

            text_objects = page.extract_words()  # Extract embedded text as word objects
            for obj in text_objects:
                # Coerce text to string
                raw_text = obj.get("text", "") or ""

                # pdfplumber returns top-based coords:
                # obj["x0"], obj["top"], obj["x1"], obj["bottom"]
                x0 = obj.get("x0", 0)
                top = obj.get("top", 0)
                x1 = obj.get("x1", 0)
                bottom = obj.get("bottom", 0)

                # Invert y to get bottom-left PDF coords:
                #   y0_bottomleft = page_height - bottom
                #   y1_bottomleft = page_height - top
                y0_bottomleft = page_height - bottom
                y1_bottomleft = page_height - top

                # Build the final bbox in bottom-left orientation:
                pdf_bbox = [x0, y0_bottomleft, x1, y1_bottomleft]

                entry = {
                    "page_index": page_index,
                    "text": raw_text,
                    "bbox": pdf_bbox,     # now in bottom-left PDF coords
                    "confidence": 1.0,    # default for embedded text
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