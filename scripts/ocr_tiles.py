import os
import sys
import re
import json
import argparse
from mmocr.apis.inferencers.mmocr_inferencer import MMOCRInferencer

def chunk_polygon(flat_list):
    """
    Converts a single flat list [x1, y1, x2, y2, ...] into a list of [x, y] pairs.
    Returns None if length is odd or can't be parsed.
    """
    if len(flat_list) % 2 != 0:
        return None
    pairs = []
    for i in range(0, len(flat_list), 2):
        pairs.append([flat_list[i], flat_list[i+1]])
    return pairs

def flatten_ocr_result(ocr_result, plan_id, page_idx, image_path, x_start, y_start, final_snippets):
    """
    Flattens the raw 'ocr_result' dictionary into snippet-level bounding box entries.
    Each entry has a top-level 'bbox', 'text', 'confidence', and 'source' = 'ocr'.
    """
    if not ocr_result:
        # If no text predicted
        final_snippets.append({
            "plan_id": plan_id,
            "page_index": page_idx,
            "image_path": image_path,
            "x_start": x_start,
            "y_start": y_start,
            "bbox": None,
            "text": "",
            "confidence": 0.0,
            "source": "ocr"
        })
        return

    predictions = ocr_result.get("predictions", [])
    for pred in predictions:
        det_polygons = pred.get("det_polygons", [])
        rec_texts = pred.get("rec_texts", [])
        rec_scores = pred.get("rec_scores", [])

        # Only iterate up to the min length to avoid index mismatches
        max_len = min(len(det_polygons), len(rec_texts), len(rec_scores))

        for i in range(max_len):
            poly = det_polygons[i]
            snippet_text = rec_texts[i]
            snippet_conf = rec_scores[i]

            # 1) If 'poly' isn't a list, skip
            if not isinstance(poly, list):
                final_snippets.append({
                    "plan_id": plan_id,
                    "page_index": page_idx,
                    "image_path": image_path,
                    "x_start": x_start,
                    "y_start": y_start,
                    "error": "poly is not a list",
                    "invalid_value": str(poly),
                    "source": "ocr"
                })
                continue

            # 2) If 'poly' is a single list of floats => chunk
            # or if it's a nested list already => handle it
            if all(isinstance(val, (float, int)) for val in poly):
                # chunk 8 floats or variable length into [ [x,y], [x2,y2], ...]
                pair_list = chunk_polygon(poly)
                if pair_list is None:
                    final_snippets.append({
                        "plan_id": plan_id,
                        "page_index": page_idx,
                        "image_path": image_path,
                        "error": "Cannot chunk flattened polygon",
                        "invalid_value": str(poly),
                        "source": "ocr"
                    })
                    continue
                xs = [pt[0] for pt in pair_list]
                ys = [pt[1] for pt in pair_list]
            elif all(isinstance(pt, list) and len(pt) == 2 for pt in poly):
                # Already a list of [x,y]
                xs = [pt[0] for pt in poly]
                ys = [pt[1] for pt in poly]
            else:
                # Invalid format
                final_snippets.append({
                    "plan_id": plan_id,
                    "page_index": page_idx,
                    "image_path": image_path,
                    "error": "Invalid polygon format",
                    "invalid_value": str(poly),
                    "source": "ocr"
                })
                continue

            # 3) Build bounding box
            bbox = [min(xs), min(ys), max(xs), max(ys)]

            # 4) Ensure text is string
            if not isinstance(snippet_text, str):
                snippet_text = str(snippet_text)
            # 5) Ensure confidence is float
            if not isinstance(snippet_conf, (float, int)):
                snippet_conf = 1.0

            # 6) Append final snippet
            final_snippets.append({
                "plan_id": plan_id,
                "page_index": page_idx,
                "image_path": image_path,
                "x_start": x_start,
                "y_start": y_start,
                "bbox": bbox,
                "text": snippet_text,
                "confidence": float(snippet_conf),
                "source": "ocr"
            })

def infer_page_index(image_path):
    """
    Extracts page index from the filename or path.
    """
    match = re.search(r'page_(\d+)', image_path)
    if match:
        return int(match.group(1))
    return None

