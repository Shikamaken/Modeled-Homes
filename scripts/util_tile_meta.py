# util_tile_meta.py
import json
import os

def load_tile_meta_map(tile_meta_path):
    """
    Loads tile_meta.json (a list of dicts) into a dictionary keyed by (page_idx, x_start, y_start).
    """
    if not os.path.isfile(tile_meta_path):
        raise FileNotFoundError(f"Tile metadata file not found: {tile_meta_path}")

    with open(tile_meta_path, "r", encoding="utf-8") as f:
        tile_meta_list = json.load(f)

    tile_meta_map = {}
    for meta in tile_meta_list:
        page_idx = meta["page_index"]
        x_start = meta["x_start"]
        y_start = meta["y_start"]
        # Build a key
        tile_key = (page_idx, x_start, y_start)

        tile_meta_map[tile_key] = meta

    return tile_meta_map

def tile_coords_to_pdf_bottom_left(xmin, ymin, xmax, ymax, tile_info):
    """
    Converts tile-based bounding box to bottom-left PDF coords.
    tile_info must have:
      - x_start, y_start, zoom_factor
      - pdf_height_points (the page height in points from pdf_to_tiles.py)
    """
    x_start_px = tile_info["x_start"]
    y_start_px = tile_info["y_start"]
    zoom = tile_info["zoom_factor"]

    pdf_height_pts = tile_info["pdf_height_points"]  # newly added in pdf_to_tiles

    # 1) Convert from tile px -> "top-based PDF coords" in points
    pdfx_min_top = (xmin + x_start_px) / zoom
    pdfx_max_top = (xmax + x_start_px) / zoom
    pdfy_min_top = (ymin + y_start_px) / zoom
    pdfy_max_top = (ymax + y_start_px) / zoom

    # 2) Invert y for bottom-left
    pdfy_min_bottom = pdf_height_pts - pdfy_max_top
    pdfy_max_bottom = pdf_height_pts - pdfy_min_top

    return [pdfx_min_top, pdfy_min_bottom, pdfx_max_top, pdfy_max_bottom]
