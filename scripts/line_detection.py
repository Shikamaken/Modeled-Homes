import os
import sys
import json
import cv2
import numpy as np
import argparse

def tile_coords_to_pdf_bottom_left(px, py, tile_info):
    """
    Converts tile-based pixel coords (px, py) to bottom-left PDF coords.
    tile_info must have:
      - x_start, y_start (top-left offsets in px)
      - zoom_factor
      - pdf_height_points (the page height in PDF points for the y-inversion)
    """
    x_start = tile_info["x_start"]
    y_start = tile_info["y_start"]
    zoom = tile_info["zoom_factor"]
    pdf_height_pts = tile_info["pdf_height_points"]  # from pdf_to_tiles.py

    # Step 1) top-based PDF coords in points
    pdfx_top = (px + x_start) / zoom
    pdfy_top = (py + y_start) / zoom

    # Step 2) invert Y for bottom-left orientation
    pdfy_bottom = pdf_height_pts - pdfy_top

    return (pdfx_top, pdfy_bottom)

def detect_lines_in_image(image_path, tile_info):
    """
    1) Reads the tile image in grayscale,
    2) Applies a bilateral filter to reduce noise while preserving edges,
    3) Runs Canny edge detection,
    4) Applies a morphological close to unify line edges,
    5) Uses HoughLinesP for probabilistic line detection,
    6) Converts the resulting line endpoints from tile pixels to PDF/page coords,
    7) Returns a list of line dicts with 'pdf_line', 'rho', 'theta' (optional).
    
    :param image_path: Path to the tile PNG.
    :param tile_info: Dict from tile_meta (x_start, y_start, zoom_factor, etc.).
    :return: List of line entries with page-based coords.
    """
    # --- 1) Load grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Failed to load image: {image_path}")

    # --- 2) Bilateral filter to smooth out minor text noise
    #     d=9, sigmaColor=75, sigmaSpace=75 are typical defaults
    filtered = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)

    # --- 3) Canny
    edges = cv2.Canny(filtered, 50, 150, apertureSize=3)

    # --- 4) Morphological close to connect line segments
    kernel = np.ones((3, 3), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)

    # --- 5) Probabilistic Hough transform
    # tune threshold, minLineLength, maxLineGap as needed
    lines_p = cv2.HoughLinesP(
        closed, 
        rho=1, 
        theta=np.pi / 180, 
        threshold=80,        # min votes in accumulator
        minLineLength=50,    # discard short segments
        maxLineGap=10        # merge gaps in collinear lines
    )

    # We'll store each line in PDF coords
    lines_list = []
    if lines_p is not None:
        for line in lines_p:
            x1, y1, x2, y2 = line[0]
            pdf_pt1 = tile_coords_to_pdf_bottom_left(x1, y1, tile_info)
            pdf_pt2 = tile_coords_to_pdf_bottom_left(x2, y2, tile_info)
            lines_list.append({
                "pdf_line": [pdf_pt1, pdf_pt2]
            })

    return lines_list

def process_line_detection(input_dir, tile_meta_path, output_path):
    """
    1) Loads tile_meta.json to get x_start, y_start, zoom_factor for each tile,
    2) For each .png tile, runs detect_lines_in_image(...),
    3) Writes final lines in PDF/page coords to line_detection_results.json.
    
    :param input_dir: Directory containing page_<idx>/tile_*.png
    :param tile_meta_path: Path to tile_meta.json
    :param output_path: JSON file for storing line detection results.
    """
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"Input directory not found: {input_dir}")

    if not os.path.isfile(tile_meta_path):
        raise FileNotFoundError(f"Tile metadata file not found: {tile_meta_path}")

    with open(tile_meta_path, 'r', encoding='utf-8') as f:
        tile_metadata = json.load(f)

    # Build a quick lookup: tile_info_map[(page_idx, tile_filename)] = tile_entry
    tile_info_map = {}
    for meta in tile_metadata:
        page_idx = meta["page_index"]
        tile_fn = meta.get("tile_filename", "")
        tile_key = (page_idx, tile_fn)
        tile_info_map[tile_key] = meta

    results = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(".png"):
                image_path = os.path.join(root, file)

                # find matching tile_meta
                tile_filename = os.path.basename(image_path)
                # Guess page index from folder or rely on tile_info_map if you have a direct approach
                # For now let's do a naive approach:
                possible_keys = [k for k in tile_info_map.keys() if k[1] == tile_filename]
                if not possible_keys:
                    print(f"Metadata not found for tile: {tile_filename}. Skipping.")
                    continue

                # If there's only one match or you trust there's only one
                page_idx, _ = possible_keys[0]
                tile_info = tile_info_map[(page_idx, tile_filename)]

                try:
                    line_segments = detect_lines_in_image(image_path, tile_info)

                    # Add them to results
                    for seg in line_segments:
                        results.append({
                            "page_index": page_idx,
                            "image_path": image_path,
                            "pdf_line": seg["pdf_line"]
                        })
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)

    print(f"Line detection results saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect lines in tile images, returning PDF coords.")
    parser.add_argument("input_dir", help="Directory containing page_<idx>/tile_*.png")
    parser.add_argument("tile_meta_path", help="Path to tile_meta.json with x_start,y_start,zoom_factor.")
    parser.add_argument("output_path", help="Path to save final line_detection_results.json.")
    args = parser.parse_args()

    try:
        process_line_detection(args.input_dir, args.tile_meta_path, args.output_path)
    except Exception as e:
        print(f"Error during line detection: {e}")
        sys.exit(1)