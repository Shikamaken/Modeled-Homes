import os
import sys
import json
import pymongo
from datetime import datetime
from clip_embedding import embed_image, embed_text
from dotenv import load_dotenv
import logging
import requests

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Force UTF-8 encoding for stdout (Windows fix)
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

try:
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        raise ValueError("MONGODB_URI not defined in the environment.")
    client = pymongo.MongoClient(mongodb_uri)
    db = client["ModeledHomes"]
    collection = db["plan_overlays"]
    logging.info("MongoDB connection successful!")
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    sys.exit(1)


def process_overlays(plan_id, plan_dir):
    """
    Reads final_overlays.json from plan_dir, embeds images & text (optional),
    and stores them in MongoDB as a single doc per tile.
    """
    logging.info(f"Processing final overlays for Plan ID: {plan_id}")

    final_overlays_path = os.path.join(plan_dir, "final_overlays.json")
    if not os.path.isfile(final_overlays_path):
        logging.error(f"final_overlays.json not found in {plan_dir}")
        return

    # Load final overlays
    with open(final_overlays_path, "r", encoding="utf-8") as f:
        final_overlays = json.load(f)

    # We can track processed_images if we suspect multiple references
    processed_images = set()

    for tile_obj in final_overlays:
        image_path = tile_obj.get("imagePath")
        overlay_data = tile_obj.get("overlayData", {})
        is_blank = overlay_data.get("isBlank", True)

        # 1) Skip if tile is marked as blank
        if is_blank:
            logging.info(f"Skipping blank tile: {image_path}")
            continue

        # 2) Embed the tile image if not done already
        image_embedding = None
        if image_path and image_path not in processed_images:
            try:
                image_embedding = embed_image(image_path)
                processed_images.add(image_path)
            except Exception as e:
                logging.error(f"Error embedding image {image_path}: {e}")

        # 3) TEXT EMBEDDING (aggregated)
        text_blocks = overlay_data.get("textBlocks", [])
        combined_text = " ".join([tb["text"] for tb in text_blocks]).strip()

        if combined_text:
            try:
                text_embedding = embed_text(combined_text)  # from clip_embedding.py
            except Exception as e:
                logging.error(f"Error embedding text for tile {image_path}: {e}")
                text_embedding = None
        else:
            text_embedding = None

        # 4) Prepare MongoDB document
        doc = {
            "planId": tile_obj.get("planId", plan_id),
            "pageIndex": tile_obj.get("pageIndex"),
            "tileIndex": tile_obj.get("tileIndex"),
            "imagePath": image_path,
            "pdfCoords": tile_obj.get("pdfCoords", {}),
            "overlayData": overlay_data,
            "imageEmbedding": image_embedding,
            "textEmbedding": text_embedding,
            "createdAt": datetime.now().isoformat()
        }

        # Insert into MongoDB
        collection.insert_one(doc)
        logging.info(f"Inserted tile doc for {image_path} (blank={is_blank}).")


def get_uuid_from_path(plan_dir):
    """
    Extracts the UUID from the plan directory path.
    Expected structure: data/user/{uuid}/projects/{plan_id}/results/
    """
    parts = os.path.normpath(plan_dir).split(os.sep)
    try:
        uuid_index = parts.index("user") + 1
        return parts[uuid_index]  # ✅ Extracts the UUID correctly
    except (ValueError, IndexError):
        logging.error(f"❌ Could not extract UUID from path: {plan_dir}")
        return None


def notify_pipeline_complete(uuid, plan_id):
    """
    Sends a request to notify the backend that the pipeline has completed.
    """
    backend_url = "http://localhost:4000/api/pipeline/complete"
    payload = {"uuid": uuid, "plan_id": plan_id}

    try:
        response = requests.post(backend_url, json=payload)
        if response.status_code == 200:
            print(f"✅ Successfully notified backend: {response.json()}")
        else:
            print(f"❌ Backend notification failed: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error notifying backend: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python batch_embed_overlays.py <plan_id> <plan_dir>")
        sys.exit(1)

    plan_id = sys.argv[1]
    plan_dir = os.path.normpath(sys.argv[2])
    uuid = get_uuid_from_path(plan_dir)

    if uuid:
        try:
            process_overlays(plan_id, plan_dir)
            logging.info(f"Embeddings stored successfully for Plan ID: {plan_id}")

            notify_pipeline_complete(uuid, plan_id)

        except Exception as e:
            logging.error(f"Error processing overlays: {e}")
    else:
        logging.error(f"🚨 Pipeline completed, but UUID extraction failed. Backend will not be notified.")