def infer_tile_offsets(image_filename):
    """
    Extracts x_start, y_start from tile filename (e.g., tile_3000_4500.png).
    """
    match = re.search(r'tile_(\d+)_(\d+)\.png', image_filename)
    if match:
        x_start = int(match.group(1))
        y_start = int(match.group(2))
        return (x_start, y_start)
    return (None, None)

def infer_plan_id_from_path(image_path):
    """
    Folder structure example:
      .../results/<plan_id>/page_0/tile_0_0.png
    We parse plan_id from after the 'results' folder
    """
    path_parts = os.path.normpath(image_path).split(os.sep)
    try:
        idx = path_parts.index("results")
        plan_id = path_parts[idx + 1]
        return plan_id
    except (ValueError, IndexError):
        return None

def ocr_tiles(tiles_dir, output_path, device="cpu", save_vis=False):
    """
    Performs OCR on all tiles in the specified directory, flattening snippet-level
    bounding boxes into 'bbox', 'text', 'confidence', etc. for each polygon. 
    Also saves the raw 'ocr_result' to a separate JSON file for further debugging.
    """
    if not os.path.isdir(tiles_dir):
        raise NotADirectoryError(f"Tiles directory not found: {tiles_dir}")

    # We'll store snippet-level results in final_snippets
    final_snippets = []
    # We'll store raw results in raw_ocr_dict, keyed by tile filename
    raw_ocr_dict = {}

    # Set up directories and MMOCR model
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    visualization_dir = os.path.join(project_root, "data", "output", "visualizations")
    os.makedirs(visualization_dir, exist_ok=True)

    mmocr = MMOCRInferencer(
        det="DBNetPP",
        rec="ABINet",
        kie="SDMGR",
        device=device
    )

    for root, _, files in os.walk(tiles_dir):
        for file in sorted(files):
            if file.endswith(".png"):
                image_path = os.path.join(root, file)
                print(f"Processing tile: {image_path}")

                plan_id = infer_plan_id_from_path(image_path)
                page_idx = infer_page_index(image_path)
                x_start, y_start = infer_tile_offsets(file)

                try:
                    # Run MMOCR with optional save_vis
                    ocr_result = mmocr(image_path, save_vis=save_vis, out_dir=visualization_dir)

                    # Save raw result in raw_ocr_dict
                    tile_key = os.path.basename(image_path)
                    raw_ocr_dict[tile_key] = ocr_result

                    # Flatten bounding boxes from the raw result
                    flatten_ocr_result(
                        ocr_result,
                        plan_id=plan_id,
                        page_idx=page_idx if page_idx is not None else 0,
                        image_path=image_path,
                        x_start=x_start if x_start is not None else 0,
                        y_start=y_start if y_start is not None else 0,
                        final_snippets=final_snippets
                    )

                except Exception as e:
                    final_snippets.append({
                        "plan_id": plan_id,
                        "page_index": page_idx,
                        "image_path": image_path,
                        "x_start": x_start,
                        "y_start": y_start,
                        "error": str(e),
                        "source": "ocr"
                    })
                    print(f"Error processing {image_path}: {e}")

    # 1) Save snippet-level results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_snippets, f, indent=4)
    print(f"OCR snippet-level results saved to {output_path}")

    # 2) Save raw results in a separate file
    raw_output_path = output_path.replace(".json", "_raw.json")
    with open(raw_output_path, 'w', encoding='utf-8') as f:
        json.dump(raw_ocr_dict, f, indent=4)
    print(f"Raw OCR results saved to {raw_output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process tiles with MMOCR.")
    parser.add_argument("tiles_dir", help="Path to the directory containing tiled PNGs.")
    parser.add_argument("output_path", help="Path to save the snippet-level OCR results.")
    parser.add_argument("--device", default="cpu", help="Device to run MMOCR on (cpu or cuda).")
    parser.add_argument("--save-vis", action="store_true", help="Enable saving visualizations.")
    args = parser.parse_args()

    try:
        ocr_tiles(
            tiles_dir=args.tiles_dir,
            output_path=args.output_path,
            device=args.device,
            save_vis=args.save_vis
        )
    except Exception as e:
        print(f"Error processing tiles for OCR: {e}")