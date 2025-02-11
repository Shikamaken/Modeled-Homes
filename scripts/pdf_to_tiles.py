import os
import sys
import fitz  # PyMuPDF
import json
from tqdm import tqdm
from PIL import Image

def convert_pdf_to_tiles(pdf_path, output_dir, plan_id=None,
                         dpi=300, tile_size=1500,
                         overlap_px=150,
                         skip_blank_tiles=True, blank_threshold=0.99):
    """
    Converts a PDF into high-resolution tiled PNG images and writes metadata.
    
    :param pdf_path: Path to the input PDF file.
    :param output_dir: Directory to store the output tile images + metadata.
    :param plan_id: (Optional) A string ID that identifies this plan/document.
    :param dpi: Desired rendering resolution in DPI (default 300).
    :param tile_size: Width/height of each tile in pixels (default 1500).
    :param skip_blank_tiles: If True, skip saving tiles that appear mostly blank.
    :param blank_threshold: A float (0.0~1.0) indicating how "white" a tile must be
                            to consider it blank. 0.97 means 97%+ white => skip.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    os.makedirs(output_dir, exist_ok=True)
    zoom_factor = dpi / 72.0
    pdf_doc = fitz.open(pdf_path)
    total_pages = len(pdf_doc)
    print(f"Converting {pdf_path} ({total_pages} pages) at {dpi} DPI...")

    tile_metadata = []
    global_tile_index = 0

    for page_index in tqdm(range(total_pages), desc="Pages", unit="page"):
        page = pdf_doc[page_index]
        page_dir = os.path.join(output_dir, f"page_{page_index}")
        os.makedirs(page_dir, exist_ok=True)

        # Rendered page size in pixels
        page_width = int(page.rect.width * zoom_factor)
        page_height = int(page.rect.height * zoom_factor)

        # Page size in PDF coordinate space
        pdf_width_points = page.rect.width
        pdf_height_points = page.rect.height

        num_tiles_x = (page_width + tile_size - 1) // tile_size
        num_tiles_y = (page_height + tile_size - 1) // tile_size

        step_y = tile_size - overlap_px  # e.g. tile_size=1500, overlap_px=150 => step_y=1350
        step_x = tile_size - overlap_px

        for y_start in range(0, page_height, step_y):
            for x_start in range(0, page_width, step_x):
                x_end = min(x_start + tile_size, page_width)
                y_end = min(y_start + tile_size, page_height)

                tile_rect = fitz.Rect(
                    x_start / zoom_factor,
                    y_start / zoom_factor,
                    x_end   / zoom_factor,
                    y_end   / zoom_factor
                )

                tile_pix = page.get_pixmap(
                    matrix=fitz.Matrix(zoom_factor, zoom_factor),
                    clip=tile_rect
                )

                tile_filename = f"tile_{x_start}_{y_start}.png"
                tile_path = os.path.join(page_dir, tile_filename)

                # --------------------------------------------------
                # Skip blank tiles
                # --------------------------------------------------
                if skip_blank_tiles:
                    # Convert the pixmap to PIL Image in memory to check "whiteness"
                    pil_img = Image.frombytes(
                        "RGB",
                        [tile_pix.width, tile_pix.height],
                        tile_pix.samples
                    )
                    # Quick grayscale conversion or direct stats
                    # Count how many pixels are near-white
                    # We'll do a naive approach: average brightness
                    grayscale = pil_img.convert("L")
                    hist = grayscale.histogram()
                    # normalized brightness
                    total_pixels = tile_pix.width * tile_pix.height
                    # approximate "white" as brightness >= 250 (for example)
                    # or do an average measure
                    brightness_sum = sum(i * hist[i] for i in range(256))
                    avg_brightness = brightness_sum / float(total_pixels)
                    
                    # if average brightness is above a threshold => skip
                    # 255 = fully white
                    if (avg_brightness / 255.0) > blank_threshold:
                        # tile is "mostly blank"
                        continue

                # --------------------------------------------------
                # Save the tile
                # --------------------------------------------------
                try:
                    tile_pix.save(tile_path)
                except Exception as e:
                    print(f"Error saving tile {tile_path}: {e}")
                    continue

                # --------------------------------------------------
                # Store tile metadata
                # --------------------------------------------------
                meta_entry = {
                    "plan_id": plan_id if plan_id else None,  # optional
                    "page_index": page_index,
                    "tile_index": global_tile_index,
                    "x_start": x_start,
                    "y_start": y_start,
                    "tile_width": x_end - x_start,
                    "tile_height": y_end - y_start,
                    "zoom_factor": zoom_factor,
                    "tile_filename": tile_filename,
                    "page_width": page_width,    # store full page size in px
                    "page_height": page_height,
                    "pdf_width_points": page.rect.width,
                    "pdf_height_points": page.rect.height,
                }
                tile_metadata.append(meta_entry)
                global_tile_index += 1

    pdf_doc.close()

    # Write tile_meta.json
    meta_path = os.path.join(output_dir, "tile_meta.json")
    with open(meta_path, 'w', encoding='utf-8') as mf:
        json.dump(tile_metadata, mf, indent=2)
    print(f"Tile metadata saved to {meta_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pdf_to_tiles.py <input_pdf_path> <output_dir> [plan_id] [dpi] [tile_size]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    plan_id = None
    if len(sys.argv) > 3:
        plan_id = sys.argv[3] if not sys.argv[3].isdigit() else None
    # parse optional dpi, tile_size if present
    dpi = 300
    tile_size = 1500

    # if arguments after plan_id are numeric, treat them as dpi/tile_size
    numeric_args = [arg for arg in sys.argv[3:] if arg.isdigit()]
    if len(numeric_args) >= 1:
        dpi = int(numeric_args[0])
    if len(numeric_args) >= 2:
        tile_size = int(numeric_args[1])

    try:
        convert_pdf_to_tiles(pdf_path, output_dir, plan_id=plan_id,
                             dpi=dpi, tile_size=tile_size)
    except Exception as e:
        print(f"Error converting PDF to tiles: {e}")