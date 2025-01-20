import os
import sys
import subprocess
import logging
from config import DATA_OUTPUT

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

def test_from_merge(plan_id):
    """
    Resumes the pipeline starting from merge_text.py and runs through completion.
    
    :param plan_id: The identifier for the plan being processed.
    """
    logging.info(f"Resuming pipeline for '{plan_id}' from merge_text.py...")

    # Define output directory for the plan
    plan_dir = os.path.join(DATA_OUTPUT, "results", plan_id)
    if not os.path.isdir(plan_dir):
        logging.error(f"Plan directory not found: {plan_dir}")
        return

    # Define intermediate file paths
    paths = {
        "embedded_text": os.path.abspath(os.path.join(plan_dir, "embedded_text.json")),
        "tile_meta": os.path.abspath(os.path.join(plan_dir, "tile_meta.json")),
        "ocr_results": os.path.abspath(os.path.join(plan_dir, "ocr_results.json")),
        "merged_results": os.path.abspath(os.path.join(plan_dir, "merged_results.json")),
        "categorized_results": os.path.abspath(os.path.join(plan_dir, "categorized_results.json")),
        "line_detection_results": os.path.abspath(os.path.join(plan_dir, "line_detection_results.json")),
        "linked_dimensions": os.path.abspath(os.path.join(plan_dir, "linked_dimensions.json")),
        "final_overlays": os.path.abspath(os.path.join(plan_dir, "final_overlays.json")),
    }

    try:
        # Step 1: Resume pipeline from merge_text.py
        run_script("merge_text.py", [
            paths["embedded_text"],
            paths["ocr_results"],
            paths["tile_meta"],
            paths["merged_results"]
        ])

        # Step 2: Categorize merged text
        run_script("categorize_text.py", [
            paths["merged_results"],
            paths["categorized_results"]
        ])

        # Step 3: Detect lines in tiles
        run_script("line_detection.py", [
            plan_dir,  # input_dir
            paths["line_detection_results"]  # output_path
        ])

        # Step 4: Link dimensions to detected lines
        run_script("link_dimensions.py", [
            paths["categorized_results"],
            paths["line_detection_results"],
            paths["linked_dimensions"]
        ])

        # Step 5: Prepare overlays
        run_script("assemble_overlay.py", [
            plan_id, 
            plan_dir,
            paths["final_overlays"]
        ])

        # Step 6: Embed overlays
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
    if len(sys.argv) < 2:
        print("Usage: python test_from_merge.py <plan_id>")
        sys.exit(1)

    plan_id = sys.argv[1]
    test_from_merge(plan_id)