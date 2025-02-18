import os
import sys
import subprocess
import logging
from config import DATA_INPUT, DATA_OUTPUT

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

def pdf_model_conv():
    """
    Orchestrates the entire pipeline:
    1) For each PDF in DATA_INPUT, generate a unique plan_id
    2) Create an output directory
    3) Sequentially run pipeline steps, calling appropriate scripts
    """
    logging.info("Starting PDF Model Conversion Pipeline...")

    # Step 1: List PDFs in DATA_INPUT
    pdf_files = [f for f in os.listdir(DATA_INPUT) if f.lower().endswith(".pdf")]
    if not pdf_files:
        logging.warning("No PDF files found in the input directory.")
        return

    for filename in pdf_files:
        pdf_path = os.path.join(DATA_INPUT, filename)
        plan_id = os.path.splitext(filename)[0]  # Plan identifier (e.g., "building_plan")
        
        # Step 2: Create output directory for the plan
        plan_dir = os.path.join(DATA_OUTPUT, "results", plan_id)
        os.makedirs(plan_dir, exist_ok=True)
        logging.info(f"Processing '{plan_id}' with output directory: {plan_dir}")

        # Define intermediate output file paths
        paths = {
            "embedded_text": os.path.join(plan_dir, "embedded_text.json"),
            "tile_meta": os.path.join(plan_dir, "tile_meta.json"),
            "ocr_results": os.path.join(plan_dir, "ocr_results.json"),
            "merged_results": os.path.join(plan_dir, "merged_results.json"),
            "categorized_results": os.path.join(plan_dir, "categorized_results.json"),
            "line_detection_results": os.path.join(plan_dir, "line_detection_results.json"),
            "classified_walls": os.path.join(plan_dir, "classified_walls.json"),
            "linked_dimensions": os.path.join(plan_dir, "linked_dimensions.json"),
            "final_overlays": os.path.join(plan_dir, "final_overlays.json"),
        }

        # Step 3: Run pipeline steps sequentially
        try:
            # Extract embedded text
            run_script("extract_embedded_text.py", [pdf_path, paths["embedded_text"]])

            # Convert PDF to tiles
            run_script("pdf_to_tiles.py", [pdf_path, plan_dir, "300", "1500"])

            # Perform OCR on tiles
            run_script("ocr_tiles.py", [
                plan_dir, 
                paths["ocr_results"], 
                paths["tile_meta"],
                "--save-vis"
            ])

            # Merge text (embedded + OCR)
            run_script("merge_text.py", [
                paths["embedded_text"],
                paths["ocr_results"],
                paths["tile_meta"],
                paths["merged_results"]
            ])

            # ID floor plan, surface area, and scale
            run_script("id_area_scale.py", [
                paths["merged_results"]
            ])

            # Categorize merged text
            run_script("categorize_text.py", [
                paths["merged_results"],
                paths["categorized_results"]
            ])

            # Detect lines in tiles
            run_script("line_detection.py", [
                plan_dir,
                paths["tile_meta"],
                paths["line_detection_results"]
            ])

            # Classify detected lines into structures (walls, partitions, etc.)
            run_script("classify_structures.py", [
                paths["line_detection_results"],
                paths["classified_walls"]
            ])

            # Link dimensions to detected lines
            run_script("link_dimensions.py", [
                paths["categorized_results"],
                paths["line_detection_results"],
                paths["linked_dimensions"]
            ])

            # Prepare overlays
            run_script("assemble_overlay.py", [
                plan_id, 
                plan_dir,
                paths["final_overlays"]
            ])

            # Embed overlays
            run_script("batch_embed_overlays.py", [plan_id, plan_dir])

            logging.info(f"Pipeline successfully completed for '{plan_id}'.")

        except Exception as e:
            logging.error(f"Pipeline failed for '{plan_id}': {e}")

def run_script(script_name, args):
    """
    Helper function to execute a script with subprocess.run().
    """
    script_path = get_script_path(script_name)
    logging.info(f"Running {script_name} with args: {args}")
    subprocess.run([sys.executable, script_path] + args, check=True)
    logging.info(f"{script_name} completed successfully.")

def get_script_path(script_name):
    """
    Resolves the full path to a script.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, script_name)
    if not os.path.isfile(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
    return script_path

if __name__ == "__main__":
    pdf_model_conv()