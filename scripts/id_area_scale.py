import json
import re
import sys
import os
from collections import defaultdict, Counter
from config import DATA_OUTPUT  # Ensure config.py is in the proper path

# --- Helper Functions ---

def parse_fraction(frac_str):
    # Replace common special fraction characters with text equivalents.
    specials = {'¼': '1/4', '½': '1/2', '¾': '3/4'}
    for char, rep in specials.items():
        frac_str = frac_str.replace(char, rep)
    frac_str = frac_str.replace('"', '').replace("”", "").strip()
    if '/' in frac_str:
        try:
            num, denom = frac_str.split('/')
            return float(num) / float(denom)
        except Exception as e:
            # If conversion fails, return None
            return None
    else:
        try:
            return float(frac_str)
        except Exception as e:
            return None

def extract_blueprint_title(text):
    # Look for common blueprint title phrases (case-insensitive)
    title_pattern = r'(?i)(noted plan|first floor plan|1st floor plan|second floor plan|2nd floor plan|third floor plan|3rd floor plan|floor plan)'
    match = re.search(title_pattern, text)
    if match:
        return match.group(1).lower()
    return None

def extract_scale(text):
    # Look for a scale string such as: SCALE : 1/4" = 1'-0"
    # Allow for various delimiters and spacing
    scale_pattern = r'(?i)scale\s*[:\-]?\s*([\d\/¼½¾]+)["”]?\s*=\s*([\d]+(?:[-\']\d+)?)["’]?'
    match = re.search(scale_pattern, text)
    if match:
        left_raw = match.group(1).strip()  # e.g. "1/4" or "¼"
        right_raw = match.group(2).strip() # e.g. "1" or "1-0"
        left_value = parse_fraction(left_raw)
        try:
            # Remove any non-digit/dot characters from right_raw:
            right_value = float(re.sub(r'[^0-9\.]', '', right_raw))
        except Exception as e:
            right_value = None
        if left_value and right_value and left_value != 0:
            # Convert right_value in feet to inches:
            scale_ratio = (right_value * 12) / left_value
            return {
                "paper_measurement": left_value,
                "real_measurement_ft": right_value,
                "scale_ratio": scale_ratio  # e.g., 48 means 1:48 scale.
            }
        else:
            return {"paper_measurement_raw": left_raw, "real_measurement_raw": right_raw}
    return None

def extract_areas(text):
    """
    Instead of scanning the entire blob with a single regex,
    we look for a header (SQUARE FOOTAGE or AREA TABULATION) and then
    attempt to parse subsequent lines for room labels and numbers.
    """
    areas = {}
    # First, try to split the text into lines
    lines = text.splitlines()
    start_idx = None
    # Look for header lines that indicate area information
    header_pattern = re.compile(r'(?i)(SQUARE\s+FOOTAGE|AREA\s+TABULATION)')
    for i, line in enumerate(lines):
        if header_pattern.search(line):
            start_idx = i
            break
    if start_idx is not None:
        # Process subsequent lines until a blank line or a different header appears
        for line in lines[start_idx+1:]:
            line = line.strip()
            if not line:
                break
            # Expect lines of the form: LABEL ... NUMBER (optionally with S.F.)
            # Example: LIVING           1768
            match = re.search(r'(?i)^([A-Z\s]+?)\s*[:\-]?\s*(\d{2,6})\s*(?:S\.?F\.?)?$', line)
            if match:
                label = match.group(1).strip().upper()
                try:
                    value = int(match.group(2))
                    areas[label] = value
                except:
                    continue
    return areas

def extract_scale_and_area(text):
    result = {"scale": None, "areas": {}}
    # First try to extract scale
    scale_data = extract_scale(text)
    result["scale"] = scale_data

    # Then try to extract area data using the header method
    areas = extract_areas(text)
    result["areas"] = areas

    return result

# --- New Functions for Spatial Grouping ---

def group_entries_by_line(entries, vertical_threshold=5):
    """
    Groups text entries (each with a 'bbox' and 'text') that lie on the same line.
    Sorting is done based on the average y coordinate of the bounding box.
    """
    # Sort entries by the average y (lower values first) then by x coordinate
    sorted_entries = sorted(entries, key=lambda e: (((e["bbox"][1] + e["bbox"][3]) / 2), e["bbox"][0]))
    lines = []
    current_line = []
    current_y = None
    for entry in sorted_entries:
        bbox = entry["bbox"]
        # Average y coordinate of the entry
        y_avg = (bbox[1] + bbox[3]) / 2
        if current_y is None:
            current_y = y_avg
            current_line.append(entry)
        elif abs(y_avg - current_y) <= vertical_threshold:
            current_line.append(entry)
        else:
            lines.append(current_line)
            current_line = [entry]
            current_y = y_avg
    if current_line:
        lines.append(current_line)
    return lines

