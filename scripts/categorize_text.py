import os
import sys
import json
import re

def categorize_text(input_path, output_path, confidence_threshold=0.5):
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
    for entry in merged_results:
        text = entry.get("text", "").strip()
        confidence = entry.get("confidence", 1.0)
        category = categorize_text_entry(text)

        categorized_results.append({
            **entry,
            "category": category,
            "needs_review": entry["source"] == "ocr" and confidence < confidence_threshold
        })

    # Save categorized results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(categorized_results, f, indent=2)

    print(f"Categorized results saved to {output_path}")

def categorize_text_entry(text):
    """
    Categorizes a text entry into a dimension, label, or miscellaneous category.
    """
    text_lower = text.lower()
    # Match common dimension patterns (e.g., "12'-6\"", "12 ft", "12.5 m")
    if re.match(r"^\d+(\.\d+)?['\"-]?\s?(ft|in|m|cm|mm)?$", text_lower):
        return "dimension"
    elif re.match(r"^[a-z\s]+$", text_lower):
        return "label"
    else:
        return "misc"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python categorize_text.py <input_path> <output_path>")
        sys.exit(1)

    try:
        categorize_text(sys.argv[1], sys.argv[2])
    except Exception as e:
        print(f"Error categorizing text: {e}")