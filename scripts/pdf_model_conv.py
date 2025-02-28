import os
import sys
import subprocess
import logging
from config import get_user_project_path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

def pdf_model_conv(uuid, plan_id):
    """
    Runs the pipeline:
    1) Accesses the project input directory using uuid and plan_id.
    2) Processes the target PDF.
    3) Saves outputs to data/user/{uuid}/projects/{plan_id}/results/.
    """
    logging.info(f"Starting pipeline for '{plan_id}' under user '{uuid}'...")

    # Step 1: Get PDF upload directory
    user_project_dir = get_user_project_path(uuid, plan_id)

    if not os.path.exists(user_project_dir):
        logging.error(f"🚨 Project input directory does not exist: {user_project_dir}")
        raise FileNotFoundError(f"Project input directory not found: {user_project_dir}")

    # Step 2: Define uploads and results directories at the same level
    uploads_dir = os.path.join(user_project_dir, "uploads")
    results_dir = os.path.join(user_project_dir, "results")

    # Create missing directories
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    logging.info(f"📂 Project Base Directory: {user_project_dir}")
    logging.info(f"📥 Uploads Directory: {uploads_dir}")
    logging.info(f"📊 Results Directory: {results_dir}")

    # Step 3: Get PDF files from uploads directory
    pdf_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(".pdf")]

    if not pdf_files:
        logging.warning(f"⚠️ No PDF files found in: {uploads_dir}")
    else:
        logging.info(f"✅ Found {len(pdf_files)} PDFs in {uploads_dir}: {pdf_files}")

    pdf_path = os.path.join(uploads_dir, pdf_files[0]) if pdf_files else None
    if pdf_path:
        logging.info(f"Using PDF: {pdf_path}")

    # Step 4: Define output paths
    paths = {
        "embedded_text": os.path.join(results_dir, "embedded_text.json"),
        "tile_meta": os.path.join(results_dir, "tile_meta.json"),
        "ocr_results": os.path.join(results_dir, "ocr_results.json"),
        "merged_results": os.path.join(results_dir, "merged_results.json"),
        "categorized_results": os.path.join(results_dir, "categorized_results.json"),
        "line_detection_results": os.path.join(results_dir, "line_detection_results.json"),
        "classified_walls": os.path.join(results_dir, "classified_walls.json"),
        "linked_dimensions": os.path.join(results_dir, "linked_dimensions.json"),
        "final_overlays": os.path.join(results_dir, "final_overlays.json"),
    }

    # Step 5: Run pipeline steps
    try:
        pipeline_steps = [
            ("extract_embedded_text.py", [pdf_path, paths["embedded_text"]]),
            ("pdf_to_tiles.py", [pdf_path, results_dir, "300", "1500"]),
            ("ocr_tiles.py", [results_dir, paths["ocr_results"], paths["tile_meta"], "--save-vis"]),
            ("merge_text.py", [paths["embedded_text"], paths["ocr_results"], paths["tile_meta"], paths["merged_results"]]),
            ("id_area_scale.py", [paths["merged_results"]]),
            ("categorize_text.py", [paths["merged_results"], paths["categorized_results"]]),
            ("line_detection.py", [results_dir, paths["tile_meta"], paths["line_detection_results"]]),
            ("classify_structures.py", [paths["line_detection_results"], paths["classified_walls"]]),
            ("link_dimensions.py", [paths["categorized_results"], paths["line_detection_results"], paths["linked_dimensions"]]),
            ("assemble_overlay.py", [plan_id, results_dir, paths["final_overlays"]]),
            ("batch_embed_overlays.py", [plan_id, results_dir]),
        ]

        for script_name, args in pipeline_steps:
            run_script(script_name, args)

        logging.info(f"✅ Pipeline completed for '{plan_id}'. Results saved in: {results_dir}")

    except Exception as e:
        logging.error(f"❌ Pipeline failed for '{plan_id}': {e}")

def run_script(script_name, args):
    """
    Helper function to execute a script.
    """
    script_path = get_script_path(script_name)
    logging.info(f"▶️ Running {script_name} with args: {args}")
    subprocess.run([sys.executable, script_path] + args, check=True)
    logging.info(f"✅ {script_name} completed successfully.")

def get_script_path(script_name):
    """
    Returns the absolute path to a script.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, script_name)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Script not found: {path}")
    return path

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pdf_model_conv.py <uuid> <plan_id>")
        sys.exit(1)

    uuid_arg = sys.argv[1]
    plan_id_arg = sys.argv[2]

    pdf_model_conv(uuid_arg, plan_id_arg)