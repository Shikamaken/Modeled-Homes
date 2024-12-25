import os
import sys
import fitz  # PyMuPDF
from tqdm import tqdm

def convert_pdf_to_tiles(pdf_path, output_dir, dpi=300, tile_size=3000):
    """
    Converts a PDF into high-resolution tiled PNG images.
    
    :param pdf_path: Path to the input PDF file.
    :param output_dir: Directory to store the output tile images.
    :param dpi: Desired rendering resolution in DPI.
    :param tile_size: Width/height of each tile in pixels.
    """
    # Check that PDF exists
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # PyMuPDF uses a 'zoom' factor relative to 72 DPI. 
    zoom_factor = dpi / 72.0
    
    # Open the PDF
    pdf_doc = fitz.open(pdf_path)
    
    total_pages = len(pdf_doc)
    print(f"Converting {pdf_path} with {total_pages} pages at {dpi} DPI...")
    
    # Progress bar for pages
    for page_index in tqdm(range(total_pages), desc="Pages", unit="page"):
        page = pdf_doc[page_index]
        
        # Create directory for this page's tiles
        page_dir = os.path.join(output_dir, f"page_{page_index}")
        if not os.path.exists(page_dir):
            os.makedirs(page_dir)
        
        page_width = int(page.rect.width * zoom_factor)
        page_height = int(page.rect.height * zoom_factor)
        
        # Nested loop for tiling
        num_tiles_x = (page_width + tile_size - 1) // tile_size
        num_tiles_y = (page_height + tile_size - 1) // tile_size
        
        tile_iter = tqdm(total=num_tiles_x * num_tiles_y, desc=f"Page {page_index} Tiles", leave=False, unit="tile")
        
        for y_start in range(0, page_height, tile_size):
            for x_start in range(0, page_width, tile_size):
                x_end = min(x_start + tile_size, page_width)
                y_end = min(y_start + tile_size, page_height)
                
                tile_rect = fitz.Rect(
                    x_start / zoom_factor, y_start / zoom_factor,
                    x_end / zoom_factor, y_end / zoom_factor
                )
                
                tile_pix = page.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor), clip=tile_rect)
                
                tile_filename = f"tile_{x_start}_{y_start}.png"
                tile_path = os.path.join(page_dir, tile_filename)
                
                try:
                    tile_pix.save(tile_path)
                except Exception as e:
                    print(f"Error saving tile: {tile_path}. Error: {e}")
                
                tile_iter.update(1)
        
        tile_iter.close()
    
    pdf_doc.close()
    print("PDF conversion complete!")

if __name__ == "__main__":
    # Example usage via CLI:
    # python pdf_to_tiles.py MyBlueprint.pdf output_folder
    if len(sys.argv) < 3:
        print("Usage: python pdf_to_tiles.py <path_to_pdf> <output_dir> [dpi] [tile_size]")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_folder = sys.argv[2]
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    tile_size = int(sys.argv[4]) if len(sys.argv) > 4 else 3000
    
    convert_pdf_to_tiles(pdf_file, output_folder, dpi=dpi, tile_size=tile_size)