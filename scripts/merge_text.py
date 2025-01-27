import os
import sys
import json
import difflib
from typing import List, Dict, Any, Optional
from spellchecker import SpellChecker

##############
# Parameters #
##############

IOU_THRESHOLD = 0.5       # Overlap threshold for merging embedded & OCR
SIM_THRESHOLD = 0.8       # Text similarity threshold for merging
ALLOW_PARTIAL_MERGE = True  # If True, combine partial OCR entries
MAX_HORIZONTAL_GAP = 5.0  # Gap for fusing embedded text
VERTICAL_THRESHOLD = 3.0  # Allowed vertical difference for same line

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN_DICTIONARY_PATH = os.path.join(project_root, "scripts", "my_domain_dictionary.txt")

#####################
# Debug text = none #
#####################

def debug_check_for_none_text(entries, label=""):
    """
    Prints a debug message for any entry whose 'text' is None.
    """
    if not entries:
        return
    for i, e in enumerate(entries):
        if e.get("text", "") is None:
            print(f"[DEBUG] {label}: Found None text at index={i}, entry={e}")

############################
# Spell Checker and Domain #
############################

spell = SpellChecker()

def load_domain_dictionary(dictionary_path: str):
    """
    Loads additional domain-specific words (HVAC terms, etc.)
    into the spellchecker so they aren't flagged as typos.
    """
    if os.path.isfile(dictionary_path):
        spell.word_frequency.load_text_file(dictionary_path)
    else:
        print(f"Domain dictionary not found: {dictionary_path} (continuing without it)")

def advanced_spellcheck(text: str) -> str:
    """
    Runs the text through pyspellchecker, skipping short numeric strings
    and handling domain-specific caps if needed.
    Ensures no None value is appended to corrected_tokens.
    """
    tokens = text.split()
    corrected_tokens = []

    for token in tokens:
        # skip very short tokens or purely digits/dimensions
        if len(token) < 3 or token.isdigit():
            corrected_tokens.append(token)
            continue

        # handle uppercase
        if token.isupper():
            guess = spell.correction(token.lower())
            corrected = guess.upper() if guess else token
        else:
            guess = spell.correction(token)
            corrected = guess if guess else token

        # fallback
        if corrected is None:
            corrected = token

        corrected_tokens.append(corrected)

    return " ".join(corrected_tokens)

####################################
# Embedded Text Fusing (same line) #
####################################

def fuse_embedded_text(embedded_entries: List[Dict],
                       max_horizontal_gap: float = MAX_HORIZONTAL_GAP,
                       vertical_threshold: float = VERTICAL_THRESHOLD) -> List[Dict]:
    """
    Combine partial embedded text in the same line if they are close horizontally.
    """
    sorted_entries = sorted(
        embedded_entries,
        key=lambda e: (e.get("page_index", 0), e["bbox"][1], e["bbox"][0])
    )

    fused = []
    pending = None

    for entry in sorted_entries:
        if not pending:
            pending = entry
            continue

        # same page
        if pending["page_index"] == entry["page_index"]:
            # check vertical alignment
            if abs(pending["bbox"][1] - entry["bbox"][1]) < vertical_threshold:
                # check horizontal gap
                gap = entry["bbox"][0] - pending["bbox"][2]
                if 0 <= gap < max_horizontal_gap:
                    # fuse
                    pending["text"] += entry["text"]
                    pending["bbox"] = [
                        min(pending["bbox"][0], entry["bbox"][0]),
                        min(pending["bbox"][1], entry["bbox"][1]),
                        max(pending["bbox"][2], entry["bbox"][2]),
                        max(pending["bbox"][3], entry["bbox"][3])
                    ]
                    pending["confidence"] = max(pending.get("confidence",1.0),
                                                entry.get("confidence",1.0))
                    continue

        fused.append(pending)
        pending = entry

    if pending:
        fused.append(pending)

    return fused

###########################################
# Simple Overlap & Similarity for Merging #
###########################################

def text_similarity(a: str, b: str) -> float:
    seq = difflib.SequenceMatcher(None, a, b)
    return seq.ratio()

def iou(bbox_a, bbox_b) -> float:
    x0_a, y0_a, x1_a, y1_a = bbox_a
    x0_b, y0_b, x1_b, y1_b = bbox_b

    inter_x0 = max(x0_a, x0_b)
    inter_y0 = max(y0_a, y0_b)
    inter_x1 = min(x1_a, x1_b)
    inter_y1 = min(y1_a, y1_b)

    inter_w = max(0, inter_x1 - inter_x0)
    inter_h = max(0, inter_y1 - inter_y0)
    inter_area = inter_w * inter_h

    area_a = (x1_a - x0_a) * (y1_a - y0_a)
    area_b = (x1_b - x0_b) * (y1_b - y0_b)
    union_area = area_a + area_b - inter_area

    if union_area == 0:
        return 0.0
    return inter_area / union_area

def choose_better_bbox(bbox_a, bbox_b):
    return [
        min(bbox_a[0], bbox_b[0]),
        min(bbox_a[1], bbox_b[1]),
        max(bbox_a[2], bbox_b[2]),
        max(bbox_a[3], bbox_b[3])
    ]