def merge_line_entries(line_entries, horizontal_gap_threshold=10):
    """
    Merges text entries within the same line based on horizontal positions.
    If the gap between the end of one entry and the start of the next exceeds
    a threshold, a space is inserted.
    """
    # Sort by x coordinate (left edge)
    sorted_entries = sorted(line_entries, key=lambda e: e["bbox"][0])
    merged_text = ""
    last_x_end = None
    for entry in sorted_entries:
        bbox = entry["bbox"]
        x_start = bbox[0]
        text = entry["text"].strip()
        if last_x_end is not None and (x_start - last_x_end) > horizontal_gap_threshold:
            merged_text += " "  # insert space if gap is significant
        merged_text += text + " "
        last_x_end = entry["bbox"][2]
    return merged_text.strip()

# --- Main Processing ---

def main():
    if len(sys.argv) < 2:
        print("Usage: python id_area_scale.py <merged_results.json>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    if not os.path.isfile(json_path):
        print(f"File not found: {json_path}")
        sys.exit(1)
    
    # Load merged_results.json
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            merged_data = json.load(f)
    except Exception as e:
        print(f"Error reading {json_path}: {e}")
        sys.exit(1)
    
    # Group text entries by page_index
    pages_entries = defaultdict(list)
    for entry in merged_data:
        page = entry.get("page_index")
        if entry.get("text") and "bbox" in entry:
            pages_entries[page].append(entry)
    
    page_extractions = {}
    blob_debug = {}
    # For each page, group the entries by their spatial line, then merge them.
    for page, entries in pages_entries.items():
        # Group entries that appear on the same line
        lines = group_entries_by_line(entries)
        # Merge entries in each line based on horizontal position
        merged_lines = [merge_line_entries(line) for line in lines]
        # Create a blob with newline separation between lines
        page_blob = "\n".join(merged_lines)
        blob_debug[str(page)] = page_blob  # store for debugging
        extraction = extract_scale_and_area(page_blob)
        title = extract_blueprint_title(page_blob)
        page_extractions[page] = {
            "extraction": extraction,
            "title": title
        }
    
    # Decide on final scale:
    scales = []
    priority_pages = []
    for page, data in page_extractions.items():
        scale_info = data["extraction"].get("scale")
        if scale_info and "scale_ratio" in scale_info:
            scales.append((page, scale_info["scale_ratio"]))
        if data["title"]:
            priority_pages.append((page, data["title"], scale_info))
    
    final_scale = None
    chosen_page = None
    if priority_pages:
        # Prefer the first priority page
        chosen_page, title, scale_info = priority_pages[0]
        final_scale = scale_info
    elif scales:
        # Choose the most common scale_ratio
        scale_ratios = [sr for page, sr in scales]
        most_common = Counter(scale_ratios).most_common(1)
        if most_common:
            common_ratio = most_common[0][0]
            for page, sr in scales:
                if sr == common_ratio:
                    chosen_page = page
                    final_scale = {"scale_ratio": sr}
                    break

    final_output = {
        "final_scale": final_scale,
        "scale_source_page": chosen_page,
        "page_extractions": { str(page): data["extraction"] for page, data in page_extractions.items() },
        "blueprint_titles": { str(page): data["title"] for page, data in page_extractions.items() if data["title"] }
    }

    # Infer plan_id from the directory where the merged_results.json is located.
    inferred_plan_id = os.path.basename(os.path.dirname(json_path))
    plan_id = inferred_plan_id if inferred_plan_id else "Floor Plan"

    # Build the output folder path from config.DATA_OUTPUT/results/<plan_id>
    out_folder = os.path.join(DATA_OUTPUT, "results", plan_id)
    os.makedirs(out_folder, exist_ok=True)
    # Write final output to plan_area_scale.json in that folder
    out_path = os.path.join(out_folder, "plan_area_scale.json")
    with open(out_path, 'w', encoding='utf-8') as f_out:
        json.dump(final_output, f_out, indent=2)
    
    # Also write the blob_debug file for reference
    blob_debug_path = os.path.join(out_folder, "blob_debug.json")
    with open(blob_debug_path, 'w', encoding='utf-8') as f_blob:
        json.dump(blob_debug, f_blob, indent=2)

if __name__ == '__main__':
    main()