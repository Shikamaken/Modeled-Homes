import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_script_path(script_name):
    """
    Resolves the path to a script, prioritizing relative paths but falling back to absolute paths.
    
    :param script_name: The name of the script to locate (e.g., "pdf_to_tiles.py").
    :return: The resolved path to the script.
    """
    relative_path = os.path.join(os.path.dirname(__file__), script_name)
    if os.path.exists(relative_path):
        return relative_path
    # Fallback to absolute path (adjust as needed for your setup)
    absolute_path = os.path.abspath(f"../pdf_tiling_pipeline/{script_name}")
    if os.path.exists(absolute_path):
        return absolute_path
    raise FileNotFoundError(f"Script {script_name} not found in expected locations.")

def process_pdf_to_embeddings(pdf_path, output_dir, plan_id, dpi=300, tile_size=3000):
    """
    Automates the workflow: Convert PDF to tiles and embed tiles.
    
    :param pdf_path: Path to the input PDF file.
    :param output_dir: Directory for output tiles.
    :param plan_id: Identifier for the plan being processed.
    :param dpi: Rendering DPI for tiling.
    :param tile_size: Tile size in pixels.
    """
    try:
        pdf_to_tiles_path = get_script_path("pdf_to_tiles.py")
        batch_embed_tiles_path = get_script_path("batch_embed_tiles.py")
    except FileNotFoundError as e:
        print(e)
        return

    # Step 1: Run pdf_to_tiles.py
    print(f"Running pdf_to_tiles.py for {pdf_path}...")
    try:
        subprocess.run(
            [
                sys.executable,
                pdf_to_tiles_path,
                pdf_path,
                output_dir,
                str(dpi),
                str(tile_size)
            ],
            check=True
        )
        print("Tiling completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during tiling: {e}")
        return

    # Step 2: Run batch_embed_tiles.py
    print(f"Running batch_embed_tiles.py for {output_dir}...")
    try:
        subprocess.run(
            [
                sys.executable,
                batch_embed_tiles_path,
                plan_id,
                output_dir
            ],
            check=True
        )
        print("Embedding completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during embedding: {e}")
        return

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python process_pdf.py <path_to_pdf> <output_dir> <plan_id> [dpi] [tile_size]")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_folder = sys.argv[2]
    plan_id = sys.argv[3]
    dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    tile_size = int(sys.argv[5]) if len(sys.argv) > 5 else 3000

    process_pdf_to_embeddings(pdf_file, output_folder, plan_id, dpi, tile_size)