###############################################
# Merging Embedded & OCR to remove Duplicates #
###############################################

def fuse_embedded_and_ocr(embedded_entries: List[Dict],
                          ocr_entries: List[Dict],
                          iou_threshold: float = IOU_THRESHOLD,
                          sim_threshold: float = SIM_THRESHOLD) -> List[Dict]:
    """
    Attempt to unify embedded & OCR entries if bounding boxes overlap significantly
    and text is similar.
    - Prefer embedded text if conflict,
    - Keep OCR's image_path for the fused record.
    - Skip any OCR entries missing 'bbox'.
    """
    fused_results = []
    used_ocr_indices = set()

    for emb in embedded_entries:
        # skip if no bounding box
        if "bbox" not in emb:
            fused_results.append(emb)
            continue

        best_match_idx = None
        best_score = 0.0

        for i, ocr in enumerate(ocr_entries):
            # skip if missing bbox
            if "bbox" not in ocr:
                continue

            # skip if page mismatch
            if ocr.get("page_index", -1) != emb.get("page_index", -1):
                continue

            # check IOU
            iou_val = iou(emb["bbox"], ocr["bbox"])
            if iou_val < iou_threshold:
                continue

            # check text similarity
            sim = text_similarity(emb["text"], ocr["text"])
            if sim > best_score:
                best_score = sim
                best_match_idx = i

        if best_match_idx is not None and best_score > sim_threshold:
            used_ocr_indices.add(best_match_idx)
            ocr_match = ocr_entries[best_match_idx]

            new_bbox = choose_better_bbox(emb["bbox"], ocr_match["bbox"])
            new_conf = max(emb.get("confidence",1.0), ocr_match.get("confidence",1.0))

            fused_results.append({
                "page_index": emb["page_index"],
                "bbox": new_bbox,
                "text": emb["text"],  # prefer embedded text
                "source": "fused",
                "confidence": new_conf,
                "image_path": ocr_match.get("image_path"),
                "fused_from": ["embedded", "ocr"]
            })
        else:
            # No suitable match
            fused_results.append(emb)

    # Add all OCR entries never used
    for i, ocr in enumerate(ocr_entries):
        if i not in used_ocr_indices:
            fused_results.append(ocr)

    return fused_results

####################################
# Add tile_filename to tile_meta   #
####################################

def add_tile_filename_to_meta(tile_meta_path):
    with open(tile_meta_path, "r", encoding="utf-8") as f:
        tile_meta_data = json.load(f)

    for entry in tile_meta_data:
        if "tile_filename" not in entry and "image_path" in entry:
            entry["tile_filename"] = os.path.basename(entry["image_path"])

    with open(tile_meta_path, "w", encoding="utf-8") as f:
        json.dump(tile_meta_data, f, indent=4)

    print(f"Updated tile_meta.json with tile_filename: {tile_meta_path}")

#########################################
# Assign tile_filename to embedded text #
#########################################

def find_tile_for_bbox(text_bbox, page_idx, tile_meta):
    x_min, y_min, x_max, y_max = text_bbox
    center_x = 0.5 * (x_min + x_max)
    center_y = 0.5 * (y_min + y_max)

    for tile in tile_meta:
        if tile["page_index"] != page_idx:
            continue

        pdf_min_x = tile["x_start"] / tile["zoom_factor"]
        pdf_min_y = tile["y_start"] / tile["zoom_factor"]
        pdf_max_x = (tile["x_start"] + tile["tile_width"]) / tile["zoom_factor"]
        pdf_max_y = (tile["y_start"] + tile["tile_height"]) / tile["zoom_factor"]

        if (pdf_min_x <= center_x <= pdf_max_x) and (pdf_min_y <= center_y <= pdf_max_y):
            # This tile encloses the center of the bounding box
            return tile

    return None

def build_tile_path(tile_filename: str, page_idx: int):
    return os.path.join(f"page_{page_idx}", tile_filename)

def assign_tile_to_embedded(embedded_data: List[Dict], tile_meta_data: List[Dict]):
    for emb in embedded_data:
        if "bbox" not in emb or "page_index" not in emb:
            continue

        page_idx = emb["page_index"]
        tile_match = find_tile_for_bbox(emb["bbox"], page_idx, tile_meta_data)
        if tile_match:
            emb["tile_filename"] = tile_match["tile_filename"]
            emb["image_path"] = build_tile_path(tile_match["tile_filename"], page_idx)
        else:
            emb["tile_filename"] = None
            emb["image_path"] = None

###########################################
# Combine overlapping OCR entries (option) #
###########################################

