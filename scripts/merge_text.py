#!/usr/bin/env python
import os
import sys
import json
import difflib
from typing import List, Dict, Any, Optional
from spellchecker import SpellChecker

#############
# Parameters #
#############

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
        # Some entries might not have 'text' at all, so be safe
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

        # uppercase words can cause issues if domain-specific
        # let's do a naive approach: if it's all caps, try lowercasing
        # then correct, then uppercase again.
        if token.isupper():
            guess = spell.correction(token.lower())
            corrected = guess.upper() if guess else token  # fallback to original token
        else:
            guess = spell.correction(token)
            corrected = guess if guess else token  # fallback to original token

        # If somehow corrected is still None, force it to token
        if corrected is None:
            corrected = token

        corrected_tokens.append(corrected)

    # final join
    return " ".join(corrected_tokens)

####################################
# Embedded Text Fusing (same line) #
####################################

def fuse_embedded_text(embedded_entries: List[Dict], 
                       max_horizontal_gap: float = MAX_HORIZONTAL_GAP,
                       vertical_threshold: float = VERTICAL_THRESHOLD) -> List[Dict]:
    """
    Combine partial embedded text in the same line if they are close horizontally.
    :param embedded_entries: list of { page_index, bbox, text, ... }
    :param max_horizontal_gap: allowable gap in PDF coords to consider text part of same word
    :param vertical_threshold: allowable vertical offset to consider text on the same line
    :return: new list of fused entries
    """
    # 1) Sort by page, then top coordinate (y0), then left x0
    sorted_entries = sorted(
        embedded_entries,
        key=lambda e: (e.get("page_index", 0), e["bbox"][1], e["bbox"][0])
    )

    fused = []
    pending = None

    for entry in sorted_entries:
        if not pending:
            # start a new group
            pending = entry
            continue

        # check if same page
        if pending["page_index"] == entry["page_index"]:
            # check vertical alignment
            if abs(pending["bbox"][1] - entry["bbox"][1]) < vertical_threshold:
                # check horizontal gap (the distance between pending's x2 and entry's x0)
                gap = entry["bbox"][0] - pending["bbox"][2]
                if 0 <= gap < max_horizontal_gap:
                    # fuse
                    pending["text"] += entry["text"]
                    # expand bounding box
                    pending["bbox"] = [
                        min(pending["bbox"][0], entry["bbox"][0]),
                        min(pending["bbox"][1], entry["bbox"][1]),
                        max(pending["bbox"][2], entry["bbox"][2]),
                        max(pending["bbox"][3], entry["bbox"][3])
                    ]
                    # optionally merge confidence
                    pending["confidence"] = max(pending.get("confidence", 1.0),
                                                entry.get("confidence", 1.0))
                    continue

        # if we cannot fuse, push pending to fused list
        fused.append(pending)
        pending = entry

    # add last pending
    if pending:
        fused.append(pending)

    return fused

##########################################
# Simple Overlap & Similarity for Merging#
##########################################

def text_similarity(a: str, b: str) -> float:
    """
    Returns a float from 0 to 1 indicating how similar two strings are,
    using difflib.
    """
    import difflib
    seq = difflib.SequenceMatcher(None, a, b)
    return seq.ratio()

def iou(bbox_a, bbox_b) -> float:
    """
    Intersection over Union for two bounding boxes (x0,y0,x1,y1).
    """
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
    """
    Use the union of two bounding boxes as the 'fused' bbox.
    """
    return [
        min(bbox_a[0], bbox_b[0]),
        min(bbox_a[1], bbox_b[1]),
        max(bbox_a[2], bbox_b[2]),
        max(bbox_a[3], bbox_b[3])
    ]

#############################################
# Merging Embedded & OCR to remove Duplicates
#############################################

