import os
import json
import pymongo
import sys
from clip_embedding import embed_image  # Assuming this is in the same folder or installed as a module
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    # MongoDB connection
    client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
    db = client["ModeledHomes"]
    collection = db["plan_embeddings"]
    print("MongoDB connection successful!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

def process_tiles(plan_id, output_dir):
    """
    Iterate through the output directory and process all tiles, storing their embeddings in MongoDB.
    
    :param plan_id: Identifier for the plan being processed.
    :param output_dir: Path to the output directory containing tiled images.
    """
    # List all page folders in the output directory
    for page_folder in sorted(os.listdir(output_dir)):
        page_path = os.path.join(output_dir, page_folder)
        
        # Skip non-folder entries
        if not os.path.isdir(page_path):
            print(f"Skipping non-folder: {page_path}")
            continue

        # Extract page number from the folder name (e.g., "page_0")
        try:
            page_number = int(page_folder.split('_')[1])
        except (IndexError, ValueError):
            print(f"Invalid folder name format: {page_folder}")
            continue

        print(f"Processing {plan_id}, Page {page_number}...")

        # Iterate through tiles in the current page folder
        for tile_file in sorted(os.listdir(page_path)):
            tile_path = os.path.join(page_path, tile_file)

            # Skip non-image files
            if not tile_file.endswith(".png"):
                print(f"Skipping non-image file: {tile_file}")
                continue

            print(f"Embedding tile: {tile_path}")
            try:
                # Generate embedding for the tile
                embedding = embed_image(tile_path)

                # Create document for MongoDB
                document = {
                    "planId": plan_id,
                    "pageNumber": page_number + 1,  # Convert to 1-based indexing
                    "tilePath": tile_path,
                    "embedding": embedding,
                    "createdAt": str(datetime.now())
                }

                # Insert into MongoDB
                collection.insert_one(document)

            except Exception as e:
                print(f"Error processing {tile_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python batch_embed_tiles.py <plan_id> <output_dir>")
        sys.exit(1)
    
    PLAN_ID = sys.argv[1]
    OUTPUT_DIR = sys.argv[2]

    process_tiles(PLAN_ID, OUTPUT_DIR)
    print(f"Embeddings successfully stored for planId: {PLAN_ID}")