def combine_overlapping_ocr_entries(ocr_entries: List[Dict]) -> List[Dict]:
    combined = []
    used = set()

    for i, entry_a in enumerate(ocr_entries):
        if i in used:
            continue
        if "bbox" not in entry_a:
            combined.append(entry_a)
            used.add(i)
            continue

        best_j = None
        best_iou = 0.0

        for j, entry_b in enumerate(ocr_entries):
            if j <= i or j in used:
                continue
            if "bbox" not in entry_b:
                continue

            if entry_a.get("page_index") != entry_b.get("page_index"):
                continue

            iou_val = iou(entry_a["bbox"], entry_b["bbox"])
            if iou_val > 0.6 and iou_val > best_iou:
                best_iou = iou_val
                best_j = j

        if best_j is not None:
            entry_b = ocr_entries[best_j]
            merged_text = (entry_a["text"] or "") + " " + (entry_b["text"] or "")
            new_bbox = [
                min(entry_a["bbox"][0], entry_b["bbox"][0]),
                min(entry_a["bbox"][1], entry_b["bbox"][1]),
                max(entry_a["bbox"][2], entry_b["bbox"][2]),
                max(entry_a["bbox"][3], entry_b["bbox"][3])
            ]
            new_conf = max(entry_a.get("confidence",1.0), entry_b.get("confidence",1.0))
            new_path = entry_a.get("image_path") or entry_b.get("image_path")
            new_tile = entry_a.get("tile_filename") or entry_b.get("tile_filename")

            combined.append({
                "page_index": entry_a.get("page_index", 0),
                "bbox": new_bbox,
                "text": merged_text.strip(),
                "source": "ocr",
                "confidence": new_conf,
                "image_path": new_path,
                "tile_filename": new_tile
            })
            used.add(i)
            used.add(best_j)
        else:
            combined.append(entry_a)
            used.add(i)

    for idx, e in enumerate(ocr_entries):
        if idx not in used:
            combined.append(e)

    return combined

###################################
# Main merge_text function
###################################

def merge_text(
    embedded_path: str,
    ocr_path: str,
    tile_meta_path: str,
    output_path: str
):
    """
    Merges embedded text and OCR results into a single JSON file, ensuring:
      1) Fused partial embedded text
      2) Spellchecking
      3) BBox + tile matching for embedded
      4) Optional merging of embedded + OCR if bounding boxes overlap
      5) Skips or logs any snippet missing 'bbox'
    """
    # Load domain dictionary if available
    load_domain_dictionary(DOMAIN_DICTIONARY_PATH)

    required_files = {
        "embedded_text": embedded_path,
        "ocr_results": ocr_path,
        "tile_metadata": tile_meta_path,
    }
    for key, file in required_files.items():
        if not os.path.isfile(file):
            raise FileNotFoundError(f"Missing input file: {file} ({key})")

    # Load data
    with open(embedded_path, "r", encoding="utf-8") as f:
        embedded_data = json.load(f)
    debug_check_for_none_text(embedded_data, label="Initial embedded_data")

    with open(ocr_path, "r", encoding="utf-8") as f:
        ocr_data = json.load(f)
    debug_check_for_none_text(ocr_data, label="Initial ocr_data")

    with open(tile_meta_path, "r", encoding="utf-8") as f:
        tile_meta_data = json.load(f)

    # Possibly add tile_filename to tile_meta if missing
    add_tile_filename_to_meta(tile_meta_path)
    # Reload tile_meta_data after we updated it
    with open(tile_meta_path, "r", encoding="utf-8") as f:
        tile_meta_data = json.load(f)

    # Assign tile references to embedded
    assign_tile_to_embedded(embedded_data, tile_meta_data)

    # 1) Fuse partial embedded text lines
    fused_embedded = fuse_embedded_text(embedded_data)
    debug_check_for_none_text(fused_embedded, label="fused_embedded after fuse_embedded_text")

    # 2) Spellcheck embedded text
    for e in fused_embedded:
        e["text"] = advanced_spellcheck(e["text"] or "")
    debug_check_for_none_text(fused_embedded, label="fused_embedded after advanced_spellcheck")

    # 3) If partial merges are allowed, combine overlapping OCR
    if ALLOW_PARTIAL_MERGE:
        ocr_data = combine_overlapping_ocr_entries(ocr_data)
        debug_check_for_none_text(ocr_data, label="ocr_data after combine_overlapping_ocr_entries")

    # 4) Fuse embedded & OCR by bounding box + text similarity
    merged_results = fuse_embedded_and_ocr(fused_embedded, ocr_data)
    debug_check_for_none_text(merged_results, label="merged_results after fuse_embedded_and_ocr")

    # Save final
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_results, f, indent=2)

    print(f"Merged results saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python merge_text.py <embedded_path> <ocr_path> <tile_meta_path> <output_path>")
        sys.exit(1)

    embedded_path = os.path.normpath(sys.argv[1])
    ocr_path = os.path.normpath(sys.argv[2])
    tile_meta_path = os.path.normpath(sys.argv[3])
    output_path = os.path.normpath(sys.argv[4])

    print(f"Running merge_text with arguments:")
    print(f"  Embedded: {embedded_path}")
    print(f"  OCR: {ocr_path}")
    print(f"  Tile Meta: {tile_meta_path}")
    print(f"  Output: {output_path}")

    import traceback

    try:
        merge_text(embedded_path, ocr_path, tile_meta_path, output_path)
    except Exception as e:
        print("[DEBUG] Caught an exception in merge_text main:")
        traceback.print_exc()
        sys.exit(1)