def fuse_embedded_and_ocr(embedded_entries: List[Dict], 
                          ocr_entries: List[Dict],
                          iou_threshold: float = IOU_THRESHOLD,
                          sim_threshold: float = SIM_THRESHOLD) -> List[Dict]:
    """
    Attempt to unify embedded & OCR entries if bounding boxes overlap significantly
    and text is similar. 
    - Prefer embedded text's content if there's conflict,
    - Keep OCR's image_path for the fused record.
    """
    fused_results = []
    used_ocr_indices = set()

    for emb in embedded_entries:
        best_match_idx = None
        best_score = 0.0

        for i, ocr in enumerate(ocr_entries):
            if ocr["page_index"] != emb["page_index"]:
                continue

            # 1) Check bounding box overlap
            iou_val = iou(emb["bbox"], ocr["bbox"])
            if iou_val < iou_threshold:
                continue

            # 2) Check text similarity
            sim = text_similarity(emb["text"], ocr["text"])
            if sim > best_score:
                best_score = sim
                best_match_idx = i

        if best_match_idx is not None and best_score > sim_threshold:
            # Fuse them
            used_ocr_indices.add(best_match_idx)
            ocr_match = ocr_entries[best_match_idx]

            fused_results.append({
                "page_index": emb["page_index"],
                "bbox": choose_better_bbox(emb["bbox"], ocr_match["bbox"]),
                "text": emb["text"],  # prefer embedded text
                "source": "fused",
                "confidence": max(emb.get("confidence", 1.0), ocr_match.get("confidence", 1.0)),
                "image_path": ocr_match.get("image_path", None), 
                "fused_from": ["embedded", "ocr"]
            })
        else:
            # No suitable match - keep the embedded as is
            fused_results.append(emb)

    # Add all OCR entries that never got used in a fusion
    for i, ocr in enumerate(ocr_entries):
        if i not in used_ocr_indices:
            fused_results.append(ocr)

    return fused_results


############################################
# Assign image_path to Embedded Text BBoxes
############################################

def find_tile_for_bbox(text_bbox, page_idx, tile_meta):
    """
    Finds which tile_filename encloses the text_bbox for the same page_idx.
    text_bbox: [x0, y0, x1, y1] in PDF coords.
    tile_meta: list of { 'page_index','x_start','y_start','tile_width','tile_height','zoom_factor','tile_filename' }
    Return tile_filename or None if not found.
    """
    x_min, y_min, x_max, y_max = text_bbox
    center_x = 0.5*(x_min + x_max)
    center_y = 0.5*(y_min + y_max)

    for tile in tile_meta:
        if tile["page_index"] != page_idx:
            continue

        pdf_min_x = tile["x_start"] / tile["zoom_factor"]
        pdf_min_y = tile["y_start"] / tile["zoom_factor"]
        pdf_max_x = (tile["x_start"] + tile["tile_width"]) / tile["zoom_factor"]
        pdf_max_y = (tile["y_start"] + tile["tile_height"]) / tile["zoom_factor"]

        if (pdf_min_x <= center_x <= pdf_max_x) and (pdf_min_y <= center_y <= pdf_max_y):
            return tile["tile_filename"]

    return None

###################################################
# Main merge_text.py function to unify everything #
###################################################

def merge_text(
    embedded_path: str,
    ocr_path: str,
    tile_meta_path: str,
    output_path: str
):
    """
    Merges embedded text and OCR results into a single JSON file, with:
      1) fused partial embedded text
      2) advanced spellchecking
      3) bounding box -> tile matching for embedded text
      4) optional fusing of embedded & OCR if needed
    """
    # Load domain dictionary
    load_domain_dictionary(DOMAIN_DICTIONARY_PATH)

    # Check input files
    required_files = {
        "embedded_text": embedded_path,
        "ocr_results": ocr_path,
        "tile_metadata": tile_meta_path,
    }
    for key, f_path in required_files.items():
        if not os.path.isfile(f_path):
            raise FileNotFoundError(f"Missing required file: {f_path} for {key}")

    # Load data
    with open(embedded_path, 'r', encoding='utf-8') as f:
        embedded_data = json.load(f)
    debug_check_for_none_text(embedded_data, label="Initial embedded_data")
    with open(ocr_path, 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)
    debug_check_for_none_text(ocr_data, label="Initial ocr_data")
    with open(tile_meta_path, 'r', encoding='utf-8') as f:
        tile_metadata = json.load(f)

    # 1) FUSE partial EMBEDDED text
    fused_embedded = fuse_embedded_text(embedded_data)
    debug_check_for_none_text(fused_embedded, label="fused_embedded after fuse_embedded_text")

    # 2) SPELLCHECK embedded text
    for emb in fused_embedded:
        emb["text"] = advanced_spellcheck(emb["text"] or "")
    debug_check_for_none_text(fused_embedded, label="fused_embedded after spellcheck")

    # 3) Assign image_path to embedded text based on bounding box -> tile
    #    This helps avoid "page_index=0, image_path=None"
    for emb in fused_embedded:
        page_idx = emb.get("page_index", 0)
        tile_fn = find_tile_for_bbox(emb["bbox"], page_idx, tile_metadata)
        if tile_fn:
            emb["image_path"] = build_tile_path(tile_fn, page_idx, tile_metadata)
        else:
            emb["image_path"] = None
    debug_check_for_none_text(fused_embedded, label="fused_embedded after tile assignment")

    # 4) Combine partial text overlaps within OCR
    if ALLOW_PARTIAL_MERGE:
        ocr_data = combine_overlapping_ocr_entries(ocr_data)
        debug_check_for_none_text(ocr_data, label="ocr_data after combine_overlapping_ocr_entries")

    # 5) Fuse EMBEDDED & OCR
    merged_results = fuse_embedded_and_ocr(fused_embedded, ocr_data)
    debug_check_for_none_text(merged_results, label="merged_results after fuse_embedded_and_ocr")

    # Save the final results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_results, f, indent=2)

    print(f"Merged results saved to {output_path}")


############################
# Additional Helper Functions
############################

def combine_overlapping_ocr_entries(ocr_entries: List[Dict]) -> List[Dict]:
    """
    Attempts to combine OCR entries that overlap significantly 
    (like phone numbers, partial lines, etc.).
    This is a naive approach:
      - If two entries have IOU > 0.6 and share the same page_index,
        we merge them into a single record (combining text).
      - We skip or leave intact any entry missing a 'bbox'.

    Minimal changes were made to skip items without bounding boxes,
    avoiding KeyErrors and data loss for valid snippet entries.
    """
    combined = []
    used = set()

    for i, entry_a in enumerate(ocr_entries):
        if i in used:
            continue

        # Skip if no bounding box or invalid
        if "bbox" not in entry_a or not entry_a["bbox"]:
            # We'll keep the entry as-is but won't attempt merging
            combined.append(entry_a)
            used.add(i)
            continue

        best_j = None
        best_iou = 0.0

        for j, entry_b in enumerate(ocr_entries):
            if j <= i or j in used:
                continue

            # Skip if no bounding box or invalid
            if "bbox" not in entry_b or not entry_b["bbox"]:
                continue

            # Must be on same page
            if entry_a["page_index"] != entry_b["page_index"]:
                continue

            # Check IOU
            iou_val = iou(entry_a["bbox"], entry_b["bbox"])
            if iou_val > 0.6:
                # naive: let's combine these
                if iou_val > best_iou:
                    best_iou = iou_val
                    best_j = j

        if best_j is not None:
            entry_b = ocr_entries[best_j]
            # Merge entry_a & entry_b
            merged_text = (entry_a["text"] or "") + " " + (entry_b["text"] or "")
            new_bbox = [
                min(entry_a["bbox"][0], entry_b["bbox"][0]),
                min(entry_a["bbox"][1], entry_b["bbox"][1]),
                max(entry_a["bbox"][2], entry_b["bbox"][2]),
                max(entry_a["bbox"][3], entry_b["bbox"][3])
            ]
            new_conf = max(entry_a.get("confidence",1.0), entry_b.get("confidence",1.0))
            new_path = entry_a.get("image_path") or entry_b.get("image_path")

            combined.append({
                "page_index": entry_a["page_index"],
                "bbox": new_bbox,
                "text": merged_text.strip(),
                "source": "ocr",
                "confidence": new_conf,
                "image_path": new_path
            })

            used.add(i)
            used.add(best_j)
        else:
            # no suitable merge, keep entry_a as-is
            combined.append(entry_a)
            used.add(i)

    # Add any leftover OCR entries not yet used
    for idx, entry in enumerate(ocr_entries):
        if idx not in used:
            combined.append(entry)

    return combined


def build_tile_path(tile_fn: str, page_idx: int, tile_metadata: List[Dict]) -> str:
    """
    Builds a full or relative path to the tile image, e.g. 
    "C:/some/path/results/<plan_id>/page_2/tile_3000_0.png"
    Adapt as needed if your directory structure differs.
    For now, we do something naive:
    """
    # We'll guess the plan directory structure is handled by the orchestrator.
    # If you have a known root like "C:/Users/shika/modeled-homes-hvac/data/output/results/<plan_name>/"
    # you might want to pass that in as a parameter. 
    # For demonstration, we'll just do: f"page_{page_idx}/{tile_fn}"

    return os.path.join(f"page_{page_idx}", tile_fn)


##################
# Entry Point CLI #
##################

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python merge_text.py <embedded_path> <ocr_path> <tile_meta_path> <output_path>")
        sys.exit(1)

    embedded_path = os.path.normpath(sys.argv[1])
    ocr_path = os.path.normpath(sys.argv[2])
    tile_meta_path = os.path.normpath(sys.argv[3])
    output_path = os.path.normpath(sys.argv[4])

    print("Running merge_text with arguments:")
    print(f"Embedded: {embedded_path}")
    print(f"OCR: {ocr_path}")
    print(f"Tile Meta: {tile_meta_path}")
    print(f"Output: {output_path}")

    import traceback

    try:
        merge_text(embedded_path, ocr_path, tile_meta_path, output_path)
    except Exception as e:
            print("[DEBUG] Caught an exception in merge_text main:")
            traceback.print_exc()
            sys.exit(1)