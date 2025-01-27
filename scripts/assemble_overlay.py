import os
import sys
import json
import logging
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def assemble_overlay(plan_id, plan_dir, output_path):
    """
    Aggregates tile metadata, text, lines, dimension data into a single JSON
    for each tile, ensuring we have a unified record ready for final embedding.

    :param plan_id: Unique identifier (string) for this PDF plan.
    :param plan_dir: Directory containing intermediate JSON files (tile_meta.json, categorized_results.json, etc.).
    :param output_path: Path to write final_overlays.json.
    """

    # ---- 1) Load tile_meta.json ----
    tile_meta_file = os.path.join(plan_dir, "tile_meta.json")
    if not os.path.isfile(tile_meta_file):
        logging.error(f"tile_meta.json not found at: {tile_meta_file}")
        return

    with open(tile_meta_file, "r", encoding="utf-8") as f:
        tile_meta = json.load(f)

    # We'll store all final overlay entries in a dict keyed by (page_index, tile_filename)
    # so we can easily merge data from other files.
    overlay_map = {}

    for tile_info in tile_meta:
        page_idx = tile_info.get("page_index")
        tile_fn = tile_info.get("tile_filename", "")
        tile_key = (page_idx, tile_fn)

        # example image path (adjust if needed)
        # e.g. "C:/.../page_0/tile_3000_6000.png"
        image_path = os.path.join(plan_dir, f"page_{page_idx}", tile_fn)

        overlay_map[tile_key] = {
            "planId": plan_id,
            "pageIndex": page_idx,
            "tileIndex": tile_info.get("tile_index"),
            "imagePath": image_path,  # or any relative/absolute path
            "pdfCoords": {
                "x_start": tile_info.get("x_start"),
                "y_start": tile_info.get("y_start"),
                "zoom_factor": tile_info.get("zoom_factor"),
                "tile_width": tile_info.get("tile_width"),
                "tile_height": tile_info.get("tile_height"),
            },
            "overlayData": {
                "textBlocks": [],
                "dimensions": [],
                "lines": [],
                "isBlank": True  # we'll set to False if we find text or lines
            }
        }

    # ---- 2) Merge in text data from categorized_results.json (if present) ----
    categorized_file = os.path.join(plan_dir, "categorized_results.json")
    if os.path.isfile(categorized_file):
        with open(categorized_file, "r", encoding="utf-8") as f:
            categorized_results = json.load(f)

        for entry in categorized_results:
            image_path = entry.get("image_path")
            if not image_path:
                continue

            # parse out page_idx + tile_filename from the path
            # e.g. ".../page_0/tile_3000_6000.png"
            page_idx, tile_fn = extract_page_tile(plan_dir, image_path)
            tile_key = (page_idx, tile_fn)

            if tile_key in overlay_map:
                text_item = {
                    "text": entry.get("text", ""),
                    "bbox": entry.get("bbox", []),
                    "confidence": entry.get("confidence", 1.0)
                }
                overlay_map[tile_key]["overlayData"]["textBlocks"].append(text_item)
                # Mark tile as not blank
                overlay_map[tile_key]["overlayData"]["isBlank"] = False

    # ---- 3) Merge line data (line_detection_results.json) if present ----
    lines_file = os.path.join(plan_dir, "line_detection_results.json")
    if os.path.isfile(lines_file):
        with open(lines_file, "r", encoding="utf-8") as f:
            line_data = json.load(f)

        # line_data might be structured differently; adapt as needed
        for line_entry in line_data:
            image_path = line_entry.get("image_path")
            if not image_path:
                continue

            page_idx, tile_fn = extract_page_tile(plan_dir, image_path)
            tile_key = (page_idx, tile_fn)
            if tile_key in overlay_map:
                # example line structure: { "line": [[x1, y1], [x2, y2]], ...}
                line_coords = line_entry.get("line", [])
                if line_coords:
                    overlay_map[tile_key]["overlayData"]["lines"].append(line_coords)
                    overlay_map[tile_key]["overlayData"]["isBlank"] = False

    # ---- 4) Merge dimension linking (linked_dimensions.json) if present ----
    dim_file = os.path.join(plan_dir, "linked_dimensions.json")
    if os.path.isfile(dim_file):
        with open(dim_file, "r", encoding="utf-8") as f:
            dim_data = json.load(f)

        for dim_entry in dim_data:
            image_path = dim_entry.get("image_path")
            if not image_path:
                continue

            page_idx, tile_fn = extract_page_tile(plan_dir, image_path)
            tile_key = (page_idx, tile_fn)
            if tile_key in overlay_map:
                # example dimension structure
                dim_item = {
                    "dimText": dim_entry.get("text", ""),
                    "bbox": dim_entry.get("bbox", []),
                    "confidence": dim_entry.get("confidence", 1.0),
                    "nearest_line": dim_entry.get("nearest_line", None),
                    "distance": dim_entry.get("distance", None)
                }
                overlay_map[tile_key]["overlayData"]["dimensions"].append(dim_item)
                overlay_map[tile_key]["overlayData"]["isBlank"] = False

    # ---- 5) Convert overlay_map dict to a list of tile overlay objects ----
    final_overlays = list(overlay_map.values())

    # ---- 6) Write out final_overlays.json ----
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_overlays, f, indent=2)

    logging.info(f"Final overlay data written to: {output_path}")

def extract_page_tile(plan_dir, image_path):
    """
    Attempts to parse page_index and tile_filename from a full image_path.
    e.g. image_path = ".../page_0/tile_3000_6000.png"

    Returns (page_index, tile_filename) so we can map it back to overlay_map.
    """
    # This is just a naive approach; adapt to your path structure.
    # We'll look for "/page_{idx}/tile_*" in the path.

    # get relative path from plan_dir
    rel_path = os.path.relpath(image_path, plan_dir)
    parts = rel_path.split(os.sep)
    # Expect: [ "page_0", "tile_3000_6000.png" ]
    if len(parts) >= 2 and parts[0].startswith("page_"):
        page_str = parts[0].replace("page_", "")
        page_idx = int(page_str) if page_str.isdigit() else 0
        tile_fn = parts[1]  # "tile_3000_6000.png"
        return (page_idx, tile_fn)
    else:
        # fallback
        return (0, os.path.basename(image_path))

if __name__ == "__main__":
    """
    Usage: python assemble_overlay.py <plan_id> <plan_dir> <output_file>
    Example:
        python assemble_overlay.py "MyPlan123" "C:/plans/MyPlan123" "C:/plans/MyPlan123/final_overlays.json"
    """
    if len(sys.argv) < 4:
        print("Usage: python assemble_overlay.py <plan_id> <plan_dir> <output_file>")
        sys.exit(1)

    plan_id = sys.argv[1]
    plan_dir = os.path.normpath(sys.argv[2])
    output_path = os.path.normpath(sys.argv[3])

    try:
        assemble_overlay(plan_id, plan_dir, output_path)
    except Exception as e:
        logging.error(f"Error assembling overlay: {e}")
        sys.exit(1)