import os
import sys
import json
import re

# Global list for label keywords, loaded from an external file.
label_keywords = []

def load_label_keywords(keywords_path: str):
    """
    Loads building plan label keywords from an external text file (one per line).
    Each line is stored in 'label_keywords' in lowercase.
    """
    global label_keywords
    if not os.path.isfile(keywords_path):
        print(f"[DEBUG] Label keywords file not found: {keywords_path}. Proceeding with empty list.")
        label_keywords = []
        return

    with open(keywords_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
        label_keywords = [line.strip().lower() for line in lines if line.strip()]

    print(f"[DEBUG] Loaded {len(label_keywords)} label keywords from {keywords_path}")

def categorize_text_entry(text: str) -> str:
    """
    Categorizes a text entry into either:
      - "dimension" if it matches common dimension patterns
      - "label" if it matches known keywords or is mostly alphanumeric
      - "misc" otherwise
    """
    text_lower = text.lower()

    # Dimension patterns
    dimension_patterns = [
        r"^\d+(\.\d+)?x\d+(\.\d+)?$",               # e.g. "8x16", "8.5x7.25"
        r"^\d+(\.\d+)?['\"-]?\s?(ft|in|m|cm|mm)?$",  # e.g. "12 ft", "12'", "12.5 in"
        r"^\d+(width|wide|height|hgt|clg)?\d*$",    # e.g. "16wide", "36height", "8clg"
    ]
    for pattern in dimension_patterns:
        if re.match(pattern, text_lower):
            return "dimension"

    # Check if text matches any known label keywords
    for kw in label_keywords:
        if kw in text_lower:
            return "label"

    # If it’s mostly alphanumeric and possibly spaces/hyphens => label
    if re.match(r"^[a-z0-9\s\-]+$", text_lower):
        return "label"

    # Otherwise, we classify it as "misc"
    print(f"[DEBUG] Unmatched entry: {text}")
    return "misc"

def categorize_text(input_path: str, output_path: str, confidence_threshold: float = 0.5):
    """
    Categorizes text entries based on regex patterns and flags low-confidence OCR results.
    
    :param input_path: Path to the merged text JSON file.
    :param output_path: Path to save the categorized results JSON file.
    :param confidence_threshold: Confidence below which text is flagged for review.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Merged results file not found: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        merged_results = json.load(f)

    categorized_results = []
    batch_size = 100  # Adjust as needed

    for i, entry in enumerate(merged_results):
        text = entry.get("text", "").strip()
        confidence = entry.get("confidence", 1.0)
        source = entry.get("source", None)

        category = categorize_text_entry(text)

        needs_review = (source == "ocr" and confidence < confidence_threshold)

        # Build final
        categorized_results.append({
            **entry,
            "category": category,
            "needs_review": needs_review
        })

        # Optional: save partial progress
        if (i + 1) % batch_size == 0:
            print(f"[DEBUG] Processed {i + 1}/{len(merged_results)} entries")
            with open(output_path, "w", encoding="utf-8") as batch_f:
                json.dump(categorized_results, batch_f, indent=2)

    # Save final results
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(categorized_results, f, indent=2)
    print(f"Categorized results saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python categorize_text.py <input_path> <output_path> [label_keywords_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # If you provided a third arg for label keywords, use it; else default
    if len(sys.argv) > 3:
        label_kw_path = sys.argv[3]
    else:
        # default to label_keywords.txt in the same dir
        script_dir = os.path.dirname(os.path.abspath(__file__))
        label_kw_path = os.path.join(script_dir, "label_keywords.txt")

    # Load label keywords
    load_label_keywords(label_kw_path)

    try:
        categorize_text(input_file, output_file)
    except Exception as e:
        print(f"Error categorizing text: